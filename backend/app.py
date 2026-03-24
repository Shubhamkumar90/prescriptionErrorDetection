from fastapi import FastAPI, UploadFile, File
import io
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import torch
torch.set_grad_enabled(False)
import easyocr
import numpy as np
import cv2
from checkFunctions import Controller

app = FastAPI()


# model_id = "shubham879/trocr-prescription"
model_id = "/trocr-prescription/final"

processor = TrOCRProcessor.from_pretrained(model_id)
model = VisionEncoderDecoderModel.from_pretrained(model_id)
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
model.eval()
reader = easyocr.Reader(['en'], gpu=True)



def linesImage(image):
    results = reader.readtext(image, detail=1, paragraph=False)

    boxes = []

    for bbox, text, conf in results:
        x = [p[0] for p in bbox]
        y = [p[1] for p in bbox]

        boxes.append({
            "x_min": int(min(x)),
            "x_max": int(max(x)),
            "y_min": int(min(y)),
            "y_max": int(max(y))
        })

    boxes = sorted(boxes, key=lambda b: b["y_min"])

    lines = []
    y_threshold = 25

    for box in boxes:
        placed = False
        y_center = (box["y_min"] + box["y_max"]) / 2

        for line in lines:
            if abs(line["y_center"] - y_center) < y_threshold:
                line["x_min"] = min(line["x_min"], box["x_min"])
                line["x_max"] = max(line["x_max"], box["x_max"])
                line["y_min"] = min(line["y_min"], box["y_min"])
                line["y_max"] = max(line["y_max"], box["y_max"])
                placed = True
                break

        if not placed:
            lines.append({
                "x_min": box["x_min"],
                "x_max": box["x_max"],
                "y_min": box["y_min"],
                "y_max": box["y_max"],
                "y_center": y_center
            })

    lines = sorted(lines, key=lambda l: l["y_min"])

    line_images = []

    target_height = 64

    for line in lines:
        crop = image[
            int(line["y_min"]):int(line["y_max"]),
            int(line["x_min"]):int(line["x_max"])
        ]

        if crop.size == 0:
            continue

        h, w = crop.shape[:2]
        scale = target_height / h
        resized = cv2.resize(crop, (int(w * scale), target_height))

        line_images.append(resized)

    return line_images



@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str):
    return {"item_id": item_id, "q": q}

@app.post("/process-image")
async def process_image(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except:
        return {"error": "Invalid image","success":False}
    # image = Image.open(fl).convert("RGB")
    line_images = linesImage(np.array(image))
    if len(line_images) == 0:
        return {
            "ocr_text": "",
            "error_report": [],
            "message": "No text detected",
            "success":False
        }
    texts = []
    for line in line_images:
        pixel_values = processor(images=line, return_tensors="pt").pixel_values
        pixel_values = pixel_values.to(device)

        with torch.no_grad():
            generated_ids = model.generate(pixel_values)

        text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        texts.append(text)
    ocr_text = "\n".join(texts)
    error=Controller(ocr_text)
    return {
        "ocr_text": ocr_text,
        "error_report":error,
        "success":True
    }