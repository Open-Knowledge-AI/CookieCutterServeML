from fastapi import Form, UploadFile, File, APIRouter

router = APIRouter(prefix="/predict", tags=["predict"])


@router.post("/")
async def predict(
    model_name: str = Form(...),
    input_data: UploadFile = File(...),
):
    content = await input_data.read()
    return {"model": model_name, "filename": input_data.filename, "size": len(content)}


@router.post("/batch")
async def predict_batch(
    model_name: str = Form(...),
    input_files: list[UploadFile] = File(...),
):
    results = []
    for input_file in input_files:
        content = await input_file.read()
        results.append(
            {"model": model_name, "filename": input_file.filename, "size": len(content)}
        )
    return {"results": results}
