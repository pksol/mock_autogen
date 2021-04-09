from datetime import datetime as dt
import random
import os
from os import remove as os_remove

from tests.sample.code import second_module
from tests.sample.code.second_module import my_dir as other_dir

import zipfile


def os_remove_wrap(filename):
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


global_counter = 1


class FirstClass(object):
    prop = 1

    def __init__(self, prop):
        self.prop = prop

    def not_implemented(self, param):
        raise NotImplementedError()

    def using_not_implemented(self):
        # call an already imported module and existing function in the module
        seed = random.randint(0, 10) + get_random_number()
        suffix: str = str(seed)  # call builtin
        suffix += str(os.path.isfile(suffix))  # call nested function

        # bin op, unsupported
        # also, ignore all variable method calls
        message_bytes = (suffix.upper() + suffix).encode('ascii')

        # inner import without alias
        import base64
        encoded = base64.b64encode(message_bytes)

        # inner import with alias
        import base64 as b64
        decoded_bytes = b64.b64decode(encoded)

        ret = decoded_bytes.decode('ascii')

        # this is unique to this method case
        FirstClass.increase_global_counter()
        FirstClass.increase_class_counter()
        self.not_implemented(get_random_number())

        return ret

    @classmethod
    def increase_class_counter(cls):
        cls.prop = get_random_number()
        cls.increase_global_counter()

    @staticmethod
    def increase_global_counter():
        global global_counter
        global_counter = get_random_number()


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


def get_random_number():
    return random.randint(0, 1000000)


def base_64_whole_modules(message):
    # call an already imported module and existing function in the module
    seed = random.randint(0, 10) + get_random_number()
    suffix: str = str(seed)  # call builtin
    suffix += str(os.path.isfile(suffix))  # call nested function

    # bin op, unsupported
    # also, ignore all variable method calls
    message_bytes = (message.upper() + suffix). \
        encode('ascii')

    # inner import without alias
    import base64
    encoded = base64.b64encode(message_bytes)

    # inner import with alias
    import base64 as b64
    decoded_bytes = b64.b64decode(encoded)

    return decoded_bytes.decode('ascii')


def base_64_partial_functions(message):
    # call an already imported module and existing function in the module
    seed = random.randint(0, 10) + get_random_number()
    suffix: str = str(seed)  # call builtin
    suffix += str(os.path.isfile(suffix))  # call nested function

    # bin op, unsupported
    # also, ignore all variable method calls
    message_bytes = (message.upper() + suffix). \
        encode('ascii')

    # inner import of functions with and without alias
    from base64 import b64encode as enc, b64decode
    encoded = enc(message_bytes)
    decoded_bytes = b64decode(encoded)

    return decoded_bytes.decode('ascii')
