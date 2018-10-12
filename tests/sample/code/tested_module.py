from datetime import datetime as dt
import os
from os import remove as os_remove

from tests.sample.code import second_module
from tests.sample.code.second_module import my_dir as other_dir

import zipfile


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


def process_and_zip(zip_path, file_name, contents):
    processed_contents = "processed " + contents  # some complex logic
    with zipfile.ZipFile(zip_path, 'w') as zip_container:
        zip_container.writestr(file_name, processed_contents)


class FirstClass(object):
    prop = 1

    def __init__(self, prop):
        self.prop = prop

    def not_implemented(self, param):
        raise NotImplementedError()


class SecondClass(object):
    prop = 2

    def __init__(self, prop):
        self.prop = prop

    def not_implemented(self):
        raise NotImplementedError()


def use_first_class(prop, opt_param=None):
    FirstClass(prop).not_implemented(opt_param)


def use_second_class_static(prop):
    instance = SecondClass(prop)
    instance.not_implemented()
    return SecondClass.prop == instance.prop


def get_current_time():
    return dt.utcnow()
