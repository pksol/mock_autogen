import math
import random


def list_subscript_games(items):
    items[math.sqrt(9)] = -1
    items[1:4] = random.randint(0, 10) or str(20)
