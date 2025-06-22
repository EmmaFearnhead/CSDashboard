from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class TransportMode(str, Enum):
    ROAD = "road"
    AIR = "air"

class Species(str, Enum):
    ELEPHANT = "elephant"
    RHINO = "rhino"
    LION = "lion"
    CHEETAH = "cheetah"
    BUFFALO = "buffalo"
    GIRAFFE = "giraffe"
    ZEBRA = "zebra"
    OTHER = "other"

# Define Models
class Location(BaseModel):
    name: str
    country: str
    latitude: float
    longitude: float

class TranslocationCreate(BaseModel):
    species: Species
    number_of_animals: int
    month: int = Field(ge=1, le=12)
    year: int
    source_reserve: Location
    recipient_reserve: Location
    transport_mode: TransportMode
    additional_notes: Optional[str] = ""

class Translocation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    species: Species
    number_of_animals: int
    month: int
    year: int
    source_reserve: Location
    recipient_reserve: Location
    transport_mode: TransportMode
    additional_notes: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Routes
@api_router.get("/")
async def root():
    return {"message": "Wildlife Conservation Dashboard API"}

@api_router.post("/translocations", response_model=Translocation)
async def create_translocation(translocation: TranslocationCreate):
    translocation_dict = translocation.dict()
    translocation_obj = Translocation(**translocation_dict)
    await db.translocations.insert_one(translocation_obj.dict())
    return translocation_obj

@api_router.get("/translocations", response_model=List[Translocation])
async def get_translocations(
    species: Optional[Species] = None,
    year: Optional[int] = None,
    transport_mode: Optional[TransportMode] = None
):
    filter_dict = {}
    if species:
        filter_dict["species"] = species
    if year:
        filter_dict["year"] = year
    if transport_mode:
        filter_dict["transport_mode"] = transport_mode
    
    translocations = await db.translocations.find(filter_dict).to_list(1000)
    return [Translocation(**translocation) for translocation in translocations]

@api_router.get("/translocations/stats")
async def get_translocation_stats():
    pipeline = [
        {
            "$group": {
                "_id": "$species",
                "total_animals": {"$sum": "$number_of_animals"},
                "total_translocations": {"$sum": 1}
            }
        }
    ]
    stats = await db.translocations.aggregate(pipeline).to_list(100)
    return {stat["_id"]: {"total_animals": stat["total_animals"], "total_translocations": stat["total_translocations"]} for stat in stats}

@api_router.delete("/translocations/{translocation_id}")
async def delete_translocation(translocation_id: str):
    result = await db.translocations.delete_one({"id": translocation_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Translocation not found")
    return {"message": "Translocation deleted successfully"}

@api_router.post("/translocations/sample-data")
async def create_sample_data():
    # Sample African reserves and their coordinates
    sample_translocations = [
        {
            "species": "elephant",
            "number_of_animals": 25,
            "month": 6,
            "year": 2023,
            "source_reserve": {
                "name": "Kruger National Park",
                "country": "South Africa",
                "latitude": -24.0063,
                "longitude": 31.4953
            },
            "recipient_reserve": {
                "name": "Addo Elephant National Park",
                "country": "South Africa", 
                "latitude": -33.4734,
                "longitude": 25.7519
            },
            "transport_mode": "road",
            "additional_notes": "Family herd relocation due to overpopulation"
        },
        {
            "species": "rhino",
            "number_of_animals": 8,
            "month": 9,
            "year": 2023,
            "source_reserve": {
                "name": "Hluhluwe-iMfolozi Park",
                "country": "South Africa",
                "latitude": -28.2742,
                "longitude": 32.0961
            },
            "recipient_reserve": {
                "name": "Maasai Mara",
                "country": "Kenya",
                "latitude": -1.4061,
                "longitude": 35.0059
            },
            "transport_mode": "air",
            "additional_notes": "White rhino conservation breeding program"
        },
        {
            "species": "elephant",
            "number_of_animals": 15,
            "month": 3,
            "year": 2024,
            "source_reserve": {
                "name": "Hwange National Park",
                "country": "Zimbabwe",
                "latitude": -18.6297,
                "longitude": 26.4285
            },
            "recipient_reserve": {
                "name": "Gonarezhou National Park",
                "country": "Zimbabwe",
                "latitude": -21.5417,
                "longitude": 31.2167
            },
            "transport_mode": "road",
            "additional_notes": "Drought mitigation relocation"
        },
        {
            "species": "rhino",
            "number_of_animals": 4,
            "month": 11,
            "year": 2023,
            "source_reserve": {
                "name": "Etosha National Park",
                "country": "Namibia",
                "latitude": -19.1544,
                "longitude": 15.9463
            },
            "recipient_reserve": {
                "name": "Waterberg Plateau Park",
                "country": "Namibia",
                "latitude": -20.4500,
                "longitude": 17.2333
            },
            "transport_mode": "road",
            "additional_notes": "Black rhino genetic diversity program"
        },
        {
            "species": "elephant",
            "number_of_animals": 35,
            "month": 8,
            "year": 2024,
            "source_reserve": {
                "name": "Tsavo East National Park",
                "country": "Kenya",
                "latitude": -2.6816,
                "longitude": 38.4481
            },
            "recipient_reserve": {
                "name": "Amboseli National Park",
                "country": "Kenya",
                "latitude": -2.6527,
                "longitude": 37.2606
            },
            "transport_mode": "road",
            "additional_notes": "Habitat restoration project relocation"
        },
        {
            "species": "rhino",
            "number_of_animals": 6,
            "month": 1,
            "year": 2024,
            "source_reserve": {
                "name": "Pilanesberg National Park",
                "country": "South Africa",
                "latitude": -25.2394,
                "longitude": 27.0767
            },
            "recipient_reserve": {
                "name": "Chobe National Park",
                "country": "Botswana",
                "latitude": -18.5539,
                "longitude": 24.0303
            },
            "transport_mode": "air",
            "additional_notes": "Cross-border conservation initiative"
        }
    ]
    
    created_translocations = []
    for sample in sample_translocations:
        translocation_obj = Translocation(**sample)
        await db.translocations.insert_one(translocation_obj.dict())
        created_translocations.append(translocation_obj)
    
    return {"message": f"Created {len(created_translocations)} sample translocations", "translocations": created_translocations}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
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