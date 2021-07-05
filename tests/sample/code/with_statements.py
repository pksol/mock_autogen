import pathlib
import threading


def simple_anonymous_context():
    with open("hello.txt", mode="r"):
        print("File exists!")


def simple_context():
    with open("hello.txt", mode="r") as file:
        print(file.read())


single_thread_dict = {}
lock = threading.Lock()


def outside_lock_context(key, value):
    with lock:
        if key not in single_thread_dict:
            single_thread_dict[key] = value
        return single_thread_dict[key]


def inside_lock_context(key, value):
    inner_lock = threading.Lock()  # yes, this doesn't makes sense
    with inner_lock:
        if key not in single_thread_dict:
            single_thread_dict[key] = value


def multiple_contexts_same_method():
    with lock:
        with open("input.txt") as read, open("output.txt", "w") as write:
            content = read.read()
            write.write(content)


def multiple_contexts_different_methods():
    with lock, pathlib.Path("input.txt").open("r") as read, open(
            "output.txt", "w") as write:
        content = read.read()
        write.write(content)
