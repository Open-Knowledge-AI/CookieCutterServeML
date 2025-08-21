import numpy as np
import onnxruntime as ort


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


if __name__ == "__main__":
    from app.config import MODELS_DIR

    path_to_model = MODELS_DIR / "v1" / "mobilenetv2" / "v1" / "model.onnx"
    input_data = np.random.rand(1, 3, 224, 224).astype(np.float32)  # Example input data
    output = run_inference(str(path_to_model), input_data)
    print("Inference output shape:", output.shape)
