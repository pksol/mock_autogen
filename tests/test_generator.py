from collections import namedtuple

import pytest

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

MocksAllCollection = namedtuple('MocksAllCollection',
                                'os, second_module, append_to_cwd, '
                                'are_in_same_folder, other_dir, rm_alias, '
                                'rm_direct, second_dir, os_remove')

MocksModulesOnlyCollection = namedtuple('MocksModulesOnlyCollection',
                                        'os, second_module')

MocksFunctionsOnlyCollection = namedtuple('MocksFunctionsOnlyCollection',
                                          'append_to_cwd, are_in_same_folder, '
                                          'other_dir, rm_alias, '
                                          'rm_direct, second_dir')

MocksBuiltinOnlyCollection = namedtuple('MocksAllCollection', 'os_remove')


@pytest.fixture
def mock_modules_only_collection(mocker):
    """
    The mocks are taken from `test_generate_mocks_modules_only` :)

    Args:
        mocker (pytest.fixture): the mocker fixture

    Yields:
        MocksModulesOnlyCollection: The generated mocks.
    """
    # mocked modules
    mock_os = mocker.MagicMock(name='os')
    mocker.patch('tests.sample.code.tested_module.os', new=mock_os)
    mock_second_module = mocker.MagicMock(name='second_module')
    mocker.patch('tests.sample.code.tested_module.second_module',
                 new=mock_second_module)

    yield MocksModulesOnlyCollection(mock_os, mock_second_module)


@pytest.fixture
def mock_functions_only_collection(mocker):
    """
    The mocks are taken from `test_generate_mocks_functions_only` :)

    Args:
        mocker (pytest.fixture): the mocker fixture

    Yields:
        MocksFunctionsOnlyCollection: The generated mocks.
    """
    # mocked functions
    mock_append_to_cwd = mocker.MagicMock(name='append_to_cwd')
    mocker.patch('tests.sample.code.tested_module.append_to_cwd',
                 new=mock_append_to_cwd)
    mock_are_in_same_folder = mocker.MagicMock(name='are_in_same_folder')
    mocker.patch('tests.sample.code.tested_module.are_in_same_folder',
                 new=mock_are_in_same_folder)
    mock_other_dir = mocker.MagicMock(name='other_dir')
    mocker.patch('tests.sample.code.tested_module.other_dir',
                 new=mock_other_dir)
    mock_rm_alias = mocker.MagicMock(name='rm_alias')
    mocker.patch('tests.sample.code.tested_module.rm_alias', new=mock_rm_alias)
    mock_rm_direct = mocker.MagicMock(name='rm_direct')
    mocker.patch('tests.sample.code.tested_module.rm_direct',
                 new=mock_rm_direct)
    mock_second_dir = mocker.MagicMock(name='second_dir')
    mocker.patch('tests.sample.code.tested_module.second_dir',
                 new=mock_second_dir)

    yield MocksFunctionsOnlyCollection(mock_append_to_cwd,
                                       mock_are_in_same_folder,
                                       mock_other_dir,
                                       mock_rm_alias, mock_rm_direct,
                                       mock_second_dir)


@pytest.fixture
def mock_builtin_only_collection(mocker):
    """
    The mocks are taken from `test_generate_mocks_builtin_only` :)

    Args:
        mocker (pytest.fixture): the mocker fixture

    Yields:
        MocksBuiltinOnlyCollection: The generated mocks.
    """
    # mocked functions
    mock_os_remove = mocker.MagicMock(name='os_remove')
    mocker.patch('tests.sample.code.tested_module.os_remove',
                 new=mock_os_remove)

    yield MocksBuiltinOnlyCollection(mock_os_remove)


@pytest.fixture
def mock_everything_collection(mocker):
    """
    The mocks are taken from `test_generate_mocks_all` :)

    Args:
        mocker (pytest.fixture): the mocker fixture

    Yields:
        MocksAllCollection: The generated mocks.
    """
    # mocked modules
    mock_os = mocker.MagicMock(name='os')
    mocker.patch('tests.sample.code.tested_module.os', new=mock_os)
    mock_second_module = mocker.MagicMock(name='second_module')
    mocker.patch('tests.sample.code.tested_module.second_module',
                 new=mock_second_module)
    # mocked functions
    mock_append_to_cwd = mocker.MagicMock(name='append_to_cwd')
    mocker.patch('tests.sample.code.tested_module.append_to_cwd',
                 new=mock_append_to_cwd)
    mock_are_in_same_folder = mocker.MagicMock(name='are_in_same_folder')
    mocker.patch('tests.sample.code.tested_module.are_in_same_folder',
                 new=mock_are_in_same_folder)
    mock_other_dir = mocker.MagicMock(name='other_dir')
    mocker.patch('tests.sample.code.tested_module.other_dir',
                 new=mock_other_dir)
    mock_rm_alias = mocker.MagicMock(name='rm_alias')
    mocker.patch('tests.sample.code.tested_module.rm_alias', new=mock_rm_alias)
    mock_rm_direct = mocker.MagicMock(name='rm_direct')
    mocker.patch('tests.sample.code.tested_module.rm_direct',
                 new=mock_rm_direct)
    mock_second_dir = mocker.MagicMock(name='second_dir')
    mocker.patch('tests.sample.code.tested_module.second_dir',
                 new=mock_second_dir)
    mock_os_remove = mocker.MagicMock(name='os_remove')
    mocker.patch('tests.sample.code.tested_module.os_remove',
                 new=mock_os_remove)

    yield MocksAllCollection(mock_os, mock_second_module,
                             mock_append_to_cwd, mock_are_in_same_folder,
                             mock_other_dir,
                             mock_rm_alias, mock_rm_direct, mock_second_dir,
                             mock_os_remove)


