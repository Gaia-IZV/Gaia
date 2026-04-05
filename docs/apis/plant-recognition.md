# Plant Recognition API

The Plant Recognition API classifies an uploaded plant image and returns the top predictions.

## Model

We use a pre-trained model from Hugging Face: **`juppy44/plant-identification-2m-vit-b`**
- This is a Vision Transformer (ViT) model trained on ~2 million plant images
- The model is loaded via the `transformers` library from Hugging Face

## Related Code

-  API entrypoint: `projects/api/plant_recognition/main.py`
-  Model loading and inference: `projects/api/plant_recognition/image_recognition_model.py`
-  Python dependencies: `projects/api/plant_recognition/requirements.txt`
-  Docker runtime image: `docker/plant-recognition-api/Dockerfile`
-  Shared environment file: `projects/api/.env` and `projects/api/.env.example`

## Related Notebooks

-  `projects/notebooks/modelo_prediccion_preentrenado.ipynb`
-  `projects/notebooks/ModeloCNN.ipynb`

## Endpoint Summary

-  `POST /recognize`: receives `multipart/form-data` with `image` and optional `username`
-  Returns top 5 predictions with probabilities
-  If confidence >= 25%, uploads image to S3 and returns the URL
-  `GET /health`: service health check

## Quick Local Run

```bash
cd projects/api/plant_recognition
python main.py
```
