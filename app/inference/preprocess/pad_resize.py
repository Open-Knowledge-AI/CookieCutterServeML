import cv2


def make_landscape(image):
    """
    Convert the image to landscape orientation if it is in portrait mode.
    This is done by rotating the image 90 degrees clockwise if its height is greater than its width.
    """
    height, width = image.shape[:2]
    if height > width:
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    return image


def resize_longest_edge(image, longest_edge):
    """
    Resize the image so that the longest edge is equal to `longest_edge`.
    The shorter edge is scaled proportionally.
    """
    height, width = image.shape[:2]
    if height > width:
        new_height = longest_edge
        new_width = int((longest_edge / height) * width)
    else:
        new_width = longest_edge
        new_height = int((longest_edge / width) * height)

    resized_image = cv2.resize(
        image, (new_width, new_height), interpolation=cv2.INTER_LINEAR
    )
    return resized_image


def pad_to_size(image, target_size):
    """
    Pad the image to the target size with zeros (black padding).
    The image is centered in the padded area.
    """
    height, width = image.shape[:2]
    pad_height = max(0, target_size[0] - height)
    pad_width = max(0, target_size[1] - width)

    top_pad = pad_height // 2
    bottom_pad = pad_height - top_pad
    left_pad = pad_width // 2
    right_pad = pad_width - left_pad

    padded_image = cv2.copyMakeBorder(
        image,
        top_pad,
        bottom_pad,
        left_pad,
        right_pad,
        cv2.BORDER_CONSTANT,
        value=(0, 0, 0),
    )

    return padded_image
