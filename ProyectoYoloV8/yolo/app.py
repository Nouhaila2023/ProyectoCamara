# app.py
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from ultralytics import YOLO
import shutil
import os

app = FastAPI()
model = YOLO("yolov8n.pt")  # tu modelo entrenado

UPLOAD_DIR = "/app/images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, "temp.jpg")
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    results = model.predict(source=file_path, imgsz=640)
    # Asumimos que detecta solo un objeto, ejemplo: número
    data = []
    for r in results:
        boxes = r.boxes.xyxy.tolist()
        cls = r.boxes.cls.tolist()
        for b, c in zip(boxes, cls):
            data.append({"box": b, "class": int(c)})
    
    return JSONResponse({"detections": data})
