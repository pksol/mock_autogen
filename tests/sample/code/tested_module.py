import os
from os import remove as os_remove

from tests.sample.code import second_module
from tests.sample.code.second_module import my_dir as other_dir


def rm_direct(filename):
    os.remove(filename)


def rm_alias(filename):
    os_remove(filename)


def append_to_cwd(path):
    return os.path.join(os.getcwd(), path)


def are_in_same_folder(path1, path2):
    return os.path.dirname(path1) == os.path.dirname(path2)


def second_dir(obj):
    dir1 = second_module.my_dir(obj)
    dir2 = other_dir(obj)
    return dir1 + dir2


def add(one, two):
    return one + two
