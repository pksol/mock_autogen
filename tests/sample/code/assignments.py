# todo: https://greentreesnakes.readthedocs.io/en/latest/nodes.html#Starred


def split_list(items):
    first, *others = items
    print(first.strip())
    for other in others:
        print(other.lstrip())