def test_generate_mocks_modules_only():
    generated_mocks = mock_autogen.generator.generate_mocks(
        mock_autogen.generator.MockingFramework.PYTEST_MOCK,
        tests.sample.code.tested_module, collect_modules=True,
        collect_functions=False, collect_builtin=False)
    assert MOCKED_MODULES_HEADER + MOCKED_MODULES == generated_mocks


def test_generate_mocks_functions_only():
    generated_mocks = mock_autogen.generator.generate_mocks(
        mock_autogen.generator.MockingFramework.PYTEST_MOCK,
        tests.sample.code.tested_module, collect_modules=False,
        collect_functions=True, collect_builtin=False)
    assert MOCKED_FUNCTIONS_HEADER + MOCKED_FUNCTIONS == generated_mocks


def test_generate_mocks_builtin_only():
    generated_mocks = mock_autogen.generator.generate_mocks(
        mock_autogen.generator.MockingFramework.PYTEST_MOCK,
        tests.sample.code.tested_module, collect_modules=False,
        collect_functions=False, collect_builtin=True)
    assert MOCKED_FUNCTIONS_HEADER + MOCKED_BUILTIN == generated_mocks


def test_generate_mocks_all():
    generated_mocks = mock_autogen.generator.generate_mocks(
        mock_autogen.generator.MockingFramework.PYTEST_MOCK,
        tests.sample.code.tested_module, collect_modules=True,
        collect_functions=True, collect_builtin=True)
    assert MOCKED_MODULES_HEADER + MOCKED_MODULES + \
           MOCKED_FUNCTIONS_HEADER + MOCKED_FUNCTIONS + MOCKED_BUILTIN == \
           generated_mocks


def test_generate_mocks_default():
    generated_mocks = mock_autogen.generator.generate_mocks(
        mock_autogen.generator.MockingFramework.PYTEST_MOCK,
        tests.sample.code.tested_module)
    assert MOCKED_MODULES_HEADER + MOCKED_MODULES + \
           MOCKED_FUNCTIONS_HEADER + MOCKED_BUILTIN == generated_mocks


def test_generate_call_list_are_in_same_folder_args(
        mock_everything_collection):
    tests.sample.code.tested_module.are_in_same_folder('/some/path/file1.txt',
                                                       '/some/path/file2.txt')
    mock_are_in_same_folder = mock_everything_collection.are_in_same_folder
    for mocked in mock_everything_collection:
        generated = mock_autogen.generator.generate_call_list(mocked)
        if mocked != mock_are_in_same_folder:
            assert 'assert 0 == mocked.call_count\n' == generated
        else:
            assert 'assert 1 == mocked.call_count\n' \
                   "mocked.assert_called_once_with('/some/path/file1.txt', " \
                   "'/some/path/file2.txt')" == generated
        exec generated  # verify the validity of assertions


def test_generate_call_list_rm_direct_kwargs(mock_functions_only_collection):
    tests.sample.code.tested_module.are_in_same_folder(
        path1='/some/path/file1.txt',
        path2='/some/path/file2.txt')
    mock_are_in_same_folder = mock_functions_only_collection.are_in_same_folder
    for mocked in mock_functions_only_collection:
        generated = mock_autogen.generator.generate_call_list(mocked)
        if mocked != mock_are_in_same_folder:
            assert 'assert 0 == mocked.call_count\n' == generated
        else:
            assert 'assert 1 == mocked.call_count\n' \
                   "mocked.assert_called_once_with(" \
                   "path1='/some/path/file1.txt', " \
                   "path2='/some/path/file2.txt')" == generated
        exec generated  # verify the validity of assertions


def test_generate_call_list_rm_direct_mix_args_kwargs(
        mock_everything_collection):
    tests.sample.code.tested_module.are_in_same_folder(
        '/some/path/file1.txt',
        path2='/some/path/file2.txt')
    mock_are_in_same_folder = mock_everything_collection.are_in_same_folder
    for mocked in mock_everything_collection:
        generated = mock_autogen.generator.generate_call_list(mocked)
        if mocked != mock_are_in_same_folder:
            assert 'assert 0 == mocked.call_count\n' == generated
        else:
            assert 'assert 1 == mocked.call_count\n' \
                   "mocked.assert_called_once_with(" \
                   "'/some/path/file1.txt', " \
                   "path2='/some/path/file2.txt')" == generated
        exec generated  # verify the validity of assertions


def test_generate_call_list_rm_alias_builtin_only(
        mock_builtin_only_collection):
    tests.sample.code.tested_module.rm_alias('/some/path/file1.txt')
    mock_os_remove = mock_builtin_only_collection.os_remove
    for mocked in mock_builtin_only_collection:
        generated = mock_autogen.generator.generate_call_list(mocked)
        if mocked != mock_os_remove:
            assert 'assert 0 == mocked.call_count\n' == generated
        else:
            assert 'assert 1 == mocked.call_count\n' \
                   "mocked.assert_called_once_with('/some/path/file1.txt')" \
                   == generated
        exec generated  # verify the validity of assertions