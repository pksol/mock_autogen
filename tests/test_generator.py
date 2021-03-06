import re
from collections import namedtuple

import pytest

import mock_autogen.generator
import tests.sample.code.tested_module
import tests.sample.code.second_module

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
                   "mock_get_current_time = mocker.MagicMock" \
                   "(name='get_current_time')\n" \
                   "mocker.patch('tests.sample.code.tested_module." \
                   "get_current_time', new=mock_get_current_time)\n" \
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
                   "second_dir', new=mock_second_dir)\n" \
                   "mock_use_first_class = mocker.MagicMock(" \
                   "name='use_first_class')\n" \
                   "mocker.patch('tests.sample.code.tested_module." \
                   "use_first_class', new=mock_use_first_class)\n" \
                   "mock_use_second_class_static = mocker.MagicMock(" \
                   "name='use_second_class_static')\n" \
                   "mocker.patch('tests.sample.code.tested_module." \
                   "use_second_class_static', " \
                   "new=mock_use_second_class_static)\n"
MOCKED_BUILTIN = "mock_os_remove = mocker.MagicMock(name='os_remove')\n" \
                 "mocker.patch('tests.sample.code.tested_module.os_remove', " \
                 "new=mock_os_remove)\n"

MOCKED_METHODS_HEADER = "# mocked methods\n"
MOCKED_METHODS = "mocker.patch.object(first, 'not_implemented')\n"

MOCKED_CLASSES_HEADER = "# mocked classes\n"
MOCKED_CLASSES = "mock_FirstClass = mocker.MagicMock(name='FirstClass', " \
                 "spec=tests.sample.code.tested_module.FirstClass)\n" \
                 "mocker.patch('tests.sample.code.tested_module.FirstClass'," \
                 " new=mock_FirstClass)\n" \
                 "mock_SecondClass = mocker.MagicMock(name='SecondClass', " \
                 "spec=tests.sample.code.tested_module.SecondClass)\n" \
                 "mocker.patch('tests.sample.code.tested_module.SecondClass'" \
                 ", new=mock_SecondClass)\n"
MOCKED_REFERENCED_CLASSES = "mock_dt = mocker.MagicMock(name='dt', " \
                            "spec=tests.sample.code.tested_module.dt)\n" \
                            "mocker.patch('tests.sample.code.tested_module." \
                            "dt', new=mock_dt)\n"
MOCKED_CLASSES_STATIC = """
class MockedFirstClassMeta(type):
    static_instance = mocker.MagicMock(spec=tests.sample.code.tested_module.FirstClass)

    def __getattr__(cls, key):
        return MockedFirstClassMeta.static_instance.__getattr__(key)

class MockedFirstClass(metaclass=MockedFirstClassMeta):
    original_cls = tests.sample.code.tested_module.FirstClass
    instances = []

    def __new__(cls, *args, **kwargs):
        MockedFirstClass.instances.append(mocker.MagicMock(spec=MockedFirstClass.original_cls))
        MockedFirstClass.instances[-1].__class__ = MockedFirstClass
        return MockedFirstClass.instances[-1]

mocker.patch('tests.sample.code.tested_module.FirstClass', new=MockedFirstClass)

class MockedSecondClassMeta(type):
    static_instance = mocker.MagicMock(spec=tests.sample.code.tested_module.SecondClass)

    def __getattr__(cls, key):
        return MockedSecondClassMeta.static_instance.__getattr__(key)

class MockedSecondClass(metaclass=MockedSecondClassMeta):
    original_cls = tests.sample.code.tested_module.SecondClass
    instances = []

    def __new__(cls, *args, **kwargs):
        MockedSecondClass.instances.append(mocker.MagicMock(spec=MockedSecondClass.original_cls))
        MockedSecondClass.instances[-1].__class__ = MockedSecondClass
        return MockedSecondClass.instances[-1]

mocker.patch('tests.sample.code.tested_module.SecondClass', new=MockedSecondClass)
"""

