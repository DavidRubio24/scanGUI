import os.path
import cv2
import numpy as np


def chose_name(name, path='./'):
    """
    Chose a name for a file that doesn't already exist.
    If the name has an extension with digits they will be increased.
    """
    new_name = os.path.join(path, name)
    # Until we generate a new name
    while os.path.isfile(new_name):
        # Increase the digits
        new_name = os.path.join(path, increase_name(name))
    return new_name


def increase_name(name):
    """Increase the digits in a name."""
    # Increase the least significant digit within the name
    for i in range(len(name) - 1, -2, -1):
        if i == -1:
            # There is no digit in the name that can be increased
            name = '1' + name
            break
        if name[i] in '012345678':
            # Increase the digit and we are done
            name = name[:i] + str(int(name[i]) + 1) + name[i + 1:]
            break
        elif name[i] == '9':
            # We still have to increase the next digit
            name = name[:i] + '0' + name[i + 1:]
    return name


def open_image(image, copy=True):
    """Takes care of opening an image in various formats: np.ndarray, path, VideoCapture."""
    if isinstance(image, cv2.VideoCapture):
        return image.read()[1]
    elif isinstance(image, np.ndarray):
        return image.copy() if copy else image
    elif isinstance(image, str):
        return cv2.imread(image)
    else:
        raise TypeError("Unsupported image type.")

