import re
import types
from collections import namedtuple, OrderedDict

from enum import Enum
import inspect

import mock as python_mock
import unittest.mock

MockingFramework = Enum('MockingFramework', 'PYTEST_MOCK')
CallParameters = namedtuple('CallParameters', 'args, kwargs')


def generate_mocks(framework,
                   mocked,
                   name='',
                   mock_modules=True,
                   mock_functions=False,
                   mock_builtin=True,
                   mock_classes=False,
                   mock_referenced_classes=True,
                   mock_classes_static=False):
    """
    Generates the list of mocks in order to mock the dependant modules and the
    functions of a given module, class or object instance.

    Note that the returned code is the initial basic code on which you can add
    your custom logic like function return values.

    Args:
        framework (MockingFramework): the type of the mocking
            framework to use
        mocked (object): the object to mock, might be
            `types.ModuleType`, a class or just a plain object instance
        name (str): the name of the mocked object, to be put in the
            generated code. If the name is not provided, the following logic
            would be used to determine its name: for modules - the name of the
            module. For anything else, would be guessed to match the argument
            name sent to the method and finally defaulted to 'arg'
        mock_modules (bool): whether to mock dependant modules which are
            referenced from the mocked object. Relevant only if `mocked`
            is `types.ModuleType`
        mock_functions (bool): whether to mock functions / methods defined in
            the mocked object
        mock_builtin (bool): whether to mock builtin functions defined in the
            module. Relevant only if `mocked` is `types.ModuleType`
        mock_classes (bool): whether to mock classes defined in the module.
            Relevant only if `mocked` is `types.ModuleType`
        mock_referenced_classes (bool): whether to mock classes referenced in
            the module but defined elsewhere. Relevant only if `mocked`
            is `types.ModuleType`
        mock_classes_static (bool): whether to mock the static functions of the
            mocked classes. Relevant only if `mocked` is
            `types.ModuleType`. This is important if the tested code uses
            isinstance of accessed class functions directly. Used only if
            mock_classes or mock_referenced_classes is `True`

    Returns:
        str: the initial code to put in your test to mock the desired behaviour
    """
    modules = []
    functions = []
    classes = []
    methods = []
    if not isinstance(mocked, types.ModuleType):
        name = name if name else _guess_var_name(name)
        if mock_functions:
            methods.extend(
                sorted([
                    t[0] for t in inspect.getmembers(
                        mocked,
                        predicate=
                        lambda x: inspect.isfunction(x) or inspect.ismethod(x))
                    if t[0] != "__init__"
                ]))
    else:
        name = name if name else mocked.__name__
        if mock_modules:
            modules.extend(
                sorted([
                    t[0] for t in inspect.getmembers(mocked, inspect.ismodule)
                ]))
        if mock_functions:
            functions.extend(
                sorted([
                    t[0] for t in inspect.getmembers(
                        mocked,
                        predicate=
                        lambda x: inspect.isfunction(x) or inspect.ismethod(x))
                ]))
        if mock_builtin:
            functions.extend(
                sorted([
                    t[0] for t in inspect.getmembers(mocked, inspect.isbuiltin)
                ]))

        if mock_classes:
            classes.extend(
                sorted([
                    t[0] for t in inspect.getmembers(mocked, inspect.isclass)
                    if t[1].__module__ == mocked.__name__
                ]))
        if mock_referenced_classes:
            classes.extend(
                sorted([
                    t[0] for t in inspect.getmembers(mocked, inspect.isclass)
                    if not t[1].__module__ == mocked.__name__
                ]))

    if MockingFramework.PYTEST_MOCK == framework:
        return _pytest_mock_generate(name, modules, functions, methods,
                                     classes, mock_classes_static)
    else:
        raise ValueError(
            "Unsupported mocking framework: {0}. "
            "You are welcome to add code to support it :)".format(framework))


def _pytest_mock_generate(mocked_name, modules, functions, methods, classes,
                          mock_classes_static):
    generated = ""
    if modules:
        generated += "# mocked modules\n"
        for module in modules:
            generated += _single_pytest_mock_module_entry(mocked_name, module)
    if functions:
        generated += "# mocked functions\n"
        for func in functions:
            generated += _single_pytest_mock_module_entry(mocked_name, func)
    if methods:
        generated += "# mocked methods\n"
        for func in methods:
            generated += _single_pytest_mock_object_entry(mocked_name, func)
    if classes:
        generated += "# mocked classes\n"
        for cls in classes:
            generated += _mock_class_static(cls, mocked_name) if \
                mock_classes_static else \
                _single_pytest_mock_entry_with_spec(
                    mocked_name,
                    cls,
                    mocked_name + "." + cls)

    return generated


