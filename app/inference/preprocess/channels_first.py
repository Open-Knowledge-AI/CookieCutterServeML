import numpy as np


def make_channels_first(image):
    """
    Convert an image from HWC (Height, Width, Channels) format to CHW (Channels, Height, Width) format.
    This is often required for models that expect input in channels-first format.

    Args:
        image (np.ndarray): Input image in HWC format.

    Returns:
        np.ndarray: Image in CHW format.
    """
    return np.transpose(image, (2, 0, 1))  # Change from HWC to CHW