MOCKED_REFERENCED_CLASSES_STATIC = """
class MockeddtMeta(type):
    static_instance = mocker.MagicMock(spec=tests.sample.code.tested_module.dt)

    def __getattr__(cls, key):
        return MockeddtMeta.static_instance.__getattr__(key)

class Mockeddt(metaclass=MockeddtMeta):
    original_cls = tests.sample.code.tested_module.dt
    instances = []

    def __new__(cls, *args, **kwargs):
        Mockeddt.instances.append(mocker.MagicMock(spec=Mockeddt.original_cls))
        Mockeddt.instances[-1].__class__ = Mockeddt
        return Mockeddt.instances[-1]

mocker.patch('tests.sample.code.tested_module.dt', new=Mockeddt)
"""

PREPARE_ASSERTS_CALLS_HEADER = "# calls to generate_asserts, put this after the 'act'\nimport mock_autogen.generator\n"

PREPARE_ASSERTS_CALLS_DEFAULT = """print(mock_autogen.generator.generate_asserts(mock_os, name='mock_os'))
print(mock_autogen.generator.generate_asserts(mock_second_module, name='mock_second_module'))
print(mock_autogen.generator.generate_asserts(mock_zipfile, name='mock_zipfile'))
print(mock_autogen.generator.generate_asserts(mock_os_remove, name='mock_os_remove'))
print(mock_autogen.generator.generate_asserts(mock_dt, name='mock_dt'))
"""

PREPARE_ASSERTS_CALLS_ALL = """print(mock_autogen.generator.generate_asserts(mock_os, name='mock_os'))
print(mock_autogen.generator.generate_asserts(mock_second_module, name='mock_second_module'))
print(mock_autogen.generator.generate_asserts(mock_zipfile, name='mock_zipfile'))
print(mock_autogen.generator.generate_asserts(mock_add, name='mock_add'))
print(mock_autogen.generator.generate_asserts(mock_append_to_cwd, name='mock_append_to_cwd'))
print(mock_autogen.generator.generate_asserts(mock_are_in_same_folder, name='mock_are_in_same_folder'))
print(mock_autogen.generator.generate_asserts(mock_get_current_time, name='mock_get_current_time'))
print(mock_autogen.generator.generate_asserts(mock_other_dir, name='mock_other_dir'))
print(mock_autogen.generator.generate_asserts(mock_process_and_zip, name='mock_process_and_zip'))
print(mock_autogen.generator.generate_asserts(mock_rm_alias, name='mock_rm_alias'))
print(mock_autogen.generator.generate_asserts(mock_rm_direct, name='mock_rm_direct'))
print(mock_autogen.generator.generate_asserts(mock_second_dir, name='mock_second_dir'))
print(mock_autogen.generator.generate_asserts(mock_use_first_class, name='mock_use_first_class'))
print(mock_autogen.generator.generate_asserts(mock_use_second_class_static, name='mock_use_second_class_static'))
print(mock_autogen.generator.generate_asserts(mock_os_remove, name='mock_os_remove'))
print(mock_autogen.generator.generate_asserts(mock_FirstClass, name='mock_FirstClass'))
print(mock_autogen.generator.generate_asserts(mock_SecondClass, name='mock_SecondClass'))
print(mock_autogen.generator.generate_asserts(mock_dt, name='mock_dt'))
"""

MocksAllCollection = namedtuple(
    'MocksAllCollection', 'os, second_module, add, append_to_cwd, '
    'are_in_same_folder, other_dir, '
    'rm_alias, rm_direct, second_dir, os_remove')

MocksModulesOnlyCollection = namedtuple('MocksModulesOnlyCollection',
                                        'os, second_module, zipfile')

MocksClassesOnlyCollection = namedtuple('MocksClassesOnlyCollection',
                                        'first, second, datetime')

