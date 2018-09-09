from aenum import Enum
import inspect

from mock import MagicMock

MockingFramework = Enum(
    'MockingFramework', 'PYTEST_MOCK')


def generate_mocks(mocking_framework, mocked_module, collect_modules=True,
                   collect_functions=False, collect_builtin=True):
    """
    Generates the list of mocks in order to mock the dependant modules and the
    functions of the given module.

    Note that the returned code is the initial basic code on which you can add
    your custom logic like function return values.

    Args:
        mocking_framework (MockingFramework): the type of the mocking
            framework to use
        mocked_module (types.ModuleType): the module to mock
        collect_modules (bool): whether to mock dependant modules which are
            referenced from the mocked module
        collect_functions (bool): whether to mock functions defined in the
            module
        collect_builtin (bool): whether to mock builtin functions defined in
            the module

    Returns:
        str: the code to put in your test to mock the desired behaviour.
    """
    modules = []
    if collect_modules:
        modules.extend(sorted([t[0] for t in
                               inspect.getmembers(mocked_module,
                                                  inspect.ismodule)]))
    functions = []
    if collect_functions:
        functions.extend(sorted([t[0] for t in
                                 inspect.getmembers(mocked_module,
                                                    inspect.isfunction)]))
    if collect_builtin:
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
    # mock_zip_dbmanage_cs_logs.zip.ZipFile.return_value.__enter__. \
    #     return_value.write. \
    #     assert_has_calls(
    #     calls=[call(archive_path, archive_name),
    #            call(os.path.join(ARCHIVE_DIR,
    #                              const.CONSTRAINT_STREAM_FILENAME),
    #                 const.CONSTRAINT_STREAM_FILENAME)])
    # mock_zip_dbmanage_cs_logs.zip.ZipFile.return_value.__enter__. \
    #     return_value.writestr. \
    #     assert_called_once_with("unitdef.xlsx", EXCEL_DATA)
    if not isinstance(mock_object, MagicMock):
        raise TypeError("Unsupported mocking object: {0}. "
                        "You are welcome to add code to support it :)".
                        format(type(mock_object)))

    generated_asserts = "assert {0} == {1}.call_count\n".format(
        len(mock_object.call_args_list), mock_name)

    if mock_object.call_args_list:
        if 1 == len(mock_object.call_args_list):
            args, kwargs = mock_object.call_args_list[0]
            generated_asserts += "{0}.assert_called_once_with({1})".format(
                mock_name, _param_string(args, kwargs))
        else:
            # todo: add support for multiple function invocation
            for call in mock_object.call_args_list:
                args, kwargs = call

    # todo: support recursive calls, ensure __enter__ works

    return generated_asserts


def _param_string(args, kwargs):
    params = ""
    if args:
        params += ', '.join(['{!r}'.format(v) for v in args])
    if kwargs:
        if params:
            params += ', '
        params += ', '.join(
            ['{}={!r}'.format(k, v) for k, v in sorted(kwargs.items())])
    return params
