import os
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
from dotenv import load_dotenv

_API_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(_API_ROOT, ".env"))

MODEL_ID = "juppy44/plant-identification-2m-vit-b"
HF_TOKEN = os.environ.get('HF_TOKEN')

model = None
processor = None

def load_model():
    global model, processor
    if model is None:
        processor = AutoImageProcessor.from_pretrained(MODEL_ID, token=HF_TOKEN)
        model = AutoModelForImageClassification.from_pretrained(MODEL_ID, token=HF_TOKEN)
        model.to("cpu")
        model.eval()
    return model, processor

def recognize_plant(image_path: str) -> dict:
    model, processor = load_model()
    
    image = Image.open(image_path).convert("RGB")
    
    inputs = processor(images=image, return_tensors="pt")
    
    with torch.no_grad():
        logits = model(**inputs).logits
    
    pred = logits.softmax(dim=-1)[0]
    topk = torch.topk(pred, k=5)
    
    results = []
    for prob, idx in zip(topk.values, topk.indices):
        label = model.config.id2label[idx.item()]
        results.append({"plant": label, "probability": round(prob.item(), 4)})
    
    return {"predictions": results}