MocksFunctionsOnlyCollection = namedtuple(
    'MocksFunctionsOnlyCollection', 'add, append_to_cwd, '
    'are_in_same_folder, '
    'other_dir, rm_alias, '
    'rm_direct, second_dir')

MocksBuiltinOnlyCollection = namedtuple('MocksAllCollection', 'os_remove')


@pytest.fixture
def mock_classes_only_collection(mocker):
    """
    The mocks are taken from `test_generate_mocks_modules_only` :)

    Args:
        mocker (pytest.fixture): the mocker fixture

    Yields:
        MocksClassesOnlyCollection: The generated mocks.
    """
    # mocked classes
    mock_FirstClass = mocker.MagicMock(
        name='FirstClass', spec=tests.sample.code.tested_module.FirstClass)
    mocker.patch('tests.sample.code.tested_module.FirstClass',
                 new=mock_FirstClass)
    mock_SecondClass = mocker.MagicMock(
        name='SecondClass', spec=tests.sample.code.tested_module.SecondClass)
    mocker.patch('tests.sample.code.tested_module.SecondClass',
                 new=mock_SecondClass)
    mock_dt = mocker.MagicMock(name='dt',
                               spec=tests.sample.code.tested_module.dt)
    mocker.patch('tests.sample.code.tested_module.dt', new=mock_dt)

    yield MocksClassesOnlyCollection(mock_FirstClass, mock_SecondClass,
                                     mock_dt)


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
    mocker.patch('tests.sample.code.tested_module.zipfile', new=mock_zipfile)

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

    yield MocksFunctionsOnlyCollection(mock_add, mock_append_to_cwd,
                                       mock_are_in_same_folder, mock_other_dir,
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
                             mock_other_dir, mock_rm_alias, mock_rm_direct,
                             mock_second_dir, mock_os_remove)


def test_generate_mocks_modules_only():
    generated_mocks = mock_autogen.generator.generate_mocks(
        mock_autogen.generator.MockingFramework.PYTEST_MOCK,
        tests.sample.code.tested_module,
        mock_modules=True,
        mock_functions=False,
        mock_builtin=False,
        mock_classes=False,
        mock_referenced_classes=False,
        mock_classes_static=False,
        prepare_asserts_calls=False)

    assert MOCKED_MODULES_HEADER + MOCKED_MODULES == generated_mocks


def test_generate_mocks_functions_only():
    generated_mocks = mock_autogen.generator.generate_mocks(
        mock_autogen.generator.MockingFramework.PYTEST_MOCK,
        tests.sample.code.tested_module,
        mock_modules=False,
        mock_functions=True,
        mock_builtin=False,
        mock_classes=False,
        mock_referenced_classes=False,
        mock_classes_static=False,
        prepare_asserts_calls=False)

    assert MOCKED_FUNCTIONS_HEADER + MOCKED_FUNCTIONS == generated_mocks


def test_generate_mocks_object_methods_only():
    first = tests.sample.code.tested_module.FirstClass('20')

    generated_mocks_instance = mock_autogen.generator.generate_mocks(
        mock_autogen.generator.MockingFramework.PYTEST_MOCK,
        first,
        name='first',
        mock_modules=False,
        mock_functions=True,
        mock_builtin=False,
        mock_classes=False,
        mock_referenced_classes=False,
        mock_classes_static=False,
        prepare_asserts_calls=False)

    assert MOCKED_METHODS_HEADER + MOCKED_METHODS == generated_mocks_instance


def test_generate_mocks_builtin_only():
    generated_mocks = mock_autogen.generator.generate_mocks(
        mock_autogen.generator.MockingFramework.PYTEST_MOCK,
        tests.sample.code.tested_module,
        mock_modules=False,
        mock_functions=False,
        mock_builtin=True,
        mock_classes=False,
        mock_referenced_classes=False,
        mock_classes_static=False,
        prepare_asserts_calls=False)

    assert MOCKED_FUNCTIONS_HEADER + MOCKED_BUILTIN == generated_mocks


