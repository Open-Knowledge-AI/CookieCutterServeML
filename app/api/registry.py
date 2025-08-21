import json

from fastapi import APIRouter, HTTPException

from ..config import MODELS_DIR

router = APIRouter(prefix="/registry", tags=["registry"])


def prepare_model_info(metadata_file, onnx_file):
    model_entry = dict()

    if onnx_file.exists():
        model_entry["onnx"] = str(onnx_file.relative_to(MODELS_DIR))
    else:
        model_entry["onnx"] = "Model file not found"
    if metadata_file.exists():
        try:
            with open(metadata_file, "r") as f:
                model_entry["metadata"] = json.load(f)
        except json.JSONDecodeError:
            model_entry["metadata"] = "Invalid JSON"
    else:
        model_entry["metadata"] = "Metadata file not found"

    return model_entry


@router.get("/")
async def registry():
    # folder structure:
    # models/
    # ├── {dataset_version}
    # │   ├── {arch_name}
    # │   │   ├── {model_name}
    # │   │   │   ├── model.onnx  # The ONNX model file
    # │   │   │   └── model.json  # Metadata file (optional)

    models = {}

    if not MODELS_DIR.exists():
        raise HTTPException(
            status_code=404,
            detail="Models directory not found. Please ensure the models are correctly placed.",
        )

    for dataset_version in MODELS_DIR.iterdir():
        if not dataset_version.is_dir():
            continue
        models[dataset_version.name] = {}

        for arch_name in dataset_version.iterdir():
            if not arch_name.is_dir():
                continue
            models[dataset_version.name][arch_name.name] = {}

            for model_name in arch_name.iterdir():
                if not model_name.is_dir():
                    continue

                onnx_file = model_name / "model.onnx"
                metadata_file = model_name / "model.json"
                model_entry = prepare_model_info(metadata_file, onnx_file)

                models[dataset_version.name][arch_name.name][
                    model_name.name
                ] = model_entry

    return models


@router.get("/{dataset_version}/{arch_name}/{model_name}")
async def get_model_info(dataset_version: str, arch_name: str, model_name: str):
    """
    Return details for a specific model in the registry.

    Path params:
    - dataset_version: dataset version folder
    - arch_name: architecture name folder
    - model_name: model name folder
    """
    model_dir = MODELS_DIR / dataset_version / arch_name / model_name

    if not model_dir.exists() or not model_dir.is_dir():
        raise HTTPException(status_code=404, detail="Model not found in registry.")

    onnx_file = model_dir / "model.onnx"
    metadata_file = model_dir / "model.json"

    model_entry = prepare_model_info(metadata_file, onnx_file)

    return {
        "dataset_version": dataset_version,
        "arch_name": arch_name,
        "model_name": model_name,
        "metadata": model_entry,
    }


if __name__ == "__main__":
    print(
        prepare_model_info(
            MODELS_DIR / "v1" / "mobilenetv2" / "model.json",
            MODELS_DIR / "v1" / "mobilenetv2" / "model.onnx",
        )
    )
