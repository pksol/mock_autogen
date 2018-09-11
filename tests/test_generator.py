import re
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
                 "second_module', new=mock_second_module)\n" \
                 "mock_zipfile = mocker.MagicMock(name='zipfile')\n" \
                 "mocker.patch('tests.sample.code.tested_module.zipfile', " \
                 "new=mock_zipfile)\n"

MOCKED_FUNCTIONS_HEADER = "# mocked functions\n"
MOCKED_FUNCTIONS = "mock_add = mocker.MagicMock(name='add')\n" \
                   "mocker.patch('tests.sample.code.tested_module.add', " \
                   "new=mock_add)\n" \
                   "mock_append_to_cwd = " \
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
                   "mock_process_and_zip = mocker.MagicMock(" \
                   "name='process_and_zip')\n" \
                   "mocker.patch('tests.sample.code.tested_module." \
                   "process_and_zip', new=mock_process_and_zip)\n" \
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
                                'os, second_module, add, append_to_cwd, '
                                'are_in_same_folder, other_dir, '
                                'rm_alias, rm_direct, second_dir, os_remove')

MocksModulesOnlyCollection = namedtuple('MocksModulesOnlyCollection',
                                        'os, second_module, zipfile')

MocksFunctionsOnlyCollection = namedtuple('MocksFunctionsOnlyCollection',
                                          'add, append_to_cwd, '
                                          'are_in_same_folder, '
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
    mock_zipfile = mocker.MagicMock(name='zipfile')
    mocker.patch('tests.sample.code.tested_module.zipfile',
                 new=mock_zipfile)

    yield MocksModulesOnlyCollection(mock_os, mock_second_module, mock_zipfile)


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
    mock_add = mocker.MagicMock(name='add')
    mocker.patch('tests.sample.code.tested_module.add', new=mock_add)
    mock_append_to_cwd = mocker.MagicMock(name='append_to_cwd')
    mocker.patch('tests.sample.code.tested_module.append_to_cwd',
                 new=mock_append_to_cwd)
    mock_are_in_same_folder = mocker.MagicMock(name='are_in_same_folder')
    mocker.patch('tests.sample.code.tested_module.are_in_same_folder',
                 new=mock_are_in_same_folder)
    mock_other_dir = mocker.MagicMock(name='other_dir')
    mocker.patch('tests.sample.code.tested_module.other_dir',
                 new=mock_other_dir)
    mock_process_and_zip = mocker.MagicMock(name='process_and_zip')
    mocker.patch('tests.sample.code.tested_module.process_and_zip',
                 new=mock_process_and_zip)
    mock_rm_alias = mocker.MagicMock(name='rm_alias')
    mocker.patch('tests.sample.code.tested_module.rm_alias', new=mock_rm_alias)
    mock_rm_direct = mocker.MagicMock(name='rm_direct')
    mocker.patch('tests.sample.code.tested_module.rm_direct',
                 new=mock_rm_direct)
    mock_second_dir = mocker.MagicMock(name='second_dir')
    mocker.patch('tests.sample.code.tested_module.second_dir',
                 new=mock_second_dir)

    yield MocksFunctionsOnlyCollection(mock_add,
                                       mock_append_to_cwd,
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
    mock_add = mocker.MagicMock(name='add')
    mocker.patch('tests.sample.code.tested_module.add', new=mock_add)
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

    yield MocksAllCollection(mock_os, mock_second_module, mock_add,
                             mock_append_to_cwd, mock_are_in_same_folder,
                             mock_other_dir,
                             mock_rm_alias, mock_rm_direct, mock_second_dir,
                             mock_os_remove)


def test_generate_mocks_modules_only():
    generated_mocks = mock_autogen.generator.generate_mocks(
        mock_autogen.generator.MockingFramework.PYTEST_MOCK,
        tests.sample.code.tested_module, mock_modules=True,
        mock_functions=False, mock_builtin=False)

    assert MOCKED_MODULES_HEADER + MOCKED_MODULES == generated_mocks


def test_generate_mocks_functions_only():
    generated_mocks = mock_autogen.generator.generate_mocks(
        mock_autogen.generator.MockingFramework.PYTEST_MOCK,
        tests.sample.code.tested_module, mock_modules=False,
        mock_functions=True, mock_builtin=False)

    assert MOCKED_FUNCTIONS_HEADER + MOCKED_FUNCTIONS == generated_mocks


def test_generate_mocks_builtin_only():
    generated_mocks = mock_autogen.generator.generate_mocks(
        mock_autogen.generator.MockingFramework.PYTEST_MOCK,
        tests.sample.code.tested_module, mock_modules=False,
        mock_functions=False, mock_builtin=True)

    assert MOCKED_FUNCTIONS_HEADER + MOCKED_BUILTIN == generated_mocks


def test_generate_mocks_all():
    generated_mocks = mock_autogen.generator.generate_mocks(
        mock_autogen.generator.MockingFramework.PYTEST_MOCK,
        tests.sample.code.tested_module, mock_modules=True,
        mock_functions=True, mock_builtin=True)

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
    generated = mock_autogen.generator.generate_call_list(
        mock_are_in_same_folder, 'mock_are_in_same_folder')
    assert 'assert 1 == mock_are_in_same_folder.call_count\n' \
           "mock_are_in_same_folder.assert_called_once_with(" \
           "'/some/path/file1.txt', '/some/path/file2.txt')\n" == generated
    exec generated  # verify the validity of assertions


def test_generate_call_list_mocks_are_untouched(
        mock_everything_collection):
    for mocked in mock_everything_collection:
        generated = mock_autogen.generator.generate_call_list(mocked)
        assert "" == generated


def test_generate_call_list_are_in_same_folder_kwargs(
        mock_functions_only_collection):
    tests.sample.code.tested_module.are_in_same_folder(
        path1='/some/path/file1.txt',
        path2='/some/path/file2.txt')

    mock_are_in_same_folder = mock_functions_only_collection.are_in_same_folder
    generated = mock_autogen.generator.generate_call_list(
        mock_are_in_same_folder,
        mock_name="mock_are_in_same_folder")
    assert "assert 1 == mock_are_in_same_folder.call_count\n" \
           "mock_are_in_same_folder.assert_called_once_with(" \
           "path1='/some/path/file1.txt', " \
           "path2='/some/path/file2.txt')\n" == generated
    exec generated  # verify the validity of assertions


def test_generate_call_list_are_in_same_folder_mix_args_kwargs(
        mock_everything_collection):
    tests.sample.code.tested_module.are_in_same_folder(
        '/some/path/file1.txt',
        path2='/some/path/file2.txt')

    mock_are_in_same_folder = mock_everything_collection.are_in_same_folder
    generated = mock_autogen.generator.generate_call_list(
        mock_are_in_same_folder, 'mock_are_in_same_folder')
    assert "assert 1 == mock_are_in_same_folder.call_count\n" \
           "mock_are_in_same_folder.assert_called_once_with(" \
           "'/some/path/file1.txt', " \
           "path2='/some/path/file2.txt')\n" == generated
    exec generated  # verify the validity of assertions


def test_generate_call_list_rm_alias_builtin_only(
        mock_builtin_only_collection):
    tests.sample.code.tested_module.rm_alias('/some/path/file1.txt')

    mock_os_remove = mock_builtin_only_collection.os_remove
    generated = mock_autogen.generator.generate_call_list(mock_os_remove,
                                                          'mock_os_remove')
    assert "assert 1 == mock_os_remove.call_count\n" \
           "mock_os_remove.assert_called_once_with('/some/path/file1.txt')\n" \
           == generated
    exec generated  # verify the validity of assertions


def test_generate_call_list_append_to_cwd_builtin_only(
        mock_modules_only_collection):
    tests.sample.code.tested_module.append_to_cwd('/some/path/file1.txt')

    mock_os = mock_modules_only_collection.os
    generated = mock_autogen.generator.generate_call_list(mock_os, 'mock_os')
    assert re.match(r"^mock_os.getcwd.assert_called_once_with\(\)\n"
                    r"mock_os.path.join.assert_called_once_with"
                    r"\(<MagicMock name='os.getcwd\(\)' id='\d+'>, "
                    r"'/some/path/file1.txt'\)\n$",
                    generated)

    # added ANY to match the mock parameter
    from mock import ANY
    mock_os.path.join.assert_called_once_with(ANY,
                                              '/some/path/file1.txt')
    mock_os.getcwd.assert_called_once_with()


def test_generate_call_list_append_to_cwd_builtin_only_mocked_cwd(
        mock_modules_only_collection):
    mock_os = mock_modules_only_collection.os

    # added this so the assert can be affective.
    # this is an example of the code the user has to add on top of the utility
    mock_os.getcwd.return_value = '/some/pwd'

    tests.sample.code.tested_module.append_to_cwd('/some/path/file1.txt')

    generated = mock_autogen.generator.generate_call_list(mock_os, 'mock_os')
    assert "mock_os.getcwd.assert_called_once_with()\n" \
           "mock_os.path.join.assert_called_once_with" \
           "('/some/pwd', '/some/path/file1.txt')\n" == generated
    exec generated  # verify the validity of assertions


def test_generate_call_list_add_mix_types(mock_functions_only_collection):
    tests.sample.code.tested_module.add('one', 2)

    mock_add = mock_functions_only_collection.add
    generated = mock_autogen.generator.generate_call_list(
        mock_add,
        mock_name="mock_add")
    assert 'assert 1 == mock_add.call_count\n' \
           "mock_add.assert_called_once_with(" \
           "'one', 2)\n" == generated
    exec generated  # verify the validity of assertions


def test_generate_call_list_add_multiple_calls(mock_functions_only_collection):
    tests.sample.code.tested_module.add(1, 2)
    tests.sample.code.tested_module.add('one', 'two')

    mock_add = mock_functions_only_collection.add
    generated = mock_autogen.generator.generate_call_list(
        mock_add,
        mock_name="mock_add")
    assert 'from mock import call\n\n' \
           'assert 2 == mock_add.call_count\n' \
           "mock_add.assert_has_calls(calls=[call(1, 2)," \
           "call('one', 'two'),])\n" == generated
    exec generated  # verify the validity of assertions


def test_generate_call_list_context_manager(mock_modules_only_collection):
    tests.sample.code.tested_module.process_and_zip('/path/to.zip',
                                                    'in_zip.txt', 'foo bar')

    mock_zipfile = mock_modules_only_collection.zipfile
    generated = mock_autogen.generator.generate_call_list(
        mock_zipfile,
        mock_name="mock_zipfile")
    assert "mock_zipfile.ZipFile.assert_called_once_with(" \
           "'/path/to.zip', 'w')\n" \
           "mock_zipfile.ZipFile.return_value.__enter__." \
           "assert_called_once_with()\n" \
           "mock_zipfile.ZipFile.return_value.__enter__." \
           "return_value.writestr.assert_called_once_with(" \
           "'in_zip.txt', 'processed foo bar')\n" \
           "mock_zipfile.ZipFile.return_value.__exit__." \
           "assert_called_once_with(None, None, None)\n" == generated
    exec generated  # verify the validity of assertions
