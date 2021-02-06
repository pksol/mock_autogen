"""
This test module verifies the public API and the validity of the documentation
by using the same code snippets.
"""

import mock_autogen
import tests
from mock_autogen import PytestMocker

from tests.sample.code.tested_module import os_remove_wrap, process_and_zip
from tests.test_generator import MOCKED_CLASSES_HEADER, MOCKED_CLASSES_STATIC, \
    MOCKED_REFERENCED_CLASSES_STATIC, MOCKED_MODULES, MOCKED_MODULES_HEADER, \
    MOCKED_FUNCTIONS_HEADER, MOCKED_FUNCTIONS, MOCKED_BUILTIN, \
    PREPARE_ASSERTS_CALLS_HEADER, PREPARE_ASSERTS_CALLS_ALL, \
    _extract_warnings_generated_mocks_and_generated_asserts
from tests.test_utils import safe_assert_clipboard


def test_generate_uut_mocks_simple(mocker, capsys):
    expected = """# mocked functions
mock_remove = mocker.MagicMock(name='remove')
mocker.patch('tests.sample.code.tested_module.os.remove', new=mock_remove)
"""

    # Arrange
    generated = mock_autogen.generate_uut_mocks(os_remove_wrap)
    exec(generated)  # verify the validity of generated mocks code

    # Act
    os_remove_wrap('some/non/existing/path')  # this fails if not mocked

    # Assert
    assert expected == generated

    # verify additional side affects like print to console and clipboard
    assert generated in capsys.readouterr().out
    safe_assert_clipboard(generated)


def test_generate_uut_mocks_complex(mocker, capsys):
    expected = """# mocked functions
mock_ZipFile = mocker.MagicMock(name='ZipFile')
mocker.patch('tests.sample.code.tested_module.zipfile.ZipFile', new=mock_ZipFile)
"""

    # Arrange
    generated = mock_autogen.generate_uut_mocks(process_and_zip)
    exec(generated)  # verify the validity of generated mocks code

    # Act
    process_and_zip(
        '',  # this fails if not mocked - path can't be empty
        'in_zip.txt',
        'foo bar')

    # Assert
    assert expected == generated

    # verify additional side affects like print to console and clipboard
    assert generated in capsys.readouterr().out
    safe_assert_clipboard(generated)


def test_generate_asserts_simple(mocker, capsys):
    # Arrange
    mock_something = mocker.MagicMock(name='something')

    # Act
    mock_something.call_something()

    # Assert
    generated_wo_name = mock_autogen.generate_asserts(mock_something)
    generated_with_name = mock_autogen.generate_asserts(mock_something,
                                                        name='mock_something')

    expected = "mock_something.call_something.assert_called_once_with()"
    assert expected == generated_wo_name.rstrip()
    assert generated_wo_name == generated_with_name

    # verify additional side affects like print to console and clipboard
    assert expected in capsys.readouterr().out
    safe_assert_clipboard(expected)

    exec(generated_wo_name)  # verify the validity of generated assertions code


def test_generate_asserts_complex(mocker, capsys):
    # Arrange
    # mocked functions
    mock_ZipFile = mocker.MagicMock(name='ZipFile')
    mocker.patch('tests.sample.code.tested_module.zipfile.ZipFile',
                 new=mock_ZipFile)

    # Act
    process_and_zip(
        '',  # this fails if not mocked - path can't be empty
        'in_zip.txt',
        'foo bar')
    # Assert
    generated_wo_name = mock_autogen.generate_asserts(mock_ZipFile)
    generated_with_name = mock_autogen.generate_asserts(mock_ZipFile,
                                                        name='mock_ZipFile')
    expected = """assert 1 == mock_ZipFile.call_count
mock_ZipFile.assert_called_once_with('', 'w')
mock_ZipFile.return_value.__enter__.assert_called_once_with()
mock_ZipFile.return_value.__enter__.return_value.writestr.assert_called_once_with('in_zip.txt', 'processed foo bar')
mock_ZipFile.return_value.__exit__.assert_called_once_with(None, None, None)"""
    assert expected == generated_wo_name.rstrip()
    assert generated_wo_name == generated_with_name

    # verify additional side affects like print to console and clipboard
    assert expected in capsys.readouterr().out
    safe_assert_clipboard(generated_with_name)

    exec(generated_wo_name)  # verify the validity of generated assertions code


def test_generate_uut_mocks_with_asserts_simple(mocker, capsys):
    expected = """# mocked functions
mock_remove = mocker.MagicMock(name='remove')
mocker.patch('tests.sample.code.tested_module.os.remove', new=mock_remove)
# calls to generate_asserts, put this after the 'act'
import mock_autogen
mock_autogen.generate_asserts(mock_remove, name='mock_remove')
"""

    # Arrange
    generated = mock_autogen.generate_uut_mocks_with_asserts(os_remove_wrap)
    exec(generated)  # verify the validity of generated mocks & asserts code

    assert "mock_remove.assert_not_called()" in capsys.readouterr().out

    # Act
    os_remove_wrap('some/non/existing/path')  # this fails if not mocked

    # Assert
    assert expected == generated

    generated_warnings, generated_mocks, generated_asserts = \
        _extract_warnings_generated_mocks_and_generated_asserts(generated)

    # verify the validity of generated asserts code
    exec("\n".join(generated_asserts))
    assert "mock_remove.assert_called_once_with('some/non/existing/path')" \
           in capsys.readouterr().out


def test_mock_everything(mocker, capsys):
    all_but_class_asserts = "\n".join(
        PREPARE_ASSERTS_CALLS_ALL.splitlines()[:-3])
    expected = MOCKED_MODULES_HEADER + MOCKED_MODULES + \
               MOCKED_FUNCTIONS_HEADER + MOCKED_FUNCTIONS + MOCKED_BUILTIN + \
               MOCKED_CLASSES_HEADER + MOCKED_CLASSES_STATIC + \
               MOCKED_REFERENCED_CLASSES_STATIC + \
               PREPARE_ASSERTS_CALLS_HEADER + all_but_class_asserts

    # Arrange
    generated = PytestMocker(
        tests.sample.code.tested_module).mock_everything().generate()

    # Assert
    assert expected.rstrip() == generated.rstrip()

    # verify additional side affects like print to console and clipboard
    assert generated in capsys.readouterr().out
    safe_assert_clipboard(generated)
