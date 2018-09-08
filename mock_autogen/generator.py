from aenum import Enum
import inspect

MockingFrameworks = Enum(
    'MockingFrameworks', 'PYTEST_MOCK')


def generate_mocks(mocking_framework, mocked_module, collect_modules=True,
                   collect_functions=False, collect_builtin=True):
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

    if MockingFrameworks.PYTEST_MOCK == mocking_framework:
        return _pytest_mock_generate(mocked_module, modules, functions)
    else:
        raise ValueError("Unsupported mocking framework.")


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
