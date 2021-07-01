import inspect
import logging
import re
import types
import unittest.mock
from collections import namedtuple, OrderedDict
from enum import Enum

import mock as python_mock

from mock_autogen.ast_tree_travel import FuncLister
from mock_autogen.utils import copy_result_to_clipboard, print_result, \
    get_unique_item

logger = logging.getLogger(__name__)

MockingFramework = Enum('MockingFramework', 'PYTEST_MOCK')
CallParameters = namedtuple('CallParameters', 'args, kwargs')


@copy_result_to_clipboard
@print_result
def generate_mocks(framework,
                   mocked,
                   name='',
                   mock_modules=True,
                   mock_functions=False,
                   mock_builtin=True,
                   mock_classes=False,
                   mock_referenced_classes=True,
                   mock_classes_static=False,
                   prepare_asserts_calls=True):
    """
    Generates the list of mocks in order to mock the dependant modules and the
    functions of a given module, class or object instance.

    Note that the returned code is the initial basic code on which you can add
    your custom logic like function return values.

    This method can also be used to prepare the calls to `generate_asserts`, in
    case `prepare_asserts_calls` is set to `True`.

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
        mock_classes (bool): whether to mock classes defined in the module, or
            a sent class. Ignored if this is a plain instance
        mock_referenced_classes (bool): whether to mock classes referenced in
            the module but defined elsewhere. Relevant only if `mocked`
            is `types.ModuleType`
        mock_classes_static (bool): whether to mock the static functions of the
            mocked classes. This is important if the tested code uses
            static class functions directly. Used only if
            mock_classes or mock_referenced_classes is `True`.
            Ignored if this is a plain instance
        prepare_asserts_calls (bool): whether to generate the subsequent calls
            to `generate_asserts` for the mocks generated by this call

    Returns:
        str: the initial code to put in your test to mock the desired behaviour
    """
    modules = []
    functions = []
    classes = []
    methods = []

    # we're mocking a class
    if inspect.isclass(mocked):
        name = name if name else _guess_var_name(name)
        if mock_classes:
            classes.append(mocked.__name__)
        if mock_functions:
            methods.extend(
                sorted([
                    t[0] for t in inspect.getmembers(
                        mocked,
                        predicate=lambda x: inspect.isfunction(
                            x) or inspect.ismethod(x)) if t[0] != "__init__"
                ]))
    # we're mocking a module
    elif isinstance(mocked, types.ModuleType):
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
                        predicate=lambda x: inspect.isfunction(
                            x) or inspect.ismethod(x))
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
    # mocking a function or a method
    elif inspect.isfunction(mocked) or inspect.ismethod(mocked):
        func_lister = FuncLister(mocked).execute()
        if func_lister.warnings:
            func_lister.warnings.insert(0, "# warnings")
            func_lister.warnings[-1] = func_lister.warnings[-1] + "\n"

        return "\n".join(
            func_lister.warnings) + _pytest_mock_function_generate(
                func_lister.dependencies_found, prepare_asserts_calls)
    # we're mocking a regular instance
    else:
        name = name if name else _guess_var_name(name)
        if mock_functions:
            methods.extend(
                sorted([
                    t[0] for t in inspect.getmembers(
                        mocked,
                        predicate=lambda x: inspect.isfunction(
                            x) or inspect.ismethod(x)) if t[0] != "__init__"
                ]))

    if MockingFramework.PYTEST_MOCK == framework:
        return _pytest_mock_generate(name, modules, functions, methods,
                                     classes, mock_classes_static,
                                     prepare_asserts_calls)
    else:
        raise ValueError(
            "Unsupported mocking framework: {0}. "
            "You are welcome to add code to support it :)".format(framework))


