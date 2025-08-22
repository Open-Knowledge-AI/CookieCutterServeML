import json

from fastapi import Form, UploadFile, File, APIRouter, HTTPException

from ..config import ASSETS_DIR
from ..inference import content_to_class

router = APIRouter(prefix="/predict", tags=["predict"])

with open(ASSETS_DIR / "idx_to_label" / "imagenet.json") as f:
    IMAGNET_MAPPING = json.load(f)


@router.post("/")
async def predict(
    model_name: str = Form(...),
    input_data: UploadFile = File(...),
):
    content = await input_data.read()

    try:
        class_idx = content_to_class(content, model_name)
        class_label = IMAGNET_MAPPING.get(str(class_idx), "Unknown")
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail=f"Model {model_name} not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "model": model_name,
        "filename": input_data.filename,
        "size": len(content),
        "class": class_label,
    }


@router.post("/batch")
async def predict_batch(
    model_name: str = Form(...),
    input_files: list[UploadFile] = File(...),
):
    results = []
    for input_file in input_files:
        results.append(await predict(model_name, input_file))
    return {"results": results}
