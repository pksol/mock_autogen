def my_dir(obj):
    return dir(obj)


class SingleClassInModule(object):
    def __init__(self, prop):
        raise NotImplementedError()

    def not_implemented(self, param):
        raise NotImplementedError()