def test_generate_mocks_classes_only():
    generated_mocks = mock_autogen.generator.generate_mocks(
        mock_autogen.generator.MockingFramework.PYTEST_MOCK,
        tests.sample.code.tested_module,
        mock_modules=False,
        mock_functions=False,
        mock_builtin=False,
        mock_classes=True,
        mock_referenced_classes=False,
        mock_classes_static=False,
        prepare_asserts_calls=False)

    assert MOCKED_CLASSES_HEADER + MOCKED_CLASSES == generated_mocks


def test_generate_mocks_referenced_classes_only():
    generated_mocks = mock_autogen.generator.generate_mocks(
        mock_autogen.generator.MockingFramework.PYTEST_MOCK,
        tests.sample.code.tested_module,
        mock_modules=False,
        mock_functions=False,
        mock_builtin=False,
        mock_classes=False,
        mock_referenced_classes=True,
        mock_classes_static=False,
        prepare_asserts_calls=False)

    assert MOCKED_CLASSES_HEADER + MOCKED_REFERENCED_CLASSES == generated_mocks


def test_generate_mocks_classes_static_only():
    generated_mocks = mock_autogen.generator.generate_mocks(
        mock_autogen.generator.MockingFramework.PYTEST_MOCK,
        tests.sample.code.tested_module,
        mock_modules=False,
        mock_functions=False,
        mock_builtin=False,
        mock_classes=True,
        mock_referenced_classes=False,
        mock_classes_static=True,
        prepare_asserts_calls=False)

    assert MOCKED_CLASSES_HEADER + MOCKED_CLASSES_STATIC == generated_mocks


def test_generate_mocks_referenced_classes_static_only():
    generated_mocks = mock_autogen.generator.generate_mocks(
        mock_autogen.generator.MockingFramework.PYTEST_MOCK,
        tests.sample.code.tested_module,
        mock_modules=False,
        mock_functions=False,
        mock_builtin=False,
        mock_classes=False,
        mock_referenced_classes=True,
        mock_classes_static=True,
        prepare_asserts_calls=False)

    assert MOCKED_CLASSES_HEADER + MOCKED_REFERENCED_CLASSES_STATIC \
        == generated_mocks


def test_generate_mocks_prepare_asserts_calls_only():
    generated_mocks = mock_autogen.generator.generate_mocks(
        mock_autogen.generator.MockingFramework.PYTEST_MOCK,
        tests.sample.code.tested_module,
        mock_modules=False,
        mock_functions=False,
        mock_builtin=False,
        mock_classes=False,
        mock_referenced_classes=False,
        mock_classes_static=False,
        prepare_asserts_calls=True)

    assert not generated_mocks


def test_generate_mocks_all():
    generated_mocks = mock_autogen.generator.generate_mocks(
        mock_autogen.generator.MockingFramework.PYTEST_MOCK,
        tests.sample.code.tested_module,
        mock_modules=True,
        mock_functions=True,
        mock_builtin=True,
        mock_classes=True,
        mock_referenced_classes=True,
        mock_classes_static=False,
        prepare_asserts_calls=True)

    assert MOCKED_MODULES_HEADER + MOCKED_MODULES + \
        MOCKED_FUNCTIONS_HEADER + MOCKED_FUNCTIONS + MOCKED_BUILTIN + \
        MOCKED_CLASSES_HEADER + MOCKED_CLASSES + MOCKED_REFERENCED_CLASSES + \
        PREPARE_ASSERTS_CALLS_HEADER + PREPARE_ASSERTS_CALLS_ALL \
        == generated_mocks


def test_generate_mocks_default():
    generated_mocks = mock_autogen.generator.generate_mocks(
        mock_autogen.generator.MockingFramework.PYTEST_MOCK,
        tests.sample.code.tested_module)

    assert MOCKED_MODULES_HEADER + MOCKED_MODULES + \
        MOCKED_FUNCTIONS_HEADER + MOCKED_BUILTIN + \
        MOCKED_CLASSES_HEADER + MOCKED_REFERENCED_CLASSES + \
        PREPARE_ASSERTS_CALLS_HEADER + PREPARE_ASSERTS_CALLS_DEFAULT == generated_mocks


