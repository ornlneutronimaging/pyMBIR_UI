import glob
import os
from pathlib import Path
import ntpath


def get_list_files(directory="./", file_extension="*.fits"):
    """
    return the list of files in the directory specified according to the instrument used
    """
    list_files = glob.glob(os.path.join(directory, file_extension))
    return list_files


def get_short_filename(full_filename=""):
    return str(Path(full_filename).stem)


def read_ascii(filename=''):
    '''return contain of an ascii file'''
    with open(filename, 'r') as f:
        text = f.read()
    return text


def write_ascii(text="", filename=''):
    with open(filename, 'w') as f:
        f.write(text)


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)
