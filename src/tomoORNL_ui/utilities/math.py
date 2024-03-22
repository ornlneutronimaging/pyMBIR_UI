import numpy as np


def is_value_int(value=None):
    try:
        _ = int(str(value))
        return True
    except ValueError:
        return False
