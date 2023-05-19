import os

import cv2
import numpy as np

import utils

FOCAL_LENGTH = 370000     # Empirical: based on OpenCV calibration
SHAPE = (3120, 4208, 3)   # Max camera resolution
INTRINSIC_MATRIX = np.array([[FOCAL_LENGTH, 0, SHAPE[1] // 2 - 800],
                             [0, FOCAL_LENGTH, SHAPE[0] // 2 - 500],
                             [0,            0,             1]])

EXTRINSIC_PARAMETERS = np.array([1, 0, 0, -.1])  # About .3 of eye fish and -.005 of perspective distortion.


class Calibration:
    def __init__(self):
        self.points = []
        self.pattern_sizes = []
        self.images = []
        self.image_size = ()

        # Calibration parameters
        self.dist_coeffs = EXTRINSIC_PARAMETERS
        self.camera_matrix = INTRINSIC_MATRIX

    def add_points(self, image, pattern_size=(55, 37), window_size=25) -> bool:
        image = utils.open_image(image)
        points = get_checker(image, pattern_size, window_size)
        if not len(points):
            return False
        self.points.append(points)
        self.pattern_sizes.append(pattern_size)
        self.image_size = image.shape[:2]
        self.images.append(image)
        return True

    def calibrate(self, side=1):
        if not self.points:
            return None, self.camera_matrix, self.dist_coeffs, None, None
        points3d = []
        for pattern_size in self.pattern_sizes:
            p3d = np.array([[(j*side, i*side, 0) for j in range(pattern_size[1])] for i in range(pattern_size[0])], np.float32)
            points3d.append(p3d.reshape(-1, 3))
        params = cv2.calibrateCamera(points3d, self.points, self.image_size, INTRINSIC_MATRIX,
                                     EXTRINSIC_PARAMETERS, flags=cv2.CALIB_USE_INTRINSIC_GUESS)
        retval, self.camera_matrix, self.dist_coeffs, rvecs, tvecs = params
        return retval, self.camera_matrix, self.dist_coeffs, rvecs, tvecs

    def undistort(self, image) -> np.ndarray:
        return cv2.undistort(utils.open_image(image), self.camera_matrix, self.dist_coeffs)

    def __str__(self):
        camera_matrix = str(self.camera_matrix.tolist()).replace("], ", "],\n" + " " * 18)
        dist_coeffs = str(self.dist_coeffs.squeeze().tolist())
        return f'{{\n"camera_matrix": {camera_matrix},\n"distortion_coefficients": {dist_coeffs}\n}}\n'


def get_checker(image, pattern_size=(53, 35), window_size=25) -> np.ndarray:
    image = utils.open_image(image)
    if image is None:
        return np.array([])

    for x_size in [360, 480, 720, 1080, image.shape[0]]:
        y_size = int(x_size * image.shape[1] / image.shape[0])
        success, points = cv2.findChessboardCorners(cv2.resize(image, (x_size, y_size)), pattern_size)
        if success:
            break

    if not success or points is None:
        return np.array([])

    # Resize the points to the window size
    points = np.array(points)
    points[..., 0] = points[..., 0] * image.shape[1] / x_size
    points[..., 1] = points[..., 1] * image.shape[0] / y_size

    points = cv2.cornerSubPix(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY),
                              points,
                              window_size if isinstance(window_size, tuple) else (window_size, window_size),
                              (-1, -1),
                              (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 500, 0.0001))
    return points


def equidistant(image, pattern_size=(53, 35), pixels_per_mm=12.32):
    """Compares the distances between the points in the image and in the ideal pattern."""
    points = get_checker(image, pattern_size[::-1])
    if points is None or not len(points):
        return None

    points = points.reshape(*pattern_size, -1)
    ideal = np.array([[(i, j) for j in range(pattern_size[1])] for i in range(pattern_size[0])])

    # Fix the extremes of one diagonal and compare the paterns.
    distances = np.linalg.norm(points - points[0, 0], axis=2)
    ideal_distances = np.linalg.norm(ideal - ideal[0, 0], axis=2)
    ideal_distances *= distances[-1, -1] / ideal_distances[-1, -1]
    one = abs(distances - ideal_distances)

    # Fix the extremes of the other diagonal and compare the paterns.
    distances = np.linalg.norm(points - points[-1, 0], axis=2)
    ideal_distances = np.linalg.norm(ideal - ideal[-1, 0], axis=2)
    ideal_distances *= distances[0, -1] / ideal_distances[0, -1]
    two = abs(distances - ideal_distances)

    return np.mean([one, two]) / pixels_per_mm


def calibrate_folder(path=r'\\10.10.204.24\scan4d\TENDER\HANDS_SIN_CALIBRAR/',
                     dest=r'\\10.10.204.24\scan4d\TENDER\HANDS_CALIBRADAS/'):
    dest = dest or path
    files = [f for f in os.listdir(path) if f.endswith('.png') and 'undistorted' not in f]
    calibration = Calibration()
    for file in utils.bar(files):
        undistorted = calibration.undistort(cv2.imread(os.path.join(path, file)))
        cv2.imwrite(os.path.join(dest, file[:-13] + '.undistorted' + file[-13:]), undistorted)
