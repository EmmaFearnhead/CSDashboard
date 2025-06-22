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
    ROAD = "Road"
    AIR = "Air"

class Species(str, Enum):
    ELEPHANT = "Elephant"
    BLACK_RHINO = "Black Rhino"
    WHITE_RHINO = "White Rhino"
    LION = "Lion"
    BUFFALO = "Buffalo"
    IMPALA = "Impala"
    SABLE = "Sable"
    KUDU = "Kudu"
    WARTHOG = "Warthog"
    WATERBUCK = "Waterbuck"
    ELAND = "Eland"
    ZEBRA = "Zebra"
    OTHER = "Other"

class SpecialProject(str, Enum):
    PEACE_PARKS = "Peace Parks"
    AFRICAN_PARKS = "African Parks"
    RHINO_REWILD = "Rhino Rewild"
    NONE = ""

# Define Models
class Location(BaseModel):
    name: str
    coordinates: str
    country: str

class TranslocationCreate(BaseModel):
    project_title: str
    year: int
    species: Species
    number_of_animals: int
    source_area: Location
    recipient_area: Location
    transport: TransportMode
    special_project: Optional[SpecialProject] = SpecialProject.NONE
    additional_info: Optional[str] = ""

class Translocation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_title: str
    year: int
    species: Species
    number_of_animals: int
    source_area: Location
    recipient_area: Location
    transport: TransportMode
    special_project: SpecialProject
    additional_info: str
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
    transport: Optional[TransportMode] = None,
    special_project: Optional[SpecialProject] = None
):
    filter_dict = {}
    if species:
        filter_dict["species"] = species
    if year:
        filter_dict["year"] = year
    if transport:
        filter_dict["transport"] = transport
    if special_project:
        filter_dict["special_project"] = special_project
    
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

