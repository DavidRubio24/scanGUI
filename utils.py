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


class bar:
    def __init__(self, *iterable, append='', length=False, bar_size=100):
        """Inputs the same arguments as range or an iterable object."""
        if not iterable: raise ValueError()
        iterable = range(*iterable) if isinstance(iterable[0], int) else iterable[0]
        self.iterable, self.append, self.start, self.len, self.i, self.r, self.bar_size = iter(iterable), append, False, length if length else len(iterable), 0, None, bar_size

    def __iter__(self): return self

    def __next__(self):
        from time import monotonic
        now = monotonic()
        self.start = self.start or now
        took = int(now - self.start)
        if self.i >= self.len:
            print(f"\r{self.i: >6}/{self.len:<} (100%) \x1B[0;34m[\x1B[0;32m{'■' * self.bar_size}\x1B[0;34m]\x1B[0m  Took:" + (f'{took // 60: 3}m' if took >= 60 else '    ') + f'{took % 60:3}s  ' + self.append.format(self.r, self.i))
        self.r = next(self.iterable)
        eta = int((self.len - self.i) * (now - self.start) / self.i) if self.i else 0
        done = self.bar_size * self.i / self.len
        print('\r' + f"{self.i: 6}/{self.len:<} ({int(100 * self.i / self.len): 3}%) [\x1B[0;32m{{:·<{self.bar_size + 4}}}]  ".format('■' * int(done) + str(int(10 * (done % 1))) + '\x1B[0m')
              + ('ETA:' + (f'{eta // 60: 4}m' if eta >= 60 else '     ') + f'{eta % 60:3}s  ' if eta else '  ') + self.append.format(self.r, self.i), end='')
        self.i += 1
        return self.r
