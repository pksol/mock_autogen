import math
import os


def get_square_root(items):
    square = [math.sqrt(x) for x in items]
    return square


def get_square_root_loop(items):
    square = []
    for x in items:
        square.append(math.sqrt(x))
    return square


external_items = [1, 4, 9]


def get_square_root_external_variable():
    square = [math.sqrt(x) for x in external_items]
    return square


def get_square_root_loop_external_variable():
    square = []
    for x in external_items:
        square.append(math.sqrt(x))
    return square


def summarize_environ_values():
    return {k: len(v) for k, v in os.environ.items()}


def summarize_environ_values_loop():
    summary = {}
    for k, v in os.environ.items():
        summary[k] = len(v)
    return summary


def trimmed_strings(items):
    return {x.strip(): len(x) for x in items}


def trimmed_strings_loop(items):
    trimmed = {}
    for x in items:
        trimmed[x.strip()] = len(x)
    return trimmed
