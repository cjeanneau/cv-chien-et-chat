from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sys
from pathlib import Path
import time
from datetime import datetime
from src.utils.utils import save_image_with_max_size

# Ajouter le répertoire racine au path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from .auth import verify_token
from src.models.predictor import CatDogPredictor
from src.monitoring.metrics import time_inference, log_inference_time, save_prediction_in_db

# Configuration des templates
TEMPLATES_DIR = ROOT_DIR / "src" / "web" / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter()

# Initialisation du prédicteur
predictor = CatDogPredictor()

@router.get("/", response_class=HTMLResponse)
async def welcome(request: Request):
    """Page d'accueil avec interface web"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "model_loaded": predictor.is_loaded()
    })

@router.get("/info", response_class=HTMLResponse)
async def info_page(request: Request):
    """Page d'informations"""
    model_info = {
        "name": "Cats vs Dogs Classifier",
        "version": "1.0.0",
        "description": "Modèle CNN pour classification chats/chiens",
        "parameters": predictor.model.count_params() if predictor.is_loaded() else 0,
        "classes": ["Cat", "Dog"],
        "input_size": f"{predictor.image_size[0]}x{predictor.image_size[1]}",
        "model_loaded": predictor.is_loaded()
    }
    return templates.TemplateResponse("info.html", {
        "request": request, 
        "model_info": model_info
    })

@router.get("/inference", response_class=HTMLResponse)
async def inference_page(request: Request):
    """Page d'inférence"""
    return templates.TemplateResponse("inference.html", {
        "request": request,
        "model_loaded": predictor.is_loaded()
    })

@router.post("/api/predict")
#@time_inference  # Décorateur de monitoring
async def predict_api(
    file: UploadFile = File(...),
    token: str = Depends(verify_token)
):
    """API de prédiction avec monitoring"""
    if not predictor.is_loaded():
        raise HTTPException(status_code=503, detail="Modèle non disponible")
    
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Format d'image invalide")
    
    try:
        start_time = time.perf_counter()
        image_data = await file.read()
        result = predictor.predict(image_data)
        end_time = time.perf_counter()
        inference_time_ms = (end_time - start_time) * 1000
        
        response_data = {
            "filename": file.filename,
            "prediction": result["prediction"],
            "inference-tile": f"{inference_time_ms:.2f} ms",
            "confidence": f"{result['confidence']:.2%}",
            "probabilities": {
                "cat": f"{result['probabilities']['cat']:.2%}",
                "dog": f"{result['probabilities']['dog']:.2%}"
            }
        }
        
        # Sauvegarder l'image uploadée avec un nom unique
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_uploads = f"{result['prediction']}_{timestamp}.jpg"
        save_image_with_max_size(image_data, filename_uploads)

        # Enregistrer dans la base de données
        save_prediction_in_db(
            probabilite_chat=result['probabilities']['cat'],
            image_path=filename_uploads,
            inference_time_ms=inference_time_ms
        )
       
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction: {str(e)}")

        # Logger les métriques
        log_inference_time(
            inference_time_ms=inference_time_ms,
            filename=file.filename,
            prediction=result["prediction"],
            confidence=f"{result['confidence']:.2%}",
            success=True
        )
        
        return response_data
        
    except Exception as e:
        # En cas d'erreur, logger quand même le temps
        end_time = time.perf_counter()
        inference_time_ms = (end_time - start_time) * 1000
        
        log_inference_time(
            inference_time_ms=inference_time_ms,
            filename=file.filename if file else "unknown",
            success=False
        )
        
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction: {str(e)}")

@router.get("/api/info")
async def api_info():
    """Informations API JSON"""
    return {
        "model_loaded": predictor.is_loaded(),
        "model_path": str(predictor.model_path),
        "version": "1.0.0",
        "parameters": predictor.model.count_params() if predictor.is_loaded() else 0
    }

@router.get("/health")
async def health_check():
    """Vérification de l'état de l'API"""
    return {
        "status": "healthy",
        "model_loaded": predictor.is_loaded()
    }