## Image rotation, flip and BGR to RGB rotation.
Both numpy and openCV offer ways to rotate and convert the image.

Numpy rotation: `image.transpose(1, 0, 2)[::-1]`
Numpy flip: `image[:, ::-1]`
NumPy BGR to RGB: `image[..., ::-1]`

OpenCV's rotation: `cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)`
OpenCV's flip: `cv2.flip(image, 1)`
OpenCV BGR to RGB: `cv2.cvtColor(image, cv2.COLOR_BGR2RGB)`

After that, the image has to be converted to PIL.

| fps     | 5.3 | 5.9 | 5  | 5.2 | *13* | 11.8 | 6  | 5.6 |
|---------|-----|-----|----|-----|------|------|----|-----|
| rotate  | np  | np  | np | np  | cv   | cv   | cv | cv  |
| flip    | np  | np  | cv | cv  | cv   | cv   | np | np  |
| convert | np  | cv  | np | cv  | cv   | np   | cv | np  |

So we use exclusively openCV for those transformations.

## Saving format
Saving the image to .png takes a full second. Saving a .bmp takes a 0.2 s.
We'll save them in .bmp and convert them afterward.
