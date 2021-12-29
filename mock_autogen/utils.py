import ast
import functools
import logging
import sys

import pyperclip

logger = logging.getLogger(__name__)


def copy_result_to_clipboard(func):
    """
    Copies the result of the decorated function to the clipboard.

    Args:
        func (callable): the original function

    Returns:
        callable: the decorated function whose output would go to the clipboard
    """

    @functools.wraps(func)
    def to_clipboard(*args, **kwargs):
        result = func(*args, **kwargs)
        try:
            pyperclip.copy(result)
        except Exception:
            logger.warning("Could not copy func results to clipboard",
                           exc_info=True)
        return result

    return to_clipboard


def print_result(func):
    """
    Prints the result of the decorated function to the console.

    Args:
        func (callable): the original function

    Returns:
        callable: the decorated function whose output would go to the console
    """

    @functools.wraps(func)
    def to_console(*args, **kwargs):
        result = func(*args, **kwargs)
        print(str(result))
        return result

    return to_console


def get_unique_item(items: set, item: str) -> str:
    """
    Returns an item which is not in the set. The basic item name is sent as a parameter and
    the returned item may be of the form 'item_#', where number is the first available.

    The new item is added to the set to ensure two subsequent calls return different items.

    Args:
        items: the current set of items
        item: the item to add

    Returns:
        The first item available, possibly in the form of 'item_#'.
    """
    sequence = 1
    compound_item = item
    while compound_item in items:
        sequence += 1
        compound_item = item + f'_{sequence}'
    items.add(compound_item)
    return compound_item