@api_router.put("/translocations/{translocation_id}", response_model=Translocation)
async def update_translocation(translocation_id: str, translocation: TranslocationCreate):
    translocation_dict = translocation.dict()
    result = await db.translocations.update_one(
        {"id": translocation_id}, 
        {"$set": translocation_dict}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Translocation not found")
    
    updated_translocation = await db.translocations.find_one({"id": translocation_id})
    return Translocation(**updated_translocation)

@api_router.post("/translocations/import-historical")
async def import_historical_data():
    """Import the user's complete historical translocation data"""
    
    historical_data = [
        # 2016-2017 Projects
        {
            "project_title": "500 Elephants",
            "year": 2016,
            "species": "Elephant",
            "number_of_animals": 500,
            "source_area": {"name": "Liwonde National Park", "coordinates": "-14.843917138011093, -35.346718672081", "country": "Malawi"},
            "recipient_area": {"name": "Nkhotakota National Park", "coordinates": "-12.798572066646505, -34.0114801594613", "country": "Malawi"},
            "transport": "Road",
            "special_project": "African Parks",
            "additional_info": ""
        },
        {
            "project_title": "500 Elephants",
            "year": 2017,
            "species": "Elephant", 
            "number_of_animals": 150,
            "source_area": {"name": "Liwonde National Park", "coordinates": "-14.843917138011093, -35.346718672081", "country": "Malawi"},
            "recipient_area": {"name": "Nkhotakota National Park", "coordinates": "-12.798572066646505, -34.0114801594613", "country": "Malawi"},
            "transport": "Road",
            "special_project": "African Parks",
            "additional_info": ""
        },
        {
            "project_title": "Buffalo Kloof Elies",
            "year": 2017,
            "species": "Elephant",
            "number_of_animals": 10,
            "source_area": {"name": "Mankgawe Private Game Reserve", "coordinates": "-35.14358903356, -23.39279790103946", "country": "South Africa"},
            "recipient_area": {"name": "Buffalo Kloof", "coordinates": "-33.408619412724946, -33.6080821090958", "country": "South Africa"},
            "transport": "Road",
            "special_project": "",
            "additional_info": ""
        },
        {
            "project_title": "Buffalo Kloof Elies",
            "year": 2017,
            "species": "Elephant",
            "number_of_animals": 2,
            "source_area": {"name": "Mankgawe Private Game Reserve", "coordinates": "-35.14358903356, -23.39279790103946", "country": "South Africa"},
            "recipient_area": {"name": "Buffalo Kloof", "coordinates": "-33.408619412724946, -33.6080821090958", "country": "South Africa"},
            "transport": "Road",
            "special_project": "",
            "additional_info": ""
        },
        {
            "project_title": "Black Rhino Akagera",
            "year": 2017,
            "species": "Black Rhino",
            "number_of_animals": 18,
            "source_area": {"name": "Thaba Tholo", "coordinates": "-24.52810027320283, -27.86500001521125", "country": "South Africa"},
            "recipient_area": {"name": "Akagera National Park", "coordinates": "-1.879435086486515, -30.796346402720666", "country": "Rwanda"},
            "transport": "Air",
            "special_project": "African Parks",
            "additional_info": ""
        },
        {
            "project_title": "Nyika Elephants",
            "year": 2017,
            "species": "Elephant",
            "number_of_animals": 34,
            "source_area": {"name": "Liwonde National Park", "coordinates": "-14.843917138011093, -35.346718672081", "country": "Malawi"},
            "recipient_area": {"name": "Nyika National Park", "coordinates": "-10.796818680346909, -33.75203456365907", "country": "Malawi"},
            "transport": "Road",
            "special_project": "African Parks",
            "additional_info": ""
        },
        
        # 2018 Projects
        {
            "project_title": "Zimbabwe Elephant Nursery",
            "year": 2018,
            "species": "Elephant",
            "number_of_animals": 6,
            "source_area": {"name": "Zimbabwe Elephant Nursery", "coordinates": "-31.86027869063172, -25.850754187789392", "country": "Zimbabwe"},
            "recipient_area": {"name": "Panda Masuie National Park", "coordinates": "-25.850754187789392, -21.87866026637094", "country": "Zimbabwe"},
            "transport": "Road",
            "special_project": "",
            "additional_info": ""
        },
        {
            "project_title": "Zinave Elephant",
            "year": 2018,
            "species": "Elephant",
            "number_of_animals": 29,
            "source_area": {"name": "Liwonde National Park", "coordinates": "-14.843917138011093, -35.346718672081", "country": "South Africa"},
            "recipient_area": {"name": "Zinave National Park", "coordinates": "-21.878662063709046, -33.54986987480505", "country": "Mozambique"},
            "transport": "Road",
            "special_project": "Peace Parks",
            "additional_info": ""
        },
        {
            "project_title": "Zinave Elephant",
            "year": 2018,
            "species": "Elephant",
            "number_of_animals": 34,
            "source_area": {"name": "Liwonde National Park", "coordinates": "-14.843917138011093, -35.346718672081", "country": "South Africa"},
            "recipient_area": {"name": "Zinave National Park", "coordinates": "-21.878662063709046, -33.54986987480505", "country": "Mozambique"},
            "transport": "Road",
            "special_project": "Peace Parks",
            "additional_info": ""
        },
        
        # 2019 Projects
        {
            "project_title": "Moremi Giants",
            "year": 2019,
            "species": "Elephant",
            "number_of_animals": 195,
            "source_area": {"name": "Venetia Limpopo Nature Reserve", "coordinates": "-22.363459913668371, -29.506456275701714", "country": "South Africa"},
            "recipient_area": {"name": "Zinave National Park", "coordinates": "-21.878662063709046, -33.54986987480505", "country": "Mozambique"},
            "transport": "Road",
            "special_project": "Peace Parks",
            "additional_info": ""
        },
        {
            "project_title": "Gourundi Rhino",
            "year": 2019,
            "species": "Black Rhino",
            "number_of_animals": 9,
            "source_area": {"name": "Thaba Tholo", "coordinates": "-24.52810027320283, -27.86500001521125", "country": "South Africa"},
            "recipient_area": {"name": "Gourundi", "coordinates": "-34.21540248209099, -14.21540248209099", "country": "Tanzania"},
            "transport": "Air",
            "special_project": "",
            "additional_info": ""
        },
        
        # 2020 Projects
        {
            "project_title": "Senabianda Bull",
            "year": 2020,
            "species": "Elephant",
            "number_of_animals": 1,
            "source_area": {"name": "Tembe Elephant Park", "coordinates": "-27.047303859625, -32.47606133960426", "country": "South Africa"},
            "recipient_area": {"name": "Senabianda", "coordinates": "-27.500906056956502, -31.34656459950664", "country": "South Africa"},
            "transport": "Road",
            "special_project": "",
            "additional_info": ""
        },
        {
            "project_title": "Buffalo Kloof Bulls",
            "year": 2020,
            "species": "Elephant",
            "number_of_animals": 2,
            "source_area": {"name": "Tembe Elephant Park", "coordinates": "-27.047303859625, -32.47606133960426", "country": "South Africa"},
            "recipient_area": {"name": "Buffalo Kloof", "coordinates": "-36.5394472005988, -27.3910631008113406", "country": "South Africa"},
            "transport": "Road",
            "special_project": "",
            "additional_info": ""
        },
        {
            "project_title": "Orphan Rhino",
            "year": 2020,
            "species": "White Rhino",
            "number_of_animals": 2,
            "source_area": {"name": "Buyeni Hluhluwe Community Reserve", "coordinates": "-27.845409735054978, -32.06401315111046", "country": "South Africa"},
            "recipient_area": {"name": "Buffalo Kloof", "coordinates": "-36.5394472005988, -27.3910631008113406", "country": "South Africa"},
            "transport": "Road",
            "special_project": "",
            "additional_info": ""
        },
        
        # Continue with remaining years...
        {
            "project_title": "Maputo National Park Elephants",
            "year": 2020,
            "species": "Elephant",
            "number_of_animals": 30,
            "source_area": {"name": "Maputo National Park", "coordinates": "-26.433995001137733, -32.794531173528485", "country": "Mozambique"},
            "recipient_area": {"name": "Zinave National Park", "coordinates": "-21.878662063709046, -33.54986987480505", "country": "Mozambique"},
            "transport": "Road",
            "special_project": "Peace Parks",
            "additional_info": ""
        },
        
        # Add more recent projects (2021-2023)
        {
            "project_title": "Akagera White Rhino",
            "year": 2021,
            "species": "White Rhino",
            "number_of_animals": 30,
            "source_area": {"name": "Phinda Private Game Reserve", "coordinates": "-27.830400013406563, -32.32901013437949", "country": "South Africa"},
            "recipient_area": {"name": "Akagera National Park", "coordinates": "-1.879435086486515, -30.796346402720666", "country": "Rwanda"},
            "transport": "Road",
            "special_project": "African Parks",
            "additional_info": ""
        },
        {
            "project_title": "Kasungu Elephants",
            "year": 2022,
            "species": "Elephant",
            "number_of_animals": 263,
            "source_area": {"name": "Liwonde National Park", "coordinates": "-14.843917138011093, -35.346718672081", "country": "Malawi"},
            "recipient_area": {"name": "Kasungu National Park", "coordinates": "-12.897171470695018, -33.7503016604216", "country": "Malawi"},
            "transport": "Road",
            "special_project": "African Parks",
            "additional_info": ""
        }
    ]
    
    created_translocations = []
    for data in historical_data:
        translocation_obj = Translocation(**data)
        await db.translocations.insert_one(translocation_obj.dict())
        created_translocations.append(translocation_obj)
    
    return {"message": f"Imported {len(created_translocations)} historical translocations", "translocations": created_translocations}

@api_router.post("/translocations/sample-data")
async def create_sample_data():
    # Keep the existing sample data for demo purposes
    sample_translocations = [
        {
            "project_title": "Sample Elephant Translocation",
            "year": 2023,
            "species": "Elephant",
            "number_of_animals": 25,
            "source_area": {
                "name": "Kruger National Park",
                "coordinates": "-24.0063, 31.4953",
                "country": "South Africa"
            },
            "recipient_area": {
                "name": "Addo Elephant National Park", 
                "coordinates": "-33.4734, 25.7519",
                "country": "South Africa"
            },
            "transport": "Road",
            "special_project": "Peace Parks",
            "additional_info": "Sample family herd relocation"
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