def test_generate_mocks_function():
    generated_mocks_function = mock_autogen.generator.generate_mocks(
        mock_autogen.generator.MockingFramework.PYTEST_MOCK,
        tests.sample.code.tested_module.get_current_time,
        mock_modules=True,
        mock_functions=True,
        mock_builtin=True,
        mock_classes=True,
        mock_referenced_classes=True,
        mock_classes_static=True)

    assert "" == generated_mocks_function  # not supported


def test_generate_asserts_are_in_same_folder_args(mock_everything_collection):
    tests.sample.code.tested_module.are_in_same_folder('/some/path/file1.txt',
                                                       '/some/path/file2.txt')

    mock_are_in_same_folder = mock_everything_collection.are_in_same_folder
    generated = mock_autogen.generator.generate_asserts(
        mock_are_in_same_folder)
    assert 'assert 1 == mock_are_in_same_folder.call_count\n' \
           "mock_are_in_same_folder.assert_called_once_with(" \
           "'/some/path/file1.txt', '/some/path/file2.txt')\n" == generated
    exec(generated)  # verify the validity of assertions


def test_generate_asserts_rename_argument(mock_everything_collection):
    tests.sample.code.tested_module.are_in_same_folder('/some/path/file1.txt',
                                                       '/some/path/file2.txt')

    mock_are_in_same_folder = mock_everything_collection.are_in_same_folder
    generated = mock_autogen.generator.generate_asserts(
        mock_are_in_same_folder, name='my_mock')
    assert 'assert 1 == my_mock.call_count\n' \
           "my_mock.assert_called_once_with(" \
           "'/some/path/file1.txt', '/some/path/file2.txt')\n" == generated


def test_generate_asserts_unable_to_find_argument(mock_everything_collection):
    tests.sample.code.tested_module.are_in_same_folder('/some/path/file1.txt',
                                                       '/some/path/file2.txt')

    generated = mock_autogen.generator.generate_asserts(
        mock_everything_collection.are_in_same_folder)
    assert 'assert 1 == arg.call_count\n' \
           "arg.assert_called_once_with(" \
           "'/some/path/file1.txt', '/some/path/file2.txt')\n" == generated


def test_generate_asserts_mocks_were_not_called(mock_everything_collection):
    for mocked in mock_everything_collection:
        generated = mock_autogen.generator.generate_asserts(mocked)
        assert "mocked.assert_not_called()" == generated
        exec(generated)


def test_generate_asserts_are_in_same_folder_kwargs(
        mock_functions_only_collection):
    tests.sample.code.tested_module.are_in_same_folder(
        path1='/some/path/file1.txt', path2='/some/path/file2.txt')

    mock_are_in_same_folder = mock_functions_only_collection.are_in_same_folder
    generated = mock_autogen.generator.generate_asserts(
        mock_are_in_same_folder)
    assert "assert 1 == mock_are_in_same_folder.call_count\n" \
           "mock_are_in_same_folder.assert_called_once_with(" \
           "path1='/some/path/file1.txt', " \
           "path2='/some/path/file2.txt')\n" == generated
    exec(generated)  # verify the validity of assertions


def test_generate_asserts_are_in_same_folder_mix_args_kwargs(
        mock_everything_collection):
    tests.sample.code.tested_module.are_in_same_folder(
        '/some/path/file1.txt', path2='/some/path/file2.txt')

    mock_are_in_same_folder = mock_everything_collection.are_in_same_folder
    generated = mock_autogen.generator.generate_asserts(
        mock_are_in_same_folder)
    assert "assert 1 == mock_are_in_same_folder.call_count\n" \
           "mock_are_in_same_folder.assert_called_once_with(" \
           "'/some/path/file1.txt', " \
           "path2='/some/path/file2.txt')\n" == generated
    exec(generated)  # verify the validity of assertions


