# Plant Recognition API

The Plant Recognition API classifies an uploaded plant image and returns the top predictions.

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

-  `POST /recognize`: receives `multipart/form-data` with `image`
-  `GET /health`: service health check

## Quick Local Run

```bash
cd projects/api/plant_recognition
python main.py
```
