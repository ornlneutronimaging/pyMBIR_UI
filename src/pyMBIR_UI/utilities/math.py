import numpy as np


def is_value_int(value=None):
    try:
        _ = np.int(str(value))
        return True
    except ValueError:
        return False
