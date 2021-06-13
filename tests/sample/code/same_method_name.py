import os


def get():
    return "some_username"


def get_username_and_password():
    username = get()
    password = os.environ.get("password", "some_password")
    return username + "," + password