def test_generate_asserts_rm_alias_builtin_only(mock_builtin_only_collection):
    tests.sample.code.tested_module.rm_alias('/some/path/file1.txt')

    mock_os_remove = mock_builtin_only_collection.os_remove
    generated = mock_autogen.generator.generate_asserts(mock_os_remove)
    assert "assert 1 == mock_os_remove.call_count\n" \
           "mock_os_remove.assert_called_once_with('/some/path/file1.txt')\n" \
           == generated
    exec(generated)  # verify the validity of assertions


def test_generate_asserts_append_to_cwd_builtin_only(
        mock_modules_only_collection):
    tests.sample.code.tested_module.append_to_cwd('/some/path/file1.txt')

    mock_os = mock_modules_only_collection.os
    generated = mock_autogen.generator.generate_asserts(mock_os)
    assert re.match(
        r"^mock_os.getcwd.assert_called_once_with\(\)\n"
        r"mock_os.path.join.assert_called_once_with"
        r"\(<MagicMock name='os.getcwd\(\)' id='\d+'>, "
        r"'/some/path/file1.txt'\)\n$", generated)

    # added ANY to match the mock parameter
    from mock import ANY
    mock_os.path.join.assert_called_once_with(ANY, '/some/path/file1.txt')
    mock_os.getcwd.assert_called_once_with()


def test_generate_asserts_append_to_cwd_builtin_only_mocked_cwd(
        mock_modules_only_collection):
    mock_os = mock_modules_only_collection.os

    # added this so the assert can be affective.
    # this is an example of the code the user has to add on top of the utility
    mock_os.getcwd.return_value = '/some/pwd'

    tests.sample.code.tested_module.append_to_cwd('/some/path/file1.txt')

    generated = mock_autogen.generator.generate_asserts(mock_os)
    assert "mock_os.getcwd.assert_called_once_with()\n" \
           "mock_os.path.join.assert_called_once_with" \
           "('/some/pwd', '/some/path/file1.txt')\n" == generated
    exec(generated)  # verify the validity of assertions


def test_generate_asserts_add_mix_types(mock_functions_only_collection):
    tests.sample.code.tested_module.add('one', 2)

    mock_add = mock_functions_only_collection.add
    generated = mock_autogen.generator.generate_asserts(mock_add)
    assert 'assert 1 == mock_add.call_count\n' \
           "mock_add.assert_called_once_with(" \
           "'one', 2)\n" == generated
    exec(generated)  # verify the validity of assertions


def test_generate_asserts_add_multiple_calls(mock_functions_only_collection):
    tests.sample.code.tested_module.add(1, 2)
    tests.sample.code.tested_module.add('one', 'two')

    mock_add = mock_functions_only_collection.add
    generated = mock_autogen.generator.generate_asserts(mock_add)
    assert 'from mock import call\n\n' \
           'assert 2 == mock_add.call_count\n' \
           "mock_add.assert_has_calls(calls=[call(1, 2)," \
           "call('one', 'two'),])\n" == generated
    exec(generated)  # verify the validity of assertions


def test_generate_asserts_context_manager(mock_modules_only_collection):
    tests.sample.code.tested_module.process_and_zip('/path/to.zip',
                                                    'in_zip.txt', 'foo bar')

    mock_zipfile = mock_modules_only_collection.zipfile
    generated = mock_autogen.generator.generate_asserts(mock_zipfile)
    assert "mock_zipfile.ZipFile.assert_called_once_with(" \
           "'/path/to.zip', 'w')\n" \
           "mock_zipfile.ZipFile.return_value.__enter__." \
           "assert_called_once_with()\n" \
           "mock_zipfile.ZipFile.return_value.__enter__." \
           "return_value.writestr.assert_called_once_with(" \
           "'in_zip.txt', 'processed foo bar')\n" \
           "mock_zipfile.ZipFile.return_value.__exit__." \
           "assert_called_once_with(None, None, None)\n" == generated
    exec(generated)  # verify the validity of assertions


