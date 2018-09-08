from aenum import Enum
import inspect

MockingFrameworks = Enum(
    'MockingFrameworks', 'PYTEST_MOCK')


def generate_mocks(mocking_framework, mocked_module, collect_modules=True,
                   collect_functions=False, collect_builtin=True):
    modules = []
    if collect_modules:
        modules.extend([t[0] for t in
                        inspect.getmembers(mocked_module, inspect.ismodule)])
    functions = []
    if collect_functions:
        functions.extend([t[0] for t in
                          inspect.getmembers(mocked_module,
                                             inspect.isfunction)])
    if collect_builtin:
        functions.extend([t[0] for t in
                          inspect.getmembers(
                              mocked_module, inspect.isbuiltin)])

        if MockingFrameworks.PYTEST_MOCK == mocking_framework:
            return _pytest_mock_generate(mocked_module, modules, functions)
        else:
            raise ValueError("Unsupported mocking framework.")


def _pytest_mock_generate(mocked_module, modules, functions):
    generated = ""
    if modules:
        generated += "# mocked modules\n"
        for module in modules:
            generated += "mock_{0} = mocker.MagicMock(name='{0}')\n".format(
                module)
            generated += "mocker.patch('{0}.{1}', new=mock_{1})\n".format(
                mocked_module.__name__, module)

    return generated
