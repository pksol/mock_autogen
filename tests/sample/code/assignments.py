import random


def multiple_assignments():
    r1, r2 = random.randint(0, 10), random.randint(0, 10)
    assert r1 + r2.wont_work()
    a = split_list([1, 2, 4])
    c = b = [1]
    b.append(2)
    c.append("3")
    d, e, f = c
    a.append(d)
    len(f.strip())
    x, y = "something", "else"
    len(x.lstrip())
    len(y.rstrip())


def split_list(items):
    first, *others = items
    print(first.strip())
    for other in others:
        print(other.lstrip())
    print(others.count())
    return items


def annotated_assignments():
    r1: int
    r2: int
    r1, r2 = random.randint(0, 10), random.randint(0, 10)
    assert r1 + r2.wont_work()
    a: list = split_list([1, 2, 4])
    c: list
    b: list
    b, c = [1], [2]
    b.append(2)
    c.append("3")
    d, e, f = c
    a.append(d)
    len(f.strip())
    suffix: str = str("seed")
    len(suffix.strip())