def _single_pytest_mock_module_entry(mocked_name, entry):
    return ("mock_{1} = mocker.MagicMock(name='{1}')\n"
            "mocker.patch('{0}.{1}', new=mock_{1})\n"). \
        format(mocked_name, entry)


def _single_pytest_mock_object_entry(mocked_name, entry):
    return "mocker.patch.object({0}, '{1}')\n".format(mocked_name, entry)


def _single_pytest_mock_entry_with_spec(mocked_name, entry, spec):
    return ("mock_{0} = mocker.MagicMock(name='{0}', spec={2})\n"
            "mocker.patch('{1}.{0}', new=mock_{0})\n"). \
        format(entry, mocked_name, spec)


def _mock_class_static(class_name, mocked_name):
    return ("""
class Mocked{0}Meta(type):
    static_instance = mocker.MagicMock(spec={1}.{0})

    def __getattr__(cls, key):
        return Mocked{0}Meta.static_instance.__getattr__(key)

class Mocked{0}(metaclass=Mocked{0}Meta):
    original_cls = {1}.{0}
    instances = []

    def __new__(cls, *args, **kwargs):
        Mocked{0}.instances.append(mocker.MagicMock(spec=Mocked{0}.original_cls))
        Mocked{0}.instances[-1].__class__ = Mocked{0}
        return Mocked{0}.instances[-1]

mocker.patch('{1}.{0}', new=Mocked{0})
""").format(class_name, mocked_name)


def get_call_list(mock, name=''):
    """
    Generates the asserts matching to the call list of the sent mock.

    Args:
        mock (MagicMock): the mock object to generate the asserts for
        name (string): the name of the mock parameter, if not provided would be
            guessed to match the argument name sent to the method and defaulted
            to 'arg'

    Returns:
        str: the asserts matching to the call list of the sent mock
    """
    name = name if name else _guess_var_name(mock)
    if not isinstance(mock, python_mock.MagicMock) and \
            not isinstance(mock, unittest.mock.MagicMock) and \
            not isinstance(mock, python_mock.Mock) and \
            not isinstance(mock, unittest.mock.Mock):
        raise TypeError("Unsupported mocking object: {0}. "
                        "You are welcome to add code to support it :)".format(
                            type(mock)))

    generated_asserts = ""
    if mock.call_args_list:
        generated_asserts += "assert {0} == {1}.call_count\n".format(
            len(mock.call_args_list), name)

    call_dictionary = OrderedDict()

    for all_calls in mock.mock_calls:
        method, args, kwargs = all_calls
        method = method.replace("()", ".return_value")
        if method and not method.startswith("."):
            method = "." + method
        if method not in call_dictionary:
            call_dictionary[method] = []
        call_dictionary[method].append(CallParameters(args, kwargs))

    had_multiple_calls_for_single_method = False
    for func_path, call_list in call_dictionary.items():
        if 1 == len(call_list):
            args, kwargs = call_list[0]
            generated_asserts += "{0}.assert_called_once_with({1})\n".format(
                name + func_path, _param_string(args, kwargs))
        else:
            had_multiple_calls_for_single_method = True
            generated_asserts += "{0}.assert_has_calls(calls=[".format(
                name + func_path)
            for call in call_list:
                args, kwargs = call
                generated_asserts += "call({0}),".format(
                    _param_string(args, kwargs))
            generated_asserts += "])\n"

    if had_multiple_calls_for_single_method:
        generated_asserts = "from mock import call\n\n" + generated_asserts

    if not generated_asserts:
        generated_asserts = "{0}.assert_not_called()".format(name)
    return generated_asserts


def _guess_var_name(var):
    """
    Guesses the argument name, according to the variable name sent to it, if
    unable to guess, returns 'arg'. See https://stackoverflow.com/a/2749881

    Args:
        var (object): the variable to figure the argument name

    Returns:
        str: the argument name, according to the variable name sent to it, if
            unable to guess, returns 'arg'.
    """
    lcls = inspect.stack()[2][0].f_locals
    for name in lcls:
        if id(var) == id(lcls[name]):
            return name
    return 'arg'


def _param_string(args, kwargs):
    params = ""
    if args:
        params += ', '.join(['{!r}'.format(v) for v in args])
    if kwargs:
        if params:
            params += ', '
        params += ', '.join(
            ['{}={!r}'.format(k, v) for k, v in sorted(kwargs.items())])
    return re.sub(r'(?P<default_repr>\<.*? object at 0x[0-9A-Fa-f]+\>)',
                  lambda default_repr: re.sub('[^0-9a-zA-Z.]+', '_',
                                              default_repr.group()), params)