def _pytest_mock_function_generate(functions, prepare_asserts_calls):
    generated_code = ""
    unique_functions = set()
    mock_names = []
    if functions:
        generated_code += "# mocked functions\n"  # todo: replace with mocked dependencies
        for (
                func_path,  # todo: this can be none if we mock root module
                func_name,  # todo: replace with object var names
        ) in functions:
            unique_name = get_unique_item(unique_functions, func_name)
            generated_mock_name, generated_mock_code = \
                _single_pytest_mock_module_entry_with_alias(unique_name,
                                                            func_name,
                                                            func_path)
            mock_names.append(generated_mock_name)
            generated_code += generated_mock_code

    if prepare_asserts_calls and mock_names:
        generated_code += "# calls to generate_asserts, " \
                          "put this after the 'act'\n" \
                          "import mock_autogen\n"
        for mock_name in mock_names:
            generated_code += _single_call_to_generate_asserts(mock_name)

    return generated_code


def _pytest_mock_generate(mocked_name, modules, functions, methods, classes,
                          mock_classes_static, prepare_asserts_calls):
    generated_code = ""
    mock_names = []
    if modules:
        generated_code += "# mocked modules\n"
        for module in modules:
            generated_mock_name, generated_mock_code = \
                _single_pytest_mock_module_entry(mocked_name, module)
            mock_names.append(generated_mock_name)
            generated_code += generated_mock_code
    if functions:
        generated_code += "# mocked functions\n"
        for func in functions:
            generated_mock_name, generated_mock_code = \
                _single_pytest_mock_module_entry(mocked_name, func)
            mock_names.append(generated_mock_name)
            generated_code += generated_mock_code
    if methods:
        generated_code += "# mocked methods\n"
        for func in methods:
            generated_code += _single_pytest_mock_object_entry(
                mocked_name, func)
    if classes:
        generated_code += "# mocked classes\n"
        for cls in classes:
            if mock_classes_static:
                generated_code += _mock_class_static(cls, mocked_name)
            else:
                generated_mock_name, generated_mock_code = \
                    _single_pytest_mock_entry_with_spec(
                        mocked_name,
                        cls,
                        mocked_name + "." + cls)
                mock_names.append(generated_mock_name)
                generated_code += generated_mock_code
    if prepare_asserts_calls and mock_names:
        generated_code += "# calls to generate_asserts, " \
                          "put this after the 'act'\n" \
                          "import mock_autogen\n"
        for mock_name in mock_names:
            generated_code += _single_call_to_generate_asserts(mock_name)

    return generated_code


def _single_pytest_mock_module_entry(mocked_name, entry):
    return "mock_{0}".format(entry), \
           ("mock_{0} = mocker.MagicMock(name='{0}')\n"
            "mocker.patch('{1}.{0}', new=mock_{0})\n"). \
               format(entry, mocked_name)


def _single_pytest_mock_module_entry_with_alias(mock_name, function, module):
    return f"mock_{mock_name}", \
           f"mock_{mock_name} = mocker.MagicMock(name='{mock_name}')\n" \
           f"mocker.patch('{module}.{function}', new=mock_{mock_name})\n"


def _single_pytest_mock_object_entry(mocked_name, entry):
    return "mocker.patch.object({0}, '{1}')\n".format(mocked_name, entry)


def _single_pytest_mock_entry_with_spec(mocked_name, entry, spec):
    return "mock_{0}".format(entry), \
           ("mock_{0} = mocker.MagicMock(name='{0}', spec={2})\n"
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


def _single_call_to_generate_asserts(mock_name):
    return "mock_autogen.generate_asserts(" \
           "{0}, name='{0}')\n".format(mock_name)


@copy_result_to_clipboard
@print_result
def generate_asserts(mock, name=''):
    """
    Generates the asserts matching to the call list of the sent mock.

    The generated asserts are printed to the console, copied to the clipboard
    and returned.

    Args:
        mock (Mock or MagicMock): the mock object to generate the asserts for
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
    for stack in range(2, len(inspect.stack())):
        lcls = inspect.stack()[stack][0].f_locals
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
    return re.sub(
        r'(?P<default_repr>\<.*? object at 0x[0-9A-Fa-f]+\>)',
        lambda default_repr: re.sub('[^0-9a-zA-Z.]+', '_', default_repr.group(
        )), params)
