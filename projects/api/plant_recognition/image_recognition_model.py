import os
import threading
import uuid
from datetime import datetime
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

USING_S3 = os.environ.get('USING_S3', 'false').strip().lower() == 'true'
USING_EMR = os.environ.get('USING_EMR', 'false').strip().lower() == 'true'
EMR_IP = os.environ.get('EMR_IP')

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN,
    region_name=AWS_REGION,
    config=Config(signature_version='s3v4')
) if USING_S3 else None

def get_hive_connection():
    from pyhive import hive
    conn = hive.Connection(
        host=EMR_IP,
        port=10000,
        database="gaia"
    )
    print(f"[Hive] Connected to {EMR_IP}")
    return conn


def _log_to_hive_sync(username, plant_name, confidence, s3_url):
    print(f"[Hive] log_to_hive called: username={username}, plant={plant_name}, confidence={confidence}")
    print(f"[Hive] USING_EMR={USING_EMR}, EMR_IP={EMR_IP}")
    
    if not USING_EMR or not EMR_IP:
        print("[Hive] Skipped: EMR not enabled or no IP")
        return
    
    conn = None
    try:
        conn = get_hive_connection()
        print(f"[Hive] Connection result: {conn}")
        cursor = conn.cursor()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql = f"""
            INSERT INTO gaia.plant_recognition_events VALUES
            ('{uuid.uuid4()}', '{username}', '{plant_name}', {confidence}, '{s3_url}', '{timestamp}')
        """
        print(f"[Hive] Executing: {sql}")
        cursor.execute(sql)
        conn.commit()
        print("[Hive] Insert successful")
    except Exception as e:
        print(f"[Hive] Failed to log: {e}")
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def log_to_hive(username, plant_name, confidence, s3_url):
    # Keep HTTP response fast even if Hive is slow/unavailable.
    t = threading.Thread(
        target=_log_to_hive_sync,
        args=(username, plant_name, confidence, s3_url),
        daemon=True,
    )
    t.start()

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
    if USING_S3 and top_probability >= 0.25:
        s3_url = upload_to_s3(image_path, username)
        if USING_EMR and EMR_IP:
            best_plant = results[0]["plant"] if results else ""
            log_to_hive(username, best_plant, round(top_probability, 4), s3_url)
    
    return {"predictions": results, "s3_url": s3_url}


def upload_to_s3(image_path: str, username: str = "uploads") -> str:
    if not s3_client:
        return None
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
