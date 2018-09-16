from collections import namedtuple, OrderedDict

from aenum import Enum
import inspect

from mock import MagicMock

MockingFramework = Enum('MockingFramework', 'PYTEST_MOCK')
CallParameters = namedtuple('CallParameters', 'args, kwargs')


def generate_mocks(mocking_framework, mocked_module, mock_modules=True,
                   mock_functions=False, mock_builtin=True,
                   mock_classes=False, mock_referenced_classes=True,
                   mock_classes_static=False):
    """
    Generates the list of mocks in order to mock the dependant modules and the
    functions of the given module.

    Note that the returned code is the initial basic code on which you can add
    your custom logic like function return values.

    Args:
        mocking_framework (MockingFramework): the type of the mocking
            framework to use
        mocked_module (types.ModuleType): the module to mock
        mock_modules (bool): whether to mock dependant modules which are
            referenced from the mocked module
        mock_functions (bool): whether to mock functions defined in the module
        mock_builtin (bool): whether to mock builtin functions defined in the
            module
        mock_classes (bool): whether to mock classes defined in the module
        mock_referenced_classes (bool): whether to mock classes referenced in
            the module but defined elsewhere
        mock_classes_static (bool): whether to mock the static functions of the
            mocked classes. This is important if the tested code uses
            isinstance of accesses class functions directly. Used only if
            mock_classes or mock_referenced_classes is `True`


    Returns:
        str: the code to put in your test to mock the desired behaviour.
    """
    modules = []
    if mock_modules:
        modules.extend(sorted([t[0] for t in
                               inspect.getmembers(mocked_module,
                                                  inspect.ismodule)]))
    functions = []
    if mock_functions:
        functions.extend(sorted([t[0] for t in
                                 inspect.getmembers(mocked_module,
                                                    inspect.isfunction)]))
    if mock_builtin:
        functions.extend(sorted([t[0] for t in
                                 inspect.getmembers(
                                     mocked_module, inspect.isbuiltin)]))

    classes = []
    if mock_classes:
        classes.extend(sorted([t[0] for t in
                               inspect.getmembers(mocked_module,
                                                  inspect.isclass) if
                               t[1].__module__ == mocked_module.__name__]))
    if mock_referenced_classes:
        classes.extend(sorted([t[0] for t in
                               inspect.getmembers(mocked_module,
                                                  inspect.isclass) if not
                               t[1].__module__ == mocked_module.__name__]))

    if MockingFramework.PYTEST_MOCK == mocking_framework:
        return _pytest_mock_generate(mocked_module.__name__, modules,
                                     functions,
                                     classes, mock_classes_static)
    else:
        raise ValueError("Unsupported mocking framework: {0}. "
                         "You are welcome to add code to support it :)".
                         format(mocking_framework))


def _pytest_mock_generate(mocked_module_name, modules, functions, classes,
                          mock_classes_static):
    generated = ""
    if modules:
        generated += "# mocked modules\n"
        for module in modules:
            generated += _single_pytest_mock_entry(mocked_module_name, module)
    if functions:
        generated += "# mocked functions\n"
        for func in functions:
            generated += _single_pytest_mock_entry(mocked_module_name, func)
    if classes:
        generated += "# mocked classes\n"
        for cls in classes:
            generated += _mock_class_static(cls, mocked_module_name) if \
                mock_classes_static else \
                _single_pytest_mock_entry_with_spec(
                    mocked_module_name,
                    cls,
                    mocked_module_name + "." + cls)

    return generated


def _single_pytest_mock_entry(mocked_module_name, entry):
    return ("mock_{0} = mocker.MagicMock(name='{0}')\n"
            "mocker.patch('{1}.{0}', new=mock_{0})\n"). \
        format(entry, mocked_module_name)


def _single_pytest_mock_entry_with_spec(mocked_module_name, entry, spec):
    return ("mock_{0} = mocker.MagicMock(name='{0}', spec={2})\n"
            "mocker.patch('{1}.{0}', new=mock_{0})\n"). \
        format(entry, mocked_module_name, spec)


def _mock_class_static(class_name, mocked_module_name):
    return ("""
class Mocked{0}Meta(type):
    static_instance = mocker.MagicMock(spec={1}.{0})

    def __getattr__(cls, key):
        return Mocked{0}Meta.static_instance.__getattr__(key)

class Mocked{0}(object):
    __metaclass__ = Mocked{0}Meta
    original_cls = {1}.{0}
    instances = []

    def __new__(cls, *args, **kwargs):
        Mocked{0}.instances.append(mocker.MagicMock(spec=Mocked{0}.original_cls))
        Mocked{0}.instances[-1].__class__ = Mocked{0}
        return Mocked{0}.instances[-1]

mocker.patch('{1}.{0}', new=Mocked{0})
""").format(class_name, mocked_module_name)


def generate_call_list(mock_object, mock_name='mocked'):
    if not isinstance(mock_object, MagicMock):
        raise TypeError("Unsupported mocking object: {0}. "
                        "You are welcome to add code to support it :)".
                        format(type(mock_object)))

    generated_asserts = ""
    if mock_object.call_args_list:
        generated_asserts += "assert {0} == {1}.call_count\n".format(
            len(mock_object.call_args_list), mock_name)

    call_dictionary = OrderedDict()

    for all_calls in mock_object.mock_calls:
        method, args, kwargs = all_calls
        method = method.replace("()", ".return_value")
        if method and not method.startswith("."):
            method = "." + method
        if method not in call_dictionary:
            call_dictionary[method] = []
        call_dictionary[method].append(CallParameters(args, kwargs))

    had_multiple_calls_for_single_method = False
    for func_path, call_list in call_dictionary.iteritems():
        if 1 == len(call_list):
            args, kwargs = call_list[0]
            generated_asserts += "{0}.assert_called_once_with({1})\n".format(
                mock_name + func_path, _param_string(args, kwargs))
        else:
            had_multiple_calls_for_single_method = True
            generated_asserts += "{0}.assert_has_calls(calls=[".format(
                mock_name + func_path)
            for call in call_list:
                args, kwargs = call
                generated_asserts += "call({0}),".format(
                    _param_string(args, kwargs))
            generated_asserts += "])\n"

    if had_multiple_calls_for_single_method:
        generated_asserts = "from mock import call\n\n" + generated_asserts

    return generated_asserts


def _param_string(args, kwargs):
    params = ""
    if args:
        params += ', '.join(['{!r}'.format(v) for v in args])
    if kwargs:
        if params:
            params += ', '
        params += ', '.join(
            ['{}={!r}'.format(k, v) for k, v in sorted(kwargs.iteritems())])
    return params
