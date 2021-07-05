import pyperclip

from mock_autogen.utils import print_result, copy_result_to_clipboard, \
    get_unique_item


@copy_result_to_clipboard
@print_result
def my_simple_func(param):
    return param + param


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
