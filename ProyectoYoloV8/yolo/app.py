# app.py
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from ultralytics import YOLO
import shutil
import os

#Crea la instancia de FastAPI que maneja todas las rutas de tu API.
app = FastAPI()
model = YOLO("yolov8n.pt")  # tu modelo entrenado

#Aquí estás definiendo una ruta en tu sistema de archivos donde quieres guardar las imágenes que suba tu ESP32-CAM.
#En este caso, "/app/images" es la carpeta dentro del contenedor Docker donde estará tu aplicación FastAPI.
#/app es típicamente el directorio de trabajo dentro de un contenedor Docker.
#/app/images será una subcarpeta donde se almacenarán temporalmente las fotos para que YOLO las procese.
#💡 Importante: Si ejecutas esto fuera de Docker, /app/images sería una ruta absoluta en tu PC, por ejemplo en Windows sería algo como C:\app\images
UPLOAD_DIR = "/app/images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

#Define una ruta POST /detect para recibir imágenes
@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    #Guarda la imagen recibida como temp.jpg dentro de /app/images.
    file_path = os.path.join(UPLOAD_DIR, "temp.jpg")
    with open(file_path, "wb") as f:
        #copia el contenido del archivo subido a disco
        shutil.copyfileobj(file.file, f)

	#Ejecuta la detección de objetos usando tu modelo YOLO en la imagen guardada.
    results = model.predict(source=file_path, imgsz=640)
    # Asumimos que detecta solo un objeto, ejemplo: número
    data = []
    #results es una lista de objetos que contienen las detecciones. Cada objeto tiene una propiedad "boxes" con las coordenadas y clases detectadas.  {"box": [x1, y1, x2, y2], "class": 5}
    for r in results:
        #boxes es una lista de coordenadas de las cajas detectadas en formato [x1, y1, x2, y2]
        boxes = r.boxes.xyxy.tolist()
				#contiene la clase detectada
        cls = r.boxes.cls.tolist()
        for b, c in zip(boxes, cls):
            data.append({"box": b, "class": int(c)})
    
		#Devuelve todas las detecciones en formato JSON.
    return JSONResponse({"detections": data})
