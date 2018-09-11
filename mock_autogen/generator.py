from collections import namedtuple, OrderedDict

from aenum import Enum
import inspect

from mock import MagicMock

MockingFramework = Enum('MockingFramework', 'PYTEST_MOCK')
CallParameters = namedtuple('CallParameters', 'args, kwargs')


def generate_mocks(mocking_framework, mocked_module, mock_modules=True,
                   mock_functions=False, mock_builtin=True):
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

    if MockingFramework.PYTEST_MOCK == mocking_framework:
        return _pytest_mock_generate(mocked_module, modules, functions)
    else:
        raise ValueError("Unsupported mocking framework: {0}. "
                         "You are welcome to add code to support it :)".
                         format(mocking_framework))


def _pytest_mock_generate(mocked_module, modules, functions):
    generated = ""
    if modules:
        generated += "# mocked modules\n"
        for module in modules:
            generated += _single_pytest_mock_entry(mocked_module, module)
    if functions:
        generated += "# mocked functions\n"
        for func in functions:
            generated += _single_pytest_mock_entry(mocked_module, func)

    return generated


def _single_pytest_mock_entry(mocked_module, entry):
    return ("mock_{0} = mocker.MagicMock(name='{0}')\n" + \
            "mocker.patch('{1}.{0}', new=mock_{0})\n"). \
        format(entry, mocked_module.__name__)


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
        if method:
            method = "." + method
        method = method.replace("()", ".return_value")
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