def test_generate_asserts_class(mocker):
    # mocked classes
    mock_FirstClass = mocker.MagicMock(
        name='FirstClass', spec=tests.sample.code.tested_module.FirstClass)
    mocker.patch('tests.sample.code.tested_module.FirstClass',
                 new=mock_FirstClass)

    tests.sample.code.tested_module.use_first_class('20')

    generated = mock_autogen.generator.generate_asserts(mock_FirstClass)
    assert "assert 1 == mock_FirstClass.call_count\n" \
           "mock_FirstClass.assert_called_once_with('20')\n" \
           "mock_FirstClass.return_value.not_implemented." \
           "assert_called_once_with(None)\n" == generated
    exec(generated)  # verify the validity of assertions


def test_generate_asserts_non_overridden_repr(mocker):
    # mocked classes
    mock_FirstClass = mocker.MagicMock(
        name='FirstClass', spec=tests.sample.code.tested_module.FirstClass)
    mocker.patch('tests.sample.code.tested_module.FirstClass',
                 new=mock_FirstClass)

    tests.sample.code.tested_module.use_first_class(
        '20', tests.sample.code.tested_module.SecondClass(42))

    generated = mock_autogen.generator.generate_asserts(mock_FirstClass)
    assert re.match(
        r"^assert 1 == mock_FirstClass.call_count\n"
        r"mock_FirstClass.assert_called_once_with\('20'\)\n"
        r"mock_FirstClass.return_value.not_implemented."
        r"assert_called_once_with\(_tests.sample.code.tested_module."
        r"SecondClass_object_at_0x[0-9A-Fa-f]+_\)\n$", generated)


def test_generate_asserts_class_static(mocker):
    # mocked classes
    class MockedSecondClassMeta(type):
        static_instance = mocker.MagicMock(
            spec=tests.sample.code.tested_module.SecondClass)

        def __getattr__(cls, key):
            return MockedSecondClassMeta.static_instance.__getattr__(key)

    class MockedSecondClass(metaclass=MockedSecondClassMeta):
        original_cls = tests.sample.code.tested_module.SecondClass
        instances = []

        def __new__(cls, *args, **kwargs):
            MockedSecondClass.instances.append(
                mocker.MagicMock(spec=MockedSecondClass.original_cls))
            MockedSecondClass.instances[-1].__class__ = MockedSecondClass
            return MockedSecondClass.instances[-1]

    mocker.patch('tests.sample.code.tested_module.SecondClass',
                 new=MockedSecondClass)

    tests.sample.code.tested_module.use_second_class_static('20')

    assert 1 == len(MockedSecondClass.instances)

    generated_static = mock_autogen.generator.generate_asserts(
        MockedSecondClassMeta.static_instance,
        name="MockedSecondClassMeta.static_instance")
    assert re.match(
        r"^MockedSecondClassMeta.static_instance.prop.__eq__."
        r"assert_called_once_with\(<MagicMock "
        r"name='mock.prop' id='\d+'>\)\n$", generated_static)

    generated_instance = mock_autogen.generator.generate_asserts(
        MockedSecondClass.instances[0], name="MockedSecondClass.instances[0]")
    assert re.match(
        r"^MockedSecondClass.instances\[0\].not_implemented."
        r"assert_called_once_with\(\)\n"
        r"MockedSecondClass.instances\[0\].prop.__eq__."
        r"assert_called_once_with\("
        r"<MagicMock name='mock.prop' id='\d+'>\)\n$", generated_instance)


