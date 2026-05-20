from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a base router without a prefix
base_router = APIRouter()


# Define Models
class PoseLandmark(BaseModel):
    x: float
    y: float
    z: float
    visibility: Optional[float] = None

class TrendingPose(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    name: str
    mood_pack: str
    scene_type: str
    landmarks: List[PoseLandmark]
    thumbnail_url: Optional[str] = None
    popularity_score: int = 100

class PoseQueryParams(BaseModel):
    mood: Optional[str] = None
    scene: Optional[str] = None

class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

# Add your routes to the router instead of directly to app
@base_router.get("/")
async def root():
    return {"message": "PosePerfect AI API"}

@base_router.get("/poses", response_model=List[TrendingPose])
async def get_trending_poses(mood: Optional[str] = None, scene: Optional[str] = None):
    query = {}
    if mood:
        query["mood_pack"] = mood
    if scene:
        query["scene_type"] = scene
    
    poses = await db.trending_poses.find(query, {"_id": 0}).to_list(50)
    return poses

@base_router.get("/poses/{pose_id}", response_model=TrendingPose)
async def get_pose_by_id(pose_id: str):
    from fastapi import HTTPException
    pose = await db.trending_poses.find_one({"id": pose_id}, {"_id": 0})
    if pose:
        return pose
    raise HTTPException(status_code=404, detail=f"Pose with id '{pose_id}' not found")

@base_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@base_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks

# Include the base router in the main app under both /api and root /
app.include_router(base_router, prefix="/api")
app.include_router(base_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

@app.on_event("startup")
async def seed_trending_poses():
    count = await db.trending_poses.count_documents({})
    if count == 0:
        logger.info("Seeding trending poses database...")
        await seed_poses()
        logger.info("Trending poses seeded successfully")

async def seed_poses():
    """Seed database with trending poses for different mood packs and scenes"""
    trending_poses = [
        # Y2K Aesthetic - Urban Street
        {
            "id": "y2k-urban-001",
            "name": "Confident Stance",
            "mood_pack": "Y2K Aesthetic",
            "scene_type": "urban_street",
            "landmarks": generate_confident_stance(),
            "popularity_score": 95
        },
        {
            "id": "y2k-urban-002",
            "name": "Peace Sign Energy",
            "mood_pack": "Y2K Aesthetic",
            "scene_type": "urban_street",
            "landmarks": generate_peace_sign_pose(),
            "popularity_score": 90
        },
        # Vogue Editorial - Indoor/Studio
        {
            "id": "vogue-studio-001",
            "name": "Power Pose",
            "mood_pack": "Vogue Editorial",
            "scene_type": "indoor_cafe",
            "landmarks": generate_power_pose(),
            "popularity_score": 98
        },
        {
            "id": "vogue-studio-002",
            "name": "Side Profile Elegance",
            "mood_pack": "Vogue Editorial",
            "scene_type": "indoor_cafe",
            "landmarks": generate_side_profile(),
            "popularity_score": 92
        },
        # Candid Streetwear - Various
        {
            "id": "candid-street-001",
            "name": "Relaxed Walk",
            "mood_pack": "Candid Streetwear",
            "scene_type": "urban_street",
            "landmarks": generate_relaxed_walk(),
            "popularity_score": 88
        },
        {
            "id": "candid-street-002",
            "name": "Casual Lean",
            "mood_pack": "Candid Streetwear",
            "scene_type": "architectural",
            "landmarks": generate_casual_lean(),
            "popularity_score": 85
        },
        # Beach poses
        {
            "id": "beach-casual-001",
            "name": "Beach Vibes",
            "mood_pack": "Candid Streetwear",
            "scene_type": "beach",
            "landmarks": generate_beach_pose(),
            "popularity_score": 87
        },
    ]
    
    await db.trending_poses.insert_many(trending_poses)

def generate_confident_stance():
    """T-pose variation with hands on hips"""
    return [
        {"x": 0.5, "y": 0.1, "z": -0.1, "visibility": 0.99},  # nose
        {"x": 0.52, "y": 0.09, "z": -0.15, "visibility": 0.98},  # left_eye_inner
        {"x": 0.53, "y": 0.09, "z": -0.1, "visibility": 0.98},  # left_eye
        {"x": 0.54, "y": 0.09, "z": -0.1, "visibility": 0.98},  # left_eye_outer
        {"x": 0.48, "y": 0.09, "z": -0.15, "visibility": 0.98},  # right_eye_inner
        {"x": 0.47, "y": 0.09, "z": -0.1, "visibility": 0.98},  # right_eye
        {"x": 0.46, "y": 0.09, "z": -0.1, "visibility": 0.98},  # right_eye_outer
        {"x": 0.54, "y": 0.08, "z": -0.05, "visibility": 0.97},  # left_ear
        {"x": 0.46, "y": 0.08, "z": -0.05, "visibility": 0.97},  # right_ear
        {"x": 0.52, "y": 0.12, "z": -0.08, "visibility": 0.95},  # mouth_left
        {"x": 0.48, "y": 0.12, "z": -0.08, "visibility": 0.95},  # mouth_right
        {"x": 0.58, "y": 0.25, "z": -0.05, "visibility": 0.99},  # left_shoulder
        {"x": 0.42, "y": 0.25, "z": -0.05, "visibility": 0.99},  # right_shoulder
        {"x": 0.62, "y": 0.4, "z": -0.08, "visibility": 0.98},  # left_elbow
        {"x": 0.38, "y": 0.4, "z": -0.08, "visibility": 0.98},  # right_elbow
        {"x": 0.56, "y": 0.5, "z": -0.1, "visibility": 0.97},  # left_wrist (hand on hip)
        {"x": 0.44, "y": 0.5, "z": -0.1, "visibility": 0.97},  # right_wrist (hand on hip)
        {"x": 0.54, "y": 0.52, "z": -0.12, "visibility": 0.95},  # left_pinky
        {"x": 0.55, "y": 0.51, "z": -0.11, "visibility": 0.95},  # left_index
        {"x": 0.56, "y": 0.51, "z": -0.1, "visibility": 0.96},  # left_thumb
        {"x": 0.46, "y": 0.52, "z": -0.12, "visibility": 0.95},  # right_pinky
        {"x": 0.45, "y": 0.51, "z": -0.11, "visibility": 0.95},  # right_index
        {"x": 0.44, "y": 0.51, "z": -0.1, "visibility": 0.96},  # right_thumb
        {"x": 0.54, "y": 0.5, "z": -0.05, "visibility": 0.99},  # left_hip
        {"x": 0.46, "y": 0.5, "z": -0.05, "visibility": 0.99},  # right_hip
        {"x": 0.54, "y": 0.75, "z": -0.08, "visibility": 0.98},  # left_knee
        {"x": 0.46, "y": 0.75, "z": -0.08, "visibility": 0.98},  # right_knee
        {"x": 0.54, "y": 0.95, "z": -0.1, "visibility": 0.97},  # left_ankle
        {"x": 0.46, "y": 0.95, "z": -0.1, "visibility": 0.97},  # right_ankle
        {"x": 0.54, "y": 0.98, "z": -0.05, "visibility": 0.96},  # left_heel
        {"x": 0.46, "y": 0.98, "z": -0.05, "visibility": 0.96},  # right_heel
        {"x": 0.55, "y": 0.99, "z": 0.05, "visibility": 0.95},  # left_foot_index
        {"x": 0.47, "y": 0.99, "z": 0.05, "visibility": 0.95},  # right_foot_index
    ]

def generate_peace_sign_pose():
    """Fun pose with one hand making peace sign near face"""
    return [
        {"x": 0.5, "y": 0.15, "z": -0.1, "visibility": 0.99},
        {"x": 0.52, "y": 0.14, "z": -0.15, "visibility": 0.98},
        {"x": 0.53, "y": 0.14, "z": -0.1, "visibility": 0.98},
        {"x": 0.54, "y": 0.14, "z": -0.1, "visibility": 0.98},
        {"x": 0.48, "y": 0.14, "z": -0.15, "visibility": 0.98},
        {"x": 0.47, "y": 0.14, "z": -0.1, "visibility": 0.98},
        {"x": 0.46, "y": 0.14, "z": -0.1, "visibility": 0.98},
        {"x": 0.54, "y": 0.13, "z": -0.05, "visibility": 0.97},
        {"x": 0.46, "y": 0.13, "z": -0.05, "visibility": 0.97},
        {"x": 0.52, "y": 0.17, "z": -0.08, "visibility": 0.95},
        {"x": 0.48, "y": 0.17, "z": -0.08, "visibility": 0.95},
        {"x": 0.57, "y": 0.28, "z": -0.05, "visibility": 0.99},
        {"x": 0.43, "y": 0.28, "z": -0.05, "visibility": 0.99},
        {"x": 0.6, "y": 0.35, "z": -0.12, "visibility": 0.98},
        {"x": 0.4, "y": 0.42, "z": -0.08, "visibility": 0.98},
        {"x": 0.58, "y": 0.2, "z": -0.2, "visibility": 0.97},  # left hand near face
        {"x": 0.45, "y": 0.55, "z": -0.1, "visibility": 0.97},
        {"x": 0.59, "y": 0.18, "z": -0.22, "visibility": 0.95},
        {"x": 0.6, "y": 0.17, "z": -0.21, "visibility": 0.95},
        {"x": 0.58, "y": 0.19, "z": -0.19, "visibility": 0.96},
        {"x": 0.46, "y": 0.57, "z": -0.12, "visibility": 0.95},
        {"x": 0.45, "y": 0.56, "z": -0.11, "visibility": 0.95},
        {"x": 0.44, "y": 0.56, "z": -0.1, "visibility": 0.96},
        {"x": 0.53, "y": 0.52, "z": -0.05, "visibility": 0.99},
        {"x": 0.47, "y": 0.52, "z": -0.05, "visibility": 0.99},
        {"x": 0.53, "y": 0.77, "z": -0.08, "visibility": 0.98},
        {"x": 0.47, "y": 0.77, "z": -0.08, "visibility": 0.98},
        {"x": 0.53, "y": 0.95, "z": -0.1, "visibility": 0.97},
        {"x": 0.47, "y": 0.95, "z": -0.1, "visibility": 0.97},
        {"x": 0.53, "y": 0.98, "z": -0.05, "visibility": 0.96},
        {"x": 0.47, "y": 0.98, "z": -0.05, "visibility": 0.96},
        {"x": 0.54, "y": 0.99, "z": 0.05, "visibility": 0.95},
        {"x": 0.48, "y": 0.99, "z": 0.05, "visibility": 0.95},
    ]

def generate_power_pose():
    """Strong editorial pose - one hand on hip, other extended"""
    return [
        {"x": 0.48, "y": 0.12, "z": -0.1, "visibility": 0.99},
        {"x": 0.5, "y": 0.11, "z": -0.15, "visibility": 0.98},
        {"x": 0.51, "y": 0.11, "z": -0.1, "visibility": 0.98},
        {"x": 0.52, "y": 0.11, "z": -0.1, "visibility": 0.98},
        {"x": 0.46, "y": 0.11, "z": -0.15, "visibility": 0.98},
        {"x": 0.45, "y": 0.11, "z": -0.1, "visibility": 0.98},
        {"x": 0.44, "y": 0.11, "z": -0.1, "visibility": 0.98},
        {"x": 0.53, "y": 0.1, "z": -0.05, "visibility": 0.97},
        {"x": 0.43, "y": 0.1, "z": -0.05, "visibility": 0.97},
        {"x": 0.5, "y": 0.14, "z": -0.08, "visibility": 0.95},
        {"x": 0.46, "y": 0.14, "z": -0.08, "visibility": 0.95},
        {"x": 0.56, "y": 0.26, "z": -0.05, "visibility": 0.99},
        {"x": 0.4, "y": 0.26, "z": -0.05, "visibility": 0.99},
        {"x": 0.65, "y": 0.35, "z": -0.08, "visibility": 0.98},  # left arm extended
        {"x": 0.36, "y": 0.42, "z": -0.08, "visibility": 0.98},
        {"x": 0.72, "y": 0.4, "z": -0.1, "visibility": 0.97},
        {"x": 0.42, "y": 0.52, "z": -0.1, "visibility": 0.97},  # right hand on hip
        {"x": 0.73, "y": 0.41, "z": -0.12, "visibility": 0.95},
        {"x": 0.74, "y": 0.4, "z": -0.11, "visibility": 0.95},
        {"x": 0.72, "y": 0.41, "z": -0.1, "visibility": 0.96},
        {"x": 0.43, "y": 0.53, "z": -0.12, "visibility": 0.95},
        {"x": 0.42, "y": 0.52, "z": -0.11, "visibility": 0.95},
        {"x": 0.41, "y": 0.52, "z": -0.1, "visibility": 0.96},
        {"x": 0.52, "y": 0.51, "z": -0.05, "visibility": 0.99},
        {"x": 0.44, "y": 0.51, "z": -0.05, "visibility": 0.99},
        {"x": 0.52, "y": 0.76, "z": -0.08, "visibility": 0.98},
        {"x": 0.44, "y": 0.76, "z": -0.08, "visibility": 0.98},
        {"x": 0.52, "y": 0.94, "z": -0.1, "visibility": 0.97},
        {"x": 0.44, "y": 0.94, "z": -0.1, "visibility": 0.97},
        {"x": 0.52, "y": 0.97, "z": -0.05, "visibility": 0.96},
        {"x": 0.44, "y": 0.97, "z": -0.05, "visibility": 0.96},
        {"x": 0.53, "y": 0.99, "z": 0.05, "visibility": 0.95},
        {"x": 0.45, "y": 0.99, "z": 0.05, "visibility": 0.95},
    ]

def generate_side_profile():
    """Side profile editorial pose"""
    return [
        {"x": 0.45, "y": 0.13, "z": -0.1, "visibility": 0.99},
        {"x": 0.46, "y": 0.12, "z": -0.15, "visibility": 0.98},
        {"x": 0.47, "y": 0.12, "z": -0.1, "visibility": 0.7},
        {"x": 0.48, "y": 0.12, "z": -0.1, "visibility": 0.5},
        {"x": 0.44, "y": 0.12, "z": -0.15, "visibility": 0.98},
        {"x": 0.43, "y": 0.12, "z": -0.1, "visibility": 0.98},
        {"x": 0.42, "y": 0.12, "z": -0.1, "visibility": 0.98},
        {"x": 0.49, "y": 0.11, "z": -0.05, "visibility": 0.6},
        {"x": 0.41, "y": 0.11, "z": -0.05, "visibility": 0.97},
        {"x": 0.46, "y": 0.15, "z": -0.08, "visibility": 0.95},
        {"x": 0.44, "y": 0.15, "z": -0.08, "visibility": 0.95},
        {"x": 0.52, "y": 0.27, "z": -0.05, "visibility": 0.8},
        {"x": 0.38, "y": 0.27, "z": -0.05, "visibility": 0.99},
        {"x": 0.55, "y": 0.4, "z": -0.08, "visibility": 0.75},
        {"x": 0.35, "y": 0.4, "z": -0.08, "visibility": 0.98},
        {"x": 0.57, "y": 0.5, "z": -0.1, "visibility": 0.7},
        {"x": 0.33, "y": 0.5, "z": -0.1, "visibility": 0.97},
        {"x": 0.58, "y": 0.51, "z": -0.12, "visibility": 0.65},
        {"x": 0.59, "y": 0.5, "z": -0.11, "visibility": 0.65},
        {"x": 0.57, "y": 0.51, "z": -0.1, "visibility": 0.7},
        {"x": 0.32, "y": 0.51, "z": -0.12, "visibility": 0.95},
        {"x": 0.31, "y": 0.5, "z": -0.11, "visibility": 0.95},
        {"x": 0.3, "y": 0.5, "z": -0.1, "visibility": 0.96},
        {"x": 0.48, "y": 0.51, "z": -0.05, "visibility": 0.99},
        {"x": 0.42, "y": 0.51, "z": -0.05, "visibility": 0.99},
        {"x": 0.48, "y": 0.76, "z": -0.08, "visibility": 0.98},
        {"x": 0.42, "y": 0.76, "z": -0.08, "visibility": 0.98},
        {"x": 0.48, "y": 0.94, "z": -0.1, "visibility": 0.97},
        {"x": 0.42, "y": 0.94, "z": -0.1, "visibility": 0.97},
        {"x": 0.48, "y": 0.97, "z": -0.05, "visibility": 0.96},
        {"x": 0.42, "y": 0.97, "z": -0.05, "visibility": 0.96},
        {"x": 0.49, "y": 0.99, "z": 0.05, "visibility": 0.95},
        {"x": 0.43, "y": 0.99, "z": 0.05, "visibility": 0.95},
    ]

def generate_relaxed_walk():
    """Natural walking pose"""
    return [
        {"x": 0.5, "y": 0.14, "z": -0.1, "visibility": 0.99},
        {"x": 0.52, "y": 0.13, "z": -0.15, "visibility": 0.98},
        {"x": 0.53, "y": 0.13, "z": -0.1, "visibility": 0.98},
        {"x": 0.54, "y": 0.13, "z": -0.1, "visibility": 0.98},
        {"x": 0.48, "y": 0.13, "z": -0.15, "visibility": 0.98},
        {"x": 0.47, "y": 0.13, "z": -0.1, "visibility": 0.98},
        {"x": 0.46, "y": 0.13, "z": -0.1, "visibility": 0.98},
        {"x": 0.54, "y": 0.12, "z": -0.05, "visibility": 0.97},
        {"x": 0.46, "y": 0.12, "z": -0.05, "visibility": 0.97},
        {"x": 0.52, "y": 0.16, "z": -0.08, "visibility": 0.95},
        {"x": 0.48, "y": 0.16, "z": -0.08, "visibility": 0.95},
        {"x": 0.56, "y": 0.27, "z": -0.05, "visibility": 0.99},
        {"x": 0.44, "y": 0.27, "z": -0.05, "visibility": 0.99},
        {"x": 0.58, "y": 0.4, "z": -0.1, "visibility": 0.98},
        {"x": 0.42, "y": 0.38, "z": -0.05, "visibility": 0.98},
        {"x": 0.6, "y": 0.52, "z": -0.12, "visibility": 0.97},
        {"x": 0.4, "y": 0.48, "z": -0.08, "visibility": 0.97},
        {"x": 0.61, "y": 0.53, "z": -0.14, "visibility": 0.95},
        {"x": 0.62, "y": 0.52, "z": -0.13, "visibility": 0.95},
        {"x": 0.6, "y": 0.53, "z": -0.12, "visibility": 0.96},
        {"x": 0.39, "y": 0.49, "z": -0.1, "visibility": 0.95},
        {"x": 0.38, "y": 0.48, "z": -0.09, "visibility": 0.95},
        {"x": 0.37, "y": 0.48, "z": -0.08, "visibility": 0.96},
        {"x": 0.52, "y": 0.52, "z": -0.05, "visibility": 0.99},
        {"x": 0.48, "y": 0.52, "z": -0.05, "visibility": 0.99},
        {"x": 0.52, "y": 0.74, "z": -0.06, "visibility": 0.98},
        {"x": 0.48, "y": 0.78, "z": -0.1, "visibility": 0.98},
        {"x": 0.52, "y": 0.92, "z": -0.08, "visibility": 0.97},
        {"x": 0.48, "y": 0.96, "z": -0.12, "visibility": 0.97},
        {"x": 0.52, "y": 0.95, "z": -0.05, "visibility": 0.96},
        {"x": 0.48, "y": 0.98, "z": -0.08, "visibility": 0.96},
        {"x": 0.53, "y": 0.97, "z": 0.02, "visibility": 0.95},
        {"x": 0.49, "y": 0.99, "z": 0.0, "visibility": 0.95},
    ]

def generate_casual_lean():
    """Leaning against wall casually"""
    return [
        {"x": 0.52, "y": 0.15, "z": -0.1, "visibility": 0.99},
        {"x": 0.54, "y": 0.14, "z": -0.15, "visibility": 0.98},
        {"x": 0.55, "y": 0.14, "z": -0.1, "visibility": 0.98},
        {"x": 0.56, "y": 0.14, "z": -0.1, "visibility": 0.98},
        {"x": 0.5, "y": 0.14, "z": -0.15, "visibility": 0.98},
        {"x": 0.49, "y": 0.14, "z": -0.1, "visibility": 0.98},
        {"x": 0.48, "y": 0.14, "z": -0.1, "visibility": 0.98},
        {"x": 0.56, "y": 0.13, "z": -0.05, "visibility": 0.97},
        {"x": 0.48, "y": 0.13, "z": -0.05, "visibility": 0.97},
        {"x": 0.54, "y": 0.17, "z": -0.08, "visibility": 0.95},
        {"x": 0.5, "y": 0.17, "z": -0.08, "visibility": 0.95},
        {"x": 0.6, "y": 0.28, "z": -0.05, "visibility": 0.99},
        {"x": 0.44, "y": 0.28, "z": -0.05, "visibility": 0.99},
        {"x": 0.64, "y": 0.42, "z": -0.08, "visibility": 0.98},
        {"x": 0.4, "y": 0.4, "z": -0.08, "visibility": 0.98},
        {"x": 0.66, "y": 0.54, "z": -0.1, "visibility": 0.97},
        {"x": 0.38, "y": 0.5, "z": -0.1, "visibility": 0.97},
        {"x": 0.67, "y": 0.55, "z": -0.12, "visibility": 0.95},
        {"x": 0.68, "y": 0.54, "z": -0.11, "visibility": 0.95},
        {"x": 0.66, "y": 0.55, "z": -0.1, "visibility": 0.96},
        {"x": 0.37, "y": 0.51, "z": -0.12, "visibility": 0.95},
        {"x": 0.36, "y": 0.5, "z": -0.11, "visibility": 0.95},
        {"x": 0.35, "y": 0.5, "z": -0.1, "visibility": 0.96},
        {"x": 0.54, "y": 0.53, "z": -0.05, "visibility": 0.99},
        {"x": 0.46, "y": 0.53, "z": -0.05, "visibility": 0.99},
        {"x": 0.56, "y": 0.77, "z": -0.08, "visibility": 0.98},
        {"x": 0.44, "y": 0.77, "z": -0.08, "visibility": 0.98},
        {"x": 0.58, "y": 0.95, "z": -0.1, "visibility": 0.97},
        {"x": 0.42, "y": 0.95, "z": -0.1, "visibility": 0.97},
        {"x": 0.58, "y": 0.98, "z": -0.05, "visibility": 0.96},
        {"x": 0.42, "y": 0.98, "z": -0.05, "visibility": 0.96},
        {"x": 0.59, "y": 0.99, "z": 0.05, "visibility": 0.95},
        {"x": 0.43, "y": 0.99, "z": 0.05, "visibility": 0.95},
    ]

def generate_beach_pose():
    """Relaxed beach pose"""
    return [
        {"x": 0.5, "y": 0.16, "z": -0.1, "visibility": 0.99},
        {"x": 0.52, "y": 0.15, "z": -0.15, "visibility": 0.98},
        {"x": 0.53, "y": 0.15, "z": -0.1, "visibility": 0.98},
        {"x": 0.54, "y": 0.15, "z": -0.1, "visibility": 0.98},
        {"x": 0.48, "y": 0.15, "z": -0.15, "visibility": 0.98},
        {"x": 0.47, "y": 0.15, "z": -0.1, "visibility": 0.98},
        {"x": 0.46, "y": 0.15, "z": -0.1, "visibility": 0.98},
        {"x": 0.54, "y": 0.14, "z": -0.05, "visibility": 0.97},
        {"x": 0.46, "y": 0.14, "z": -0.05, "visibility": 0.97},
        {"x": 0.52, "y": 0.18, "z": -0.08, "visibility": 0.95},
        {"x": 0.48, "y": 0.18, "z": -0.08, "visibility": 0.95},
        {"x": 0.55, "y": 0.29, "z": -0.05, "visibility": 0.99},
        {"x": 0.45, "y": 0.29, "z": -0.05, "visibility": 0.99},
        {"x": 0.58, "y": 0.38, "z": -0.12, "visibility": 0.98},
        {"x": 0.42, "y": 0.38, "z": -0.12, "visibility": 0.98},
        {"x": 0.6, "y": 0.3, "z": -0.18, "visibility": 0.97},  # arms raised
        {"x": 0.4, "y": 0.3, "z": -0.18, "visibility": 0.97},
        {"x": 0.61, "y": 0.29, "z": -0.2, "visibility": 0.95},
        {"x": 0.62, "y": 0.28, "z": -0.19, "visibility": 0.95},
        {"x": 0.6, "y": 0.29, "z": -0.18, "visibility": 0.96},
        {"x": 0.39, "y": 0.29, "z": -0.2, "visibility": 0.95},
        {"x": 0.38, "y": 0.28, "z": -0.19, "visibility": 0.95},
        {"x": 0.4, "y": 0.29, "z": -0.18, "visibility": 0.96},
        {"x": 0.51, "y": 0.54, "z": -0.05, "visibility": 0.99},
        {"x": 0.49, "y": 0.54, "z": -0.05, "visibility": 0.99},
        {"x": 0.51, "y": 0.78, "z": -0.08, "visibility": 0.98},
        {"x": 0.49, "y": 0.78, "z": -0.08, "visibility": 0.98},
        {"x": 0.51, "y": 0.94, "z": -0.1, "visibility": 0.97},
        {"x": 0.49, "y": 0.94, "z": -0.1, "visibility": 0.97},
        {"x": 0.51, "y": 0.97, "z": -0.05, "visibility": 0.96},
        {"x": 0.49, "y": 0.97, "z": -0.05, "visibility": 0.96},
        {"x": 0.52, "y": 0.99, "z": 0.05, "visibility": 0.95},
        {"x": 0.5, "y": 0.99, "z": 0.05, "visibility": 0.95},
    ]
