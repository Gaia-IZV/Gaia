import os
import uuid
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
from dotenv import load_dotenv
import boto3
from botocore.config import Config

_API_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(_API_ROOT, ".env"))

MODEL_ID = "juppy44/plant-identification-2m-vit-b"
HF_TOKEN = os.environ.get('HF_TOKEN')

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_SESSION_TOKEN = os.environ.get('AWS_SESSION_TOKEN')
AWS_REGION = os.environ.get('AWS_REGION')
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN,
    region_name=AWS_REGION,
    config=Config(signature_version='s3v4')
)

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

def recognize_plant(image_path: str, username: str = "uploads") -> dict:
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
    
    top_probability = topk.values[0].item()
    
    s3_url = None
    if top_probability >= 0.25:
        s3_url = upload_to_s3(image_path, username)
    
    return {"predictions": results, "s3_url": s3_url}


def upload_to_s3(image_path: str, username: str = "uploads") -> str:
    ext = os.path.splitext(image_path)[1].lower()
    key = f"{username}/{uuid.uuid4()}{ext}"
    
    with open(image_path, 'rb') as f:
        s3_client.upload_fileobj(
            f,
            S3_BUCKET_NAME,
            key,
            ExtraArgs={'ContentType': 'image/jpeg'}
        )
    
    return f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{key}"
