from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import cv2
import numpy as np
import base64
from ultralytics import YOLO
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


models = []
for mod in sorted(os.listdir("models_detect")):
    model = YOLO(f"models_detect/{mod}")
    model.to("cpu")  # Forzar que siempre se use CPU
    models.append(model)

ultima_imagen = None

# Coordenadas fijas ROI (x, y, w, h)
ROI_X, ROI_Y, ROI_W, ROI_H = 582, 6, 766, 1052

@app.get("/tomar-imagen")
def tomar_imagen():
    global ultima_imagen

    cap = cv2.VideoCapture(2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    ret, frame = cap.read()
    print("Resolución cámara:", frame.shape)

    cap.release()

    if not ret:
        return {"error": "No se pudo capturar la imagen"}

    # Recorte ROI
    frame = frame[ROI_Y:ROI_Y+ROI_H, ROI_X:ROI_X+ROI_W]

    ultima_imagen = frame
    print(f"Imagen recortada: {ultima_imagen.shape}")
    return {"mensaje": "Imagen tomada desde webcam y recortada"}

@app.get("/obtener-imagen")
def obtener_imagen():
    global ultima_imagen
    if ultima_imagen is None:
        return {"error": "No hay imagen"}
    _, buffer = cv2.imencode(".jpg", ultima_imagen)
    return Response(buffer.tobytes(), media_type="image/jpeg")

def iou(box1, box2):
    # box = [x1, y1, x2, y2]
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    inter_area = max(0, x2 - x1) * max(0, y2 - y1)
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union = area1 + area2 - inter_area
    return inter_area / union if union > 0 else 0

def agrupar_detecciones(cajas, iou_thresh=0.5):
    grupos = []
    usadas = set()

    for i in range(len(cajas)):
        if i in usadas:
            continue
        grupo = [cajas[i]]
        usadas.add(i)
        for j in range(i+1, len(cajas)):
            if j in usadas:
                continue
            if iou(cajas[i][:4], cajas[j][:4]) > iou_thresh:
                grupo.append(cajas[j])
                usadas.add(j)
        grupos.append(grupo)

    # Promediar cada grupo
    cajas_finales = []
    for grupo in grupos:
        xs1, ys1, xs2, ys2, confs = [], [], [], [], []
        for (x1, y1, x2, y2, conf, cls) in grupo:
            xs1.append(x1); ys1.append(y1); xs2.append(x2); ys2.append(y2); confs.append(conf)
        caja_prom = [
            np.mean(xs1), np.mean(ys1),
            np.mean(xs2), np.mean(ys2),
            np.mean(confs), int(grupo[0][5])  # cls igual
        ]
        cajas_finales.append(caja_prom)
    return cajas_finales

@app.get("/analizar-imagen")
def analizar_imagen():
    global ultima_imagen
    if ultima_imagen is None:
        return {"error": "No hay imagen para analizar"}

    img_pre = ultima_imagen.copy()
    todas_cajas = []
    if img_pre is None:
        return {"error": "Error al procesar la imagen"}

    for model in models:
        results = model.predict(img_pre, imgsz=736, conf=0.5, device="cpu")
        if not results or results[0].boxes is None:
            print("⚠️ No hay detecciones para este modelo.")
            continue

        boxes = results[0].boxes
        xyxy = boxes.xyxy.cpu().numpy()
        conf = boxes.conf.cpu().numpy()
        cls = boxes.cls.cpu().numpy()

        for i in range(len(xyxy)):
            todas_cajas.append([*xyxy[i], conf[i], int(cls[i])])

    if not todas_cajas:
        return {"mensaje": "No se detectaron piezas", "imagen_procesada": None}

    # 👉 reemplazo del NMS clásico por agrupación por IoU
    cajas_finales = agrupar_detecciones(todas_cajas, iou_thresh=0.25)

    img_draw = ultima_imagen.copy()
    num_dets = 0

    for (x1, y1, x2, y2, conf, cls) in cajas_finales:
        # Calcula el centro del rectángulo
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)

        # Vecinos alrededor del centro
        h, w, _ = img_draw.shape
        vecinos = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < w and 0 <= ny < h:
                vecinos.append(img_draw[ny, nx])
        if vecinos:
            color_prom = np.mean(vecinos, axis=0)
        else:
            color_prom = np.array([0, 0, 0])

        color_complementario = [255 - int(c) for c in color_prom]

        # Dibujar centro
        cv2.circle(img_draw, (cx, cy), 10, color_complementario, -1)
        num_dets += 1

    print(f"Número de piezas detectadas: {num_dets}")
    # Debug: guardar imagen con detecciones
    # cv2.imwrite("ultima_deteccion.jpg", img_draw)
    _, buffer = cv2.imencode(".jpg", img_draw)
    imagen_base64 = base64.b64encode(buffer).decode("utf-8")

    return {
        "imagen_procesada": imagen_base64,
        "texto": {
            "mensaje": f"Número de piezas detectadas: {num_dets}",
        }
    }
