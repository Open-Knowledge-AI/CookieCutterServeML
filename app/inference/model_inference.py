from pathlib import Path

import cv2
import numpy as np
import onnxruntime as ort

from ..config import MODELS_DIR
from .preprocess import (
    make_landscape,
    resize_longest_edge,
    pad_to_size,
    make_channels_first,
)

from .postprocess import (
    probability_to_class,
)


def run_inference(model_path, input_data):
    """
    Run inference using an ONNX model.

    Args:
        model_path (str): Path to the ONNX model file.
        input_data (np.ndarray): Input data for the model.

    Returns:
        np.ndarray: Output from the model.
    """
    session = ort.InferenceSession(model_path)
    input_name = session.get_inputs()[0].name
    output = session.run(None, {input_name: input_data})
    return output[0] if output else None


def content_to_class(content, model_name):
    # Assuming the content is an image, we need to process it.
    # Here we would typically convert the content to an image format.
    # For demonstration, let's assume the content is a valid image file.
    # You can use PIL or OpenCV to handle the image processing.
    # For example, if using OpenCV:
    np_array = np.frombuffer(content, np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Invalid image content")

    # Preprocess the image
    image = make_landscape(image)
    image = resize_longest_edge(image, 224)  # Resize to longest edge of 224 pixels
    image = pad_to_size(image, (224, 224))  # Pad to 224x224 pixels
    image = image.astype(np.float32)
    image = make_channels_first(image)  # Convert to channels-first format (C, H, W)
    image = np.expand_dims(image, axis=0)  # Add batch dimension

    # normalise the image
    image /= 255.0
    image = (image - 0.5) / 0.5  # Normalize to [-1, 1]

    # Run inference
    model_path = MODELS_DIR / Path(model_name)
    if not model_path.exists():
        raise FileNotFoundError(f"Model file {model_path} does not exist")

    output = run_inference(str(model_path), image)
    if output is None:
        raise ValueError("Model inference failed, no output returned")

    # Convert probabilities to class labels
    class_label = probability_to_class(output)

    return class_label


if __name__ == "__main__":
    path_to_model = MODELS_DIR / "v1" / "mobilenetv2" / "v1" / "model.onnx"
    input_data = np.random.rand(1, 3, 224, 224).astype(np.float32)  # Example input data
    output = run_inference(str(path_to_model), input_data)
    print("Inference output shape:", output.shape)
