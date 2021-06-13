import sys

import pyperclip
from unittest.mock import sentinel

from mock_autogen.utils import print_result, copy_result_to_clipboard, \
    safe_travels, get_unique_item


@copy_result_to_clipboard
@print_result
def my_simple_func(param):
    return param + param


warnings = []
source_code = "my = python.code"


@safe_travels(warnings, "a dummy method that might fail", source_code)
def node_visit_func(self, node):
    node.made_up_function()


def safe_assert_clipboard(expected):
    """
    Asserts that the clipboard contains the expected string.

    If the clipboard is not available, ignores this test. This can happen on
    some Linux systems like the GitHub Action runners.

    Args:
        expected (str): the expected string that the clipboard should contain

    Raises:
        AssertionError: when the content of the clipboard does not match the
        expected
    """
    clipboard = None
    try:
        clipboard = "\n".join(pyperclip.paste().splitlines())
    except pyperclip.PyperclipException as e:
        pass
    if clipboard:
        cleaned_expected = "\n".join(expected.splitlines())
        assert cleaned_expected == clipboard


def test_print_result_and_copy_result_to_clipboard(capsys):
    generated = my_simple_func("20")
    assert "2020" == generated

    # verify additional side affects like print to console and clipboard
    assert generated in capsys.readouterr().out
    safe_assert_clipboard(generated)


def test_safe_travels_on_func_success(mocker):
    self = mocker.MagicMock(name='self')
    node = mocker.MagicMock(name='node')

    node_visit_func(self, node)

    node.made_up_function.assert_called_once_with()
    self.generic_visit.assert_called_once_with(node)


def test_safe_travels_on_func_failure(mocker):
    # arrange
    global warnings
    warnings.clear()
    mock_dump = mocker.MagicMock(name='dump')
    mock_dump.return_value = "code_dump"
    mocker.patch('mock_autogen.utils.ast.dump', new=mock_dump)
    mock_get_source_segment = mocker.MagicMock(name='get_source_segment')
    mock_get_source_segment.return_value = "code_actual"
    if sys.version_info >= (3, 8):
        mocker.patch('mock_autogen.utils.ast.get_source_segment',
                     new=mock_get_source_segment)
    mock_warning = mocker.MagicMock(name='warning')
    mocker.patch('mock_autogen.utils.logger.warning', new=mock_warning)
    self = mocker.MagicMock(name='self')

    # act
    node_visit_func(self, sentinel.node)

    # assert
    self.generic_visit.assert_called_once_with(sentinel.node)

    mock_dump.assert_called_once_with(sentinel.node)

    if sys.version_info >= (3, 8):
        mock_get_source_segment.assert_called_once_with(
            'my = python.code', sentinel.node)
        warning = '# could not a dummy method that might fail on node:\n' \
                  '#  code_actual'
    else:
        mock_get_source_segment.assert_not_called()
        warning = '# could not a dummy method that might fail on node:\n' \
                  '#  code_dump'
    mock_warning.assert_called_once_with(warning, exc_info=True)
    assert warning in warnings


def test_get_unique_item_empty_set():
    items = set()
    assert 'a' == get_unique_item(items, 'a')
    assert 'a' in items


def test_get_unique_item_unique():
    items = set('b')
    assert 'a' == get_unique_item(items, 'a')
    assert 'a' in items
    assert len(items) == 2


def test_get_unique_item_exist():
    items = set('a')
    assert 'a_2' == get_unique_item(items, 'a')
    assert 'a' in items
    assert 'a_2' in items
    assert len(items) == 2


def test_get_unique_item_exist_multiple():
    items = set(['a', 'a_2', 'b'])
    assert 'a_3' == get_unique_item(items, 'a')
    assert 'a' in items
    assert 'a_2' in items
    assert 'a_3' in items
    assert 'b' in items
    assert len(items) == 4
