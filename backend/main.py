from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import Response
import os, uuid, shutil
from translator import translate_pdf_file

app = FastAPI()

UPLOAD_DIR = "uploads"
RESULT_DIR = "results"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

def remove_files(*paths):
    for path in paths:
        try:
            os.remove(path)
        except Exception as e:
            print(f"Error deleting {path}: {e}")

@app.post("/translate-pdf/")
async def translate_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    lang: str = "id"
):
    uid = str(uuid.uuid4())
    input_path = f"{UPLOAD_DIR}/{uid}.pdf"
    output_path = f"{RESULT_DIR}/translated-{uid}.pdf"

    with open(input_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    translate_pdf_file(input_path, output_path, lang)

    # Read the translated file into memory and close it
    with open(output_path, "rb") as f:
        file_data = f.read()

    # Schedule deletion AFTER reading the file
    background_tasks.add_task(remove_files, input_path, output_path)

    return Response(
        content=file_data,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=translated.pdf"}
    )
