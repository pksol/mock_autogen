import mock_autogen.generator
import tests.sample.code.tested_module

MOCKED_MODULES_HEADER = "# mocked modules\n"
MOCKED_MODULES = "mock_os = mocker.MagicMock(name='os')\n" \
                 "mocker.patch('tests.sample.code.tested_module.os', " \
                 "new=mock_os)\n" \
                 "mock_second_module = " \
                 "mocker.MagicMock(name='second_module')\n" \
                 "mocker.patch('tests.sample.code.tested_module." \
                 "second_module', new=mock_second_module)\n"

MOCKED_FUNCTIONS_HEADER = "# mocked functions\n"
MOCKED_FUNCTIONS = "mock_append_to_cwd = " \
                   "mocker.MagicMock(name='append_to_cwd')\n" \
                   "mocker.patch('tests.sample.code.tested_module." \
                   "append_to_cwd', new=mock_append_to_cwd)\n" \
                   "mock_are_in_same_folder = " \
                   "mocker.MagicMock(name='are_in_same_folder')\n" \
                   "mocker.patch('tests.sample.code.tested_module." \
                   "are_in_same_folder', new=mock_are_in_same_folder)\n" \
                   "mock_other_dir = mocker.MagicMock(name='other_dir')\n" \
                   "mocker.patch('tests.sample.code.tested_module." \
                   "other_dir', new=mock_other_dir)\n" \
                   "mock_rm_alias = mocker.MagicMock(name='rm_alias')\n" \
                   "mocker.patch('tests.sample.code.tested_module." \
                   "rm_alias', new=mock_rm_alias)\n" \
                   "mock_rm_direct = mocker.MagicMock(name='rm_direct')\n" \
                   "mocker.patch('tests.sample.code.tested_module." \
                   "rm_direct', new=mock_rm_direct)\n" \
                   "mock_second_dir = mocker.MagicMock(name='second_dir')\n" \
                   "mocker.patch('tests.sample.code.tested_module." \
                   "second_dir', new=mock_second_dir)\n"
MOCKED_BUILTIN = "mock_os_remove = mocker.MagicMock(name='os_remove')\n" \
                 "mocker.patch('tests.sample.code.tested_module.os_remove', " \
                 "new=mock_os_remove)\n"


def test_generate_mocks_modules_only():
    generated_mocks = mock_autogen.generator.generate_mocks(
        mock_autogen.generator.MockingFrameworks.PYTEST_MOCK,
        tests.sample.code.tested_module, collect_modules=True,
        collect_functions=False, collect_builtin=False)
    assert MOCKED_MODULES_HEADER + MOCKED_MODULES == generated_mocks


def test_generate_mocks_functions_only():
    generated_mocks = mock_autogen.generator.generate_mocks(
        mock_autogen.generator.MockingFrameworks.PYTEST_MOCK,
        tests.sample.code.tested_module, collect_modules=False,
        collect_functions=True, collect_builtin=False)
    assert MOCKED_FUNCTIONS_HEADER + MOCKED_FUNCTIONS == generated_mocks


def test_generate_mocks_builtin_only():
    generated_mocks = mock_autogen.generator.generate_mocks(
        mock_autogen.generator.MockingFrameworks.PYTEST_MOCK,
        tests.sample.code.tested_module, collect_modules=False,
        collect_functions=False, collect_builtin=True)
    assert MOCKED_FUNCTIONS_HEADER + MOCKED_BUILTIN == generated_mocks


def test_generate_mocks_all():
    generated_mocks = mock_autogen.generator.generate_mocks(
        mock_autogen.generator.MockingFrameworks.PYTEST_MOCK,
        tests.sample.code.tested_module, collect_modules=True,
        collect_functions=True, collect_builtin=True)
    assert MOCKED_MODULES_HEADER + MOCKED_MODULES + \
        MOCKED_FUNCTIONS_HEADER + MOCKED_FUNCTIONS + MOCKED_BUILTIN == \
        generated_mocks


def test_generate_mocks_default():
    generated_mocks = mock_autogen.generator.generate_mocks(
        mock_autogen.generator.MockingFrameworks.PYTEST_MOCK,
        tests.sample.code.tested_module)
    assert MOCKED_MODULES_HEADER + MOCKED_MODULES + \
        MOCKED_FUNCTIONS_HEADER + MOCKED_BUILTIN == generated_mocks
