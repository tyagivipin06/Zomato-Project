from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from src.api.schemas import LocationsResponse, CuisinesResponse
from src.models.preferences import UserPreferences
from src.models.recommendation import RecommendationResponse
from data_layer.repository import RestaurantRepository
from src.services.filter import RestaurantFilter
from src.llm.recommendation import RecommendationService

logger = logging.getLogger(__name__)

repo = None
filter_service = None
recommendation_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global repo, filter_service, recommendation_service
    logger.info("Initializing services on startup...")
    repo = RestaurantRepository()
    filter_service = RestaurantFilter(repository=repo)
    recommendation_service = RecommendationService(filter_service=filter_service)
    yield
    # Cleanup if needed

app = FastAPI(title="Zomato AI Recommendation API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/v1/locations", response_model=LocationsResponse)
def get_locations():
    if not repo:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return {"locations": repo.get_locations()}

@app.get("/api/v1/cuisines", response_model=CuisinesResponse)
def get_cuisines():
    if not repo:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return {"cuisines": repo.get_cuisines()}

@app.post("/api/v1/recommend", response_model=RecommendationResponse)
def recommend(prefs: UserPreferences):
    if not recommendation_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    try:
        import time
        start_time = time.time()
        response, warnings = recommendation_service.recommend(prefs)
        latency = time.time() - start_time
        logger.info(f"/api/v1/recommend completed in {latency:.2f}s | filter warnings: {len(warnings)}")
        
        response.metadata["relaxation_applied"] = len(warnings) > 0
        response.metadata["warnings"] = warnings
        return response
    except Exception as e:
        logger.error(f"Error in recommend endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
