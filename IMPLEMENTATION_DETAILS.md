## Image rotation, flip and BGR to RGB rotation.
Both numpy and openCV offer ways to rotate and convert the image.

Numpy rotation: `image.transpose(1, 0, 2)[::-1]`
Numpy flip: `image[:, ::-1]`
NumPy BGR to RGB: `image[..., ::-1]`

OpenCV's rotation: `cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)`
OpenCV's flip: `cv2.flip(image, 1)`
OpenCV BGR to RGB: `cv2.cvtColor(image, cv2.COLOR_BGR2RGB)`

After that, the image has to be converted to PIL.
Here's the time it takes to do each convination of opertaions
(since Numpy transfomations only change the metadata, they have to be tested jointly):

| fps     | 5.3 | 5.9 | 5  | 5.2 | *13* | 11.8 | 6  | 5.6 |
|---------|-----|-----|----|-----|------|------|----|-----|
| rotate  | np  | np  | np | np  | cv   | cv   | cv | cv  |
| flip    | np  | np  | cv | cv  | cv   | cv   | np | np  |
| convert | np  | cv  | np | cv  | cv   | np   | cv | np  |

So we use exclusively openCV for those transformations.

## Saving format
Saving the image to .png takes a full second. Saving a .bmp takes a 0.2 s.
We'll save them to .png in another thread.


# VideoCapture properties change
The camera is very slow, so it makes it hard to capture correct images.
But we need to use the UYVY fourcc codec with the maximum resolution possible.
One idea is preview in a lower resolution and capture in a higher one.
But the test camera was unable to use the MPEG, JPEG or MJPG fourcc codecs and a change in resolution made the camera stop working.

In the end, connecting the camera to a real USB 3.0 port made it work reasonably fast.
The left side USB 3.0 port of our laptop only works as 3.0 with an adapter. ¯\_(ツ)_/¯
