import math
import os


def get_square_root(items):
    square = [math.sqrt(x) for x in items]
    return square


def summarize_environ_values():
    return {k: len(v) for k, v in os.environ.items()}


# todo: https://greentreesnakes.readthedocs.io/en/latest/nodes.html#For
def trimmed_strings(items):
    return {x.strip(): len(x) for x in items}