def test_class_static_objects_behave_the_same(mocker):
    # mocked classes
    class MockedSecondClassMeta(type):
        static_instance = mocker.MagicMock(
            spec=tests.sample.code.tested_module.SecondClass)

        def __getattr__(cls, key):
            return MockedSecondClassMeta.static_instance.__getattr__(key)

    class MockedSecondClass(metaclass=MockedSecondClassMeta):
        original_cls = tests.sample.code.tested_module.SecondClass
        instances = []

        def __new__(cls, *args, **kwargs):
            MockedSecondClass.instances.append(
                mocker.MagicMock(spec=MockedSecondClass.original_cls))
            MockedSecondClass.instances[-1].__class__ = MockedSecondClass
            return MockedSecondClass.instances[-1]

    mocker.patch('tests.sample.code.tested_module.SecondClass',
                 new=MockedSecondClass)

    second = tests.sample.code.tested_module.SecondClass('20')
    second.not_implemented()

    with pytest.raises(AttributeError):
        second.unknown_method()

    assert isinstance(second, tests.sample.code.tested_module.SecondClass)


def test_referenced_class(mock_classes_only_collection):
    mock_classes_only_collection.datetime.utcnow.return_value = 20
    current_time = tests.sample.code.tested_module.get_current_time()
    assert 20 == current_time


def test_mock_object_instance(mocker):
    first = tests.sample.code.tested_module.FirstClass('20')
    exec(MOCKED_METHODS)  # mocks all the methods

    first.not_implemented()  # would have raised exception otherwise
    first.not_implemented.assert_called_once_with()


def test_mock_object_class_direct(mocker):
    first_class = tests.sample.code.tested_module.FirstClass

    generated_mocks_class = mock_autogen.generator.generate_mocks(
        mock_autogen.generator.MockingFramework.PYTEST_MOCK,
        first_class,
        name='first_class',
        mock_modules=False,
        mock_functions=True,
        mock_builtin=False,
        mock_classes=False,
        mock_referenced_classes=False,
        mock_classes_static=False)
    exec(generated_mocks_class)

    first_class_instance = first_class(42)
    first_class_instance.not_implemented('some param')
    first_class_instance.not_implemented.assert_called_once_with('some param')


def test_mock_object_class_indirect(mocker):
    first_class = tests.sample.code.tested_module.FirstClass

    generated_mocks_class = mock_autogen.generator.generate_mocks(
        mock_autogen.generator.MockingFramework.PYTEST_MOCK,
        first_class,
        name='first_class',
        mock_modules=False,
        mock_functions=True,
        mock_builtin=False,
        mock_classes=False,
        mock_referenced_classes=False,
        mock_classes_static=False)
    exec(generated_mocks_class)

    first_class_instance = tests.sample.code.tested_module.FirstClass(42)
    first_class_instance.not_implemented('some param')
    first_class_instance.not_implemented.assert_called_once_with('some param')


@pytest.mark.parametrize('static', [True, False])
def test_generate_mocks_mocked_class_equals_to_module(static):
    module = tests.sample.code.second_module
    single_class = module.SingleClassInModule

    generated_mocks_module = mock_autogen.generator.generate_mocks(
        mock_autogen.generator.MockingFramework.PYTEST_MOCK,
        module,
        name='some_name',
        mock_modules=False,
        mock_functions=False,
        mock_builtin=False,
        mock_classes=True,
        mock_referenced_classes=False,
        mock_classes_static=static)

    generated_mocks_class = mock_autogen.generator.generate_mocks(
        mock_autogen.generator.MockingFramework.PYTEST_MOCK,
        single_class,
        name='some_name',
        mock_modules=False,
        mock_functions=False,
        mock_builtin=False,
        mock_classes=True,
        mock_referenced_classes=False,
        mock_classes_static=static)

    assert generated_mocks_module == generated_mocks_class


def test_generate_mocks_invalid_framework():
    with pytest.raises(ValueError):
        mock_autogen.generator.generate_mocks('unittest', tests.sample.code)


def test_generate_asserts_invalid_object():
    with pytest.raises(TypeError):
        mock_autogen.generator.generate_asserts('not a mock')
