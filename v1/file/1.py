from fastapi import FastAPI, UploadFile, File

app = FastAPI()

@app.post("/uploadfile/")
def upload_file(file: UploadFile = File(...)):
    with open("uploaded_" + file.filename, "wb") as f:
        for chunk in iter(lambda: file.file.read(1024), b""):
            f.write(chunk)
    return {"filename": file.filename}
