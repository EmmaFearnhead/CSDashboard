# 1. Imports
import os
import pandas as pd
import io
import logging
import uuid
import traceback
from datetime import datetime
from typing import List, Optional
from enum import Enum

# FastAPI and Database
from fastapi import FastAPI, APIRouter, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient

# 2. MongoDB Setup
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DATABASE_NAME = "conservation_dashboard"

client = AsyncIOMotorClient(MONGO_URL)
db = client[DATABASE_NAME]

# 3. Pydantic Models
class Transport(str, Enum):
    ROAD = "Road"
    AIR = "Air"

class Species(str, Enum):
    ELEPHANT = "Elephant"
    BLACK_RHINO = "Black Rhino"
    WHITE_RHINO = "White Rhino"
    PLAINS_GAME = "Plains Game Species"
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

class Translocation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_title: str
    year: int
    species: Species
    number_of_animals: int
    source_area: Location
    recipient_area: Location
    transport: Transport
    special_project: str = ""
    additional_info: str = ""
    created_at: datetime = Field(default_factory=datetime.now)

# 4. API Setup
app = FastAPI()
api_router = APIRouter()

# API endpoints
@api_router.get("/")
async def health_check():
    return {"message": "Wildlife Conservation Dashboard API"}

@api_router.get("/translocations")
async def get_translocations():
    translocations = []
    async for translocation in db.translocations.find():
        translocations.append(translocation)
    return translocations

@api_router.get("/translocations/stats")
async def get_stats():
    pipeline = [
        {
            "$group": {
                "_id": "$species",
                "total_animals": {"$sum": "$number_of_animals"},
                "total_translocations": {"$sum": 1}
            }
        }
    ]
    
    stats = {}
    async for result in db.translocations.aggregate(pipeline):
        stats[result["_id"]] = {
            "total_animals": result["total_animals"],
            "total_translocations": result["total_translocations"]
        }
    
    return stats

@api_router.post("/translocations")
async def create_translocation(translocation: Translocation):
    result = await db.translocations.insert_one(translocation.dict())
    return {"id": str(result.inserted_id), "message": "Translocation created successfully"}

@api_router.put("/translocations/{translocation_id}")
async def update_translocation(translocation_id: str, translocation: Translocation):
    result = await db.translocations.update_one(
        {"id": translocation_id},
        {"$set": translocation.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Translocation not found")
    return {"message": "Translocation updated successfully"}

@api_router.delete("/translocations/{translocation_id}")
async def delete_translocation(translocation_id: str):
    result = await db.translocations.delete_one({"id": translocation_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Translocation not found")
    return {"message": "Translocation deleted successfully"}

@api_router.post("/translocations/import-simplified-data")
async def import_simplified_data():
    """Import simplified conservation data with 5 species categories"""
    
    # Clear existing data
    await db.translocations.delete_many({})
    
    # Simplified dataset with 5 categories: Elephant, Black Rhino, White Rhino, Plains Game Species, Other
    simplified_data = [
        # Elephants - keep as "Elephant" 
        {"project_title": "500 Elephants", "year": 2016, "species": "Elephant", "number_of_animals": 366, "source_area": {"name": "Liwonde National Park", "coordinates": "-14.843917, 35.346718", "country": "Malawi"}, "recipient_area": {"name": "Nkhotakota National Park", "coordinates": "-12.798572, 34.011480", "country": "Malawi"}, "transport": "Road", "special_project": "African Parks", "additional_info": ""},
        {"project_title": "500 Elephants", "year": 2017, "species": "Elephant", "number_of_animals": 156, "source_area": {"name": "Majete Wildlife Reserve", "coordinates": "-16.009218, 35.015772", "country": "Malawi"}, "recipient_area": {"name": "Nkhotakota National Park", "coordinates": "-12.798572, 34.011480", "country": "Malawi"}, "transport": "Road", "special_project": "African Parks", "additional_info": ""},
        {"project_title": "Buffalo Kloof Elies", "year": 2017, "species": "Elephant", "number_of_animals": 10, "source_area": {"name": "Mankgawe Private Game Reserve", "coordinates": "-25.144, 27.393", "country": "South Africa"}, "recipient_area": {"name": "Buffalo Kloof", "coordinates": "-33.409, 25.608", "country": "South Africa"}, "transport": "Road", "special_project": "", "additional_info": ""},
        {"project_title": "Buffalo Kloof Elies", "year": 2017, "species": "Elephant", "number_of_animals": 2, "source_area": {"name": "Mankgawe Private Game Reserve", "coordinates": "-25.144, 27.393", "country": "South Africa"}, "recipient_area": {"name": "Buffalo Kloof", "coordinates": "-33.409, 25.608", "country": "South Africa"}, "transport": "Road", "special_project": "", "additional_info": ""},
        {"project_title": "Nyika Elephants", "year": 2017, "species": "Elephant", "number_of_animals": 34, "source_area": {"name": "Liwonde National Park", "coordinates": "-14.844, 35.347", "country": "Malawi"}, "recipient_area": {"name": "Nyika National Park", "coordinates": "-10.797, 33.752", "country": "Malawi"}, "transport": "Road", "special_project": "African Parks", "additional_info": ""},
        {"project_title": "Zimbabwe Elephant Nursery", "year": 2018, "species": "Elephant", "number_of_animals": 6, "source_area": {"name": "Zimbabwe Elephant Nursery", "coordinates": "-17.825, 31.053", "country": "Zimbabwe"}, "recipient_area": {"name": "Panda Masuie National Park", "coordinates": "-18.879, 25.879", "country": "Zimbabwe"}, "transport": "Road", "special_project": "", "additional_info": ""},
        {"project_title": "Zinave Elephant", "year": 2018, "species": "Elephant", "number_of_animals": 29, "source_area": {"name": "Liwonde National Park", "coordinates": "-14.844, 35.347", "country": "Malawi"}, "recipient_area": {"name": "Zinave National Park", "coordinates": "-21.879, 33.550", "country": "Mozambique"}, "transport": "Road", "special_project": "Peace Parks", "additional_info": ""},
        {"project_title": "Zinave Elephant", "year": 2018, "species": "Elephant", "number_of_animals": 34, "source_area": {"name": "Private Game Reserve", "coordinates": "-27.612, 31.280", "country": "South Africa"}, "recipient_area": {"name": "Zinave National Park", "coordinates": "-21.879, 33.550", "country": "Mozambique"}, "transport": "Road", "special_project": "Peace Parks", "additional_info": ""},
        {"project_title": "Moremi Giants", "year": 2019, "species": "Elephant", "number_of_animals": 101, "source_area": {"name": "Venetia Limpopo Nature Reserve", "coordinates": "-22.363, 29.506", "country": "South Africa"}, "recipient_area": {"name": "Zinave National Park", "coordinates": "-21.879, 33.550", "country": "Mozambique"}, "transport": "Road", "special_project": "Peace Parks", "additional_info": ""},
        {"project_title": "Emergency Relocation Elephant Bull Eastern Cape", "year": 2019, "species": "Elephant", "number_of_animals": 1, "source_area": {"name": "Eastern Cape", "coordinates": "-32.290, 26.408", "country": "South Africa"}, "recipient_area": {"name": "Mount Camdeboo", "coordinates": "-32.219, 24.630", "country": "South Africa"}, "transport": "Road", "special_project": "", "additional_info": ""},
        {"project_title": "Emergency Relocation Elephant Herd Eastern Cape", "year": 2019, "species": "Elephant", "number_of_animals": 11, "source_area": {"name": "Eastern Cape", "coordinates": "-32.290, 26.408", "country": "South Africa"}, "recipient_area": {"name": "Buffalo Kloof", "coordinates": "-33.409, 25.608", "country": "South Africa"}, "transport": "Road", "special_project": "", "additional_info": ""},
        {"project_title": "Senabianda Bull", "year": 2020, "species": "Elephant", "number_of_animals": 1, "source_area": {"name": "Tembe Elephant Park", "coordinates": "-27.047, 32.476", "country": "South Africa"}, "recipient_area": {"name": "Senabianda Community Reserve", "coordinates": "-27.501, 31.347", "country": "South Africa"}, "transport": "Road", "special_project": "", "additional_info": ""},
        {"project_title": "Buffalo Kloof Bulls", "year": 2020, "species": "Elephant", "number_of_animals": 2, "source_area": {"name": "Tembe Elephant Park", "coordinates": "-27.047, 32.476", "country": "South Africa"}, "recipient_area": {"name": "Buffalo Kloof", "coordinates": "-33.409, 25.608", "country": "South Africa"}, "transport": "Road", "special_project": "", "additional_info": ""},
        {"project_title": "Maputo National Park Elephants", "year": 2020, "species": "Elephant", "number_of_animals": 30, "source_area": {"name": "Maputo National Park", "coordinates": "-26.434, 32.795", "country": "Mozambique"}, "recipient_area": {"name": "Zinave National Park", "coordinates": "-21.879, 33.550", "country": "Mozambique"}, "transport": "Road", "special_project": "Peace Parks", "additional_info": ""},
        {"project_title": "Phinda Elephant", "year": 2021, "species": "Elephant", "number_of_animals": 3, "source_area": {"name": "Phinda Game Reserve", "coordinates": "-27.830, 32.329", "country": "South Africa"}, "recipient_area": {"name": "Phinda Private Game Reserve", "coordinates": "-27.830, 32.329", "country": "South Africa"}, "transport": "Road", "special_project": "", "additional_info": ""},
        {"project_title": "Kasungu Elephants", "year": 2022, "species": "Elephant", "number_of_animals": 263, "source_area": {"name": "Liwonde National Park", "coordinates": "-14.844, 35.347", "country": "Malawi"}, "recipient_area": {"name": "Kasungu National Park", "coordinates": "-12.897, 33.750", "country": "Malawi"}, "transport": "Road", "special_project": "African Parks", "additional_info": ""},
        {"project_title": "Babanango Elephant", "year": 2023, "species": "Elephant", "number_of_animals": 7, "source_area": {"name": "Mankgawe Game Reserve", "coordinates": "-27.845, 32.064", "country": "South Africa"}, "recipient_area": {"name": "Babanango Game Reserve", "coordinates": "-28.340, 31.197", "country": "South Africa"}, "transport": "Road", "special_project": "", "additional_info": ""},
        {"project_title": "Babanango Elephant", "year": 2023, "species": "Elephant", "number_of_animals": 8, "source_area": {"name": "Addo Elephant National Park", "coordinates": "-33.390, 25.646", "country": "South Africa"}, "recipient_area": {"name": "Babanango Game Reserve", "coordinates": "-28.340, 31.197", "country": "South Africa"}, "transport": "Road", "special_project": "", "additional_info": ""},
        {"project_title": "Namibia Bulls", "year": 2023, "species": "Elephant", "number_of_animals": 2, "source_area": {"name": "Elephant Sands Game Reserve", "coordinates": "-19.981, 24.596", "country": "South Africa"}, "recipient_area": {"name": "Desert Reserve", "coordinates": "-22.938, 18.296", "country": "South Africa"}, "transport": "Road", "special_project": "", "additional_info": ""},
        {"project_title": "Asante Sana Elephant", "year": 2025, "species": "Elephant", "number_of_animals": 5, "source_area": {"name": "Addo Elephant National Park", "coordinates": "-33.390, 25.646", "country": "South Africa"}, "recipient_area": {"name": "Ubulozi Private Reserve", "coordinates": "-24.635, 30.970", "country": "South Africa"}, "transport": "Road", "special_project": "", "additional_info": ""},
        {"project_title": "Addo Elephant", "year": 2025, "species": "Elephant", "number_of_animals": 30, "source_area": {"name": "Addo Elephant National Park", "coordinates": "-33.390, 25.646", "country": "South Africa"}, "recipient_area": {"name": "Addo Elephant National Park", "coordinates": "-24.362, 30.962", "country": "South Africa"}, "transport": "Road", "special_project": "", "additional_info": ""},

        # Black Rhinos - keep as "Black Rhino"
        {"project_title": "Black Rhino Akagera", "year": 2017, "species": "Black Rhino", "number_of_animals": 18, "source_area": {"name": "Thaba Tholo", "coordinates": "-24.528, 27.865", "country": "South Africa"}, "recipient_area": {"name": "Akagera National Park", "coordinates": "-1.879, 30.796", "country": "Rwanda"}, "transport": "Air", "special_project": "African Parks", "additional_info": ""},
        {"project_title": "Gourundi Rhino", "year": 2019, "species": "Black Rhino", "number_of_animals": 9, "source_area": {"name": "Thaba Tholo", "coordinates": "-24.528, 27.865", "country": "South Africa"}, "recipient_area": {"name": "Mount Camdeboo", "coordinates": "-4.215, 34.215", "country": "Tanzania"}, "transport": "Air", "special_project": "", "additional_info": ""},
        {"project_title": "Liwonde Black Rhino", "year": 2019, "species": "Black Rhino", "number_of_animals": 17, "source_area": {"name": "Ezemvelo", "coordinates": "-28.211, 31.655", "country": "South Africa"}, "recipient_area": {"name": "Liwonde National Park", "coordinates": "-14.844, 35.347", "country": "Malawi"}, "transport": "Air", "special_project": "African Parks", "additional_info": ""},
        {"project_title": "Zinave Black Rhino", "year": 2022, "species": "Black Rhino", "number_of_animals": 7, "source_area": {"name": "Hluhluwe Game Reserve", "coordinates": "-27.345, 32.065", "country": "South Africa"}, "recipient_area": {"name": "Zinave National Park", "coordinates": "-21.879, 33.550", "country": "Mozambique"}, "transport": "Road", "special_project": "Peace Parks", "additional_info": ""},
        {"project_title": "Zinave Black Rhino", "year": 2023, "species": "Black Rhino", "number_of_animals": 10, "source_area": {"name": "Hluhluwe Game Reserve", "coordinates": "-28.062, 32.125", "country": "South Africa"}, "recipient_area": {"name": "Zinave National Park", "coordinates": "-21.879, 33.550", "country": "Mozambique"}, "transport": "Road", "special_project": "Peace Parks", "additional_info": ""},
        {"project_title": "Zakouma Rhino", "year": 2023, "species": "Black Rhino", "number_of_animals": 6, "source_area": {"name": "Thaba Tholo", "coordinates": "-24.528, 27.865", "country": "South Africa"}, "recipient_area": {"name": "Zakouma National Park", "coordinates": "10.837, 19.831", "country": "Chad"}, "transport": "Air", "special_project": "African Parks", "additional_info": "Plane: C130"},
        {"project_title": "Zinave Black Rhino", "year": 2025, "species": "Black Rhino", "number_of_animals": 10, "source_area": {"name": "Hluhluwe Game Reserve", "coordinates": "-27.345, 32.065", "country": "South Africa"}, "recipient_area": {"name": "Zinave National Park", "coordinates": "-21.879, 33.550", "country": "Mozambique"}, "transport": "Road", "special_project": "Peace Parks", "additional_info": ""},

        # White Rhinos - keep as "White Rhino"  
        {"project_title": "Orphan Rhino", "year": 2020, "species": "White Rhino", "number_of_animals": 2, "source_area": {"name": "Mankgawe Game Reserve", "coordinates": "-27.845, 32.064", "country": "South Africa"}, "recipient_area": {"name": "Senabianda Community Reserve", "coordinates": "-27.594, 31.842", "country": "South Africa"}, "transport": "Road", "special_project": "", "additional_info": ""},
        {"project_title": "Akagera White Rhino", "year": 2021, "species": "White Rhino", "number_of_animals": 30, "source_area": {"name": "Phinda Private Game Reserve", "coordinates": "-27.830, 32.329", "country": "South Africa"}, "recipient_area": {"name": "Akagera National Park", "coordinates": "-1.879, 30.796", "country": "Rwanda"}, "transport": "Road", "special_project": "African Parks", "additional_info": ""},
        {"project_title": "Zinave White Rhino", "year": 2022, "species": "White Rhino", "number_of_animals": 40, "source_area": {"name": "Hluhluwe Game Reserve", "coordinates": "-28.062, 32.162", "country": "South Africa"}, "recipient_area": {"name": "Zinave National Park", "coordinates": "-21.879, 33.550", "country": "Mozambique"}, "transport": "Road", "special_project": "Peace Parks", "additional_info": ""},
        {"project_title": "Zinave White Rhino", "year": 2023, "species": "White Rhino", "number_of_animals": 27, "source_area": {"name": "Mankgawe Game Reserve", "coordinates": "-23.855, 32.125", "country": "South Africa"}, "recipient_area": {"name": "Zinave National Park", "coordinates": "-21.879, 33.550", "country": "Mozambique"}, "transport": "Road", "special_project": "Peace Parks", "additional_info": ""},
        {"project_title": "Akagera White Rhino", "year": 2025, "species": "White Rhino", "number_of_animals": 70, "source_area": {"name": "Phinda Private Game Reserve", "coordinates": "-27.830, 32.329", "country": "South Africa"}, "recipient_area": {"name": "Akagera National Park", "coordinates": "-1.879, 30.796", "country": "Rwanda"}, "transport": "Air", "special_project": "African Parks", "additional_info": "Two Loads of 35 Rhino - Boeing 747"},
        {"project_title": "Ngorongoro Crater Rhino", "year": 2025, "species": "White Rhino", "number_of_animals": 17, "source_area": {"name": "Phinda Private Game Reserve", "coordinates": "-27.830, 32.329", "country": "South Africa"}, "recipient_area": {"name": "Ngorongoro Crater", "coordinates": "-3.162, 35.582", "country": "Tanzania"}, "transport": "Air", "special_project": "", "additional_info": "Boeing 767"},

        # Single species other animals - categorize as "Other"
        {"project_title": "Akagera Lions", "year": 2023, "species": "Other", "number_of_animals": 7, "source_area": {"name": "Phinda Private Game Reserve", "coordinates": "-27.830, 32.329", "country": "South Africa"}, "recipient_area": {"name": "Akagera National Park", "coordinates": "-1.879, 30.796", "country": "Rwanda"}, "transport": "Air", "special_project": "", "additional_info": "Primary species: Lion"},
        {"project_title": "Ewangoula Buffalo", "year": 2018, "species": "Other", "number_of_animals": 196, "source_area": {"name": "North Luangwa National Park", "coordinates": "-11.889, 32.140", "country": "Zambia"}, "recipient_area": {"name": "Bangweulu Wetlands", "coordinates": "-11.937, 34.342", "country": "Zambia"}, "transport": "Road", "special_project": "African Parks", "additional_info": "Primary species: Buffalo"},
        {"project_title": "Niassa National Park Buffalo", "year": 2021, "species": "Other", "number_of_animals": 200, "source_area": {"name": "North Luangwa National Park", "coordinates": "-11.889, 32.140", "country": "Zambia"}, "recipient_area": {"name": "Niassa National Park", "coordinates": "-8.796, 37.936", "country": "Mozambique"}, "transport": "Road", "special_project": "", "additional_info": "Primary species: Buffalo"},
        {"project_title": "Gorongosa Buffalo", "year": 2022, "species": "Other", "number_of_animals": 16, "source_area": {"name": "Zinave National Park", "coordinates": "-21.879, 33.550", "country": "Mozambique"}, "recipient_area": {"name": "Gorongosa National Park", "coordinates": "-18.973, 34.536", "country": "Mozambique"}, "transport": "Road", "special_project": "Peace Parks", "additional_info": "Primary species: Buffalo"},
        {"project_title": "Zakouma Buffalo", "year": 2022, "species": "Other", "number_of_animals": 268, "source_area": {"name": "Hluhluwe iMfolozi Park", "coordinates": "-28.256, 31.969", "country": "South Africa"}, "recipient_area": {"name": "Simala Moma", "coordinates": "10.531, 19.255", "country": "Chad"}, "transport": "Road", "special_project": "African Parks", "additional_info": "Primary species: Buffalo"},

        # Multi-species entries - categorize as "Plains Game Species"
        {"project_title": "Nkhotakota plains game", "year": 2016, "species": "Plains Game Species", "number_of_animals": 1500, "source_area": {"name": "Liwonde National Park", "coordinates": "-14.844, 35.347", "country": "Malawi"}, "recipient_area": {"name": "Nkhotakota National Park", "coordinates": "-12.799, 34.011", "country": "Malawi"}, "transport": "Road", "special_project": "African Parks", "additional_info": "Buffalo, island, impala, kudu, sable, zebra, warthog, waterbuck, hartebeest"},
        {"project_title": "Zinave Plains Game", "year": 2019, "species": "Plains Game Species", "number_of_animals": 388, "source_area": {"name": "Gouritse South Park and Maputo National Park", "coordinates": "-26.791, 32.699", "country": "Mozambique"}, "recipient_area": {"name": "Zinave National Park", "coordinates": "-21.879, 33.550", "country": "Mozambique"}, "transport": "Road", "special_project": "Peace Parks", "additional_info": "Sable, Oryx, Waterbuck & Reedbuck"},
        {"project_title": "Kasungu Plains Game", "year": 2022, "species": "Plains Game Species", "number_of_animals": 423, "source_area": {"name": "Liwonde National Park", "coordinates": "-14.844, 35.347", "country": "Malawi"}, "recipient_area": {"name": "Kasungu National Park", "coordinates": "-12.897, 33.750", "country": "Malawi"}, "transport": "Road", "special_project": "African Parks", "additional_info": "Buffalo (84); Impala (127); Sable (29); Warthog (86); Kudu (46); Hartebeest (32)"},
        {"project_title": "Mangochi Plains Game", "year": 2022, "species": "Plains Game Species", "number_of_animals": 221, "source_area": {"name": "Liwonde National Park", "coordinates": "-14.844, 35.347", "country": "Malawi"}, "recipient_area": {"name": "Mangochi Forest Reserve", "coordinates": "-14.436, 35.256", "country": "Malawi"}, "transport": "Road", "special_project": "African Parks", "additional_info": "Impala (94); Kudu (48); Hartebeest (30); Warthog (36); Sable (12); Waterbuck (12)"},
        {"project_title": "Niassa Plains Game", "year": 2022, "species": "Plains Game Species", "number_of_animals": 40, "source_area": {"name": "Liwonde National Park", "coordinates": "-14.844, 35.347", "country": "Malawi"}, "recipient_area": {"name": "Niassa Forest Reserve", "coordinates": "-14.526, 36.435", "country": "Malawi"}, "transport": "Road", "special_project": "African Parks", "additional_info": "Sable (8); Kudu (12); Warthog (14); Eland (6)"},
        {"project_title": "Nkhotakota plains game", "year": 2022, "species": "Plains Game Species", "number_of_animals": 711, "source_area": {"name": "Liwonde National Park", "coordinates": "-14.844, 35.347", "country": "Malawi"}, "recipient_area": {"name": "Nkhotakota National Park", "coordinates": "-12.799, 34.011", "country": "Malawi"}, "transport": "Road", "special_project": "African Parks", "additional_info": "Buffalo (96); Impala (217); Sable (96); Warthog (75); Kudu (79)"},
        {"project_title": "Nkhotakota plains game", "year": 2022, "species": "Plains Game Species", "number_of_animals": 79, "source_area": {"name": "Majete Wildlife Reserve", "coordinates": "-16.009, 35.016", "country": "Malawi"}, "recipient_area": {"name": "Nkhotakota National Park", "coordinates": "-12.799, 34.011", "country": "Malawi"}, "transport": "Road", "special_project": "African Parks", "additional_info": "Zebra (27); Eland (20); Kudu (32)"},
        {"project_title": "Nkhotakota plains game", "year": 2022, "species": "Plains Game Species", "number_of_animals": 15, "source_area": {"name": "Liwonde National Park", "coordinates": "-14.844, 35.347", "country": "Malawi"}, "recipient_area": {"name": "Nkhotakota National Park", "coordinates": "-12.799, 34.011", "country": "Malawi"}, "transport": "Road", "special_project": "African Parks", "additional_info": "Buffalo (8); Impala (4); Warthog (3)"},
        {"project_title": "Liwonde Plains Game", "year": 2022, "species": "Plains Game Species", "number_of_animals": 25, "source_area": {"name": "Majete Wildlife Reserve", "coordinates": "-16.009, 35.016", "country": "Malawi"}, "recipient_area": {"name": "Liwonde National Park", "coordinates": "-14.844, 35.347", "country": "Malawi"}, "transport": "Road", "special_project": "African Parks", "additional_info": "Zebra (15); Kudu (10)"},
        {"project_title": "Mangochi Plains Game", "year": 2022, "species": "Plains Game Species", "number_of_animals": 40, "source_area": {"name": "Majete Wildlife Reserve", "coordinates": "-16.009, 35.016", "country": "Malawi"}, "recipient_area": {"name": "Mangochi Forest Reserve", "coordinates": "-14.436, 35.256", "country": "Malawi"}, "transport": "Road", "special_project": "African Parks", "additional_info": "Kudu (22); Hartebeest (18)"}
    ]
    
    created_translocations = []
    for data in simplified_data:
        translocation_obj = Translocation(**data)
        await db.translocations.insert_one(translocation_obj.dict())
        created_translocations.append(translocation_obj)
    
    return {"message": f"Imported {len(created_translocations)} translocations with simplified species categorization", "translocations": created_translocations}

@api_router.post("/translocations/import-excel-file")
async def import_excel_file(file: UploadFile = File(...)):
    """Import translocation data from Excel or CSV file upload"""
    
    def validate_coordinates(coord_string):
        """Validate and format coordinates for Google Maps format"""
        if not coord_string or pd.isna(coord_string) or str(coord_string).strip() == "":
            return "0, 0"
        
        try:
            # Clean the coordinate string
            clean_coords = str(coord_string).replace("°", "").replace("'", "").replace('"', "").strip()
            
            # Handle Google Maps format: "-27.808400634565363, 32.34692072433984"
            if "," in clean_coords:
                parts = clean_coords.split(",")
                if len(parts) >= 2:
                    lat = float(parts[0].strip())
                    lng = float(parts[1].strip())
                    
                    # Validate coordinates are reasonable for Africa
                    # Africa latitude range: roughly -35 to 37
                    # Africa longitude range: roughly -20 to 52
                    if (-40 <= lat <= 40) and (-25 <= lng <= 55):
                        return f"{lat}, {lng}"
                    else:
                        print(f"Warning: Coordinates outside Africa range: {clean_coords}")
                        return "0, 0"
            
            return "0, 0"
        except Exception as e:
            print(f"Error validating coordinates '{coord_string}': {e}")
            return "0, 0"
    
    def categorize_species(original_species, additional_info=""):
        """Categorize species with proper validation"""
        if pd.isna(original_species) or not original_species:
            return "Other"
                
        species_str = str(original_species).strip()
        additional_str = str(additional_info) if not pd.isna(additional_info) else ""
        
        # Direct mapping for primary species
        if "elephant" in species_str.lower():
            return "Elephant"
        elif "black rhino" in species_str.lower():
            return "Black Rhino"
        elif "white rhino" in species_str.lower():
            return "White Rhino"
        elif "plains game" in species_str.lower():
            return "Plains Game Species"
        else:
            # Check if this is a multi-species entry based on additional info
            multi_species_keywords = ["buffalo", "impala", "sable", "kudu", "warthog", "waterbuck", "eland", "zebra", "hartebeest", "reedbuck", "oryx"]
            species_count = sum(1 for keyword in multi_species_keywords if keyword.lower() in additional_str.lower())
            
            # If additional_info mentions multiple species or has separators, it's Plains Game
            if species_count >= 2 or ";" in additional_str or ("," in additional_str and any(keyword in additional_str.lower() for keyword in multi_species_keywords)):
                return "Plains Game Species"
            else:
                # Return "Other" for single species that aren't the main categories
                return "Other"
    
    try:
        # Clear existing data first
        delete_result = await db.translocations.delete_many({})
        print(f"Cleared {delete_result.deleted_count} existing records")
        
        # Read file content
        content = await file.read()
        
        # Determine file type and read accordingly
        if file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
            # Read Excel file
            df = pd.read_excel(io.BytesIO(content))
        elif file.filename.endswith('.csv'):
            # Read CSV file
            df = pd.read_csv(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="File must be Excel (.xlsx, .xls) or CSV (.csv)")
        
        print(f"File read successfully. Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # Column mapping - handle different possible column names
        column_mapping = {
            'project_title': ['Project Title', 'project_title', 'Project', 'Title'],
            'year': ['Year', 'year'],
            'species': ['Species', 'species'],
            'number_of_animals': ['Number', 'number', 'Number of Animals', 'Animals', 'Count'],
            'source_name': ['Source Area: Name', 'Source Name', 'Source Area Name', 'source_name'],
            'source_coordinates': ['Source Area: Co-Ordinates', 'Source Coordinates', 'Source Area Coordinates', 'source_coordinates'],
            'source_country': ['Source Area: Country', 'Source Country', 'Source Area Country', 'source_country'],
            'recipient_name': ['Recipient Area: Name', 'Recipient Name', 'Recipient Area Name', 'recipient_name'],
            'recipient_coordinates': ['Recipient Area: Co-Ordinates', 'Recipient Coordinates', 'Recipient Area Coordinates', 'recipient_coordinates'],
            'recipient_country': ['Recipient Area: Country', 'Recipient Country', 'Recipient Area Country', 'recipient_country'],
            'transport': ['Transport', 'transport'],
            'special_project': ['Special Project', 'special_project', 'Special'],
            'additional_info': ['Additional Info', 'additional_info', 'Notes', 'Additional Information']
        }
        
        # Find the correct column names
        found_columns = {}
        for field, possible_names in column_mapping.items():
            for col_name in possible_names:
                if col_name in df.columns:
                    found_columns[field] = col_name
                    break
            if field not in found_columns:
                # If critical columns are missing, raise error
                if field in ['project_title', 'year', 'species', 'number_of_animals']:
                    print(f"CRITICAL: Missing required column '{field}'. Available columns: {list(df.columns)}")
                    raise HTTPException(status_code=400, detail=f"Required column not found: {field}. Available columns: {list(df.columns)}")
                else:
                    print(f"WARNING: Optional column '{field}' not found. Available columns: {list(df.columns)}")
        
        print(f"Column mapping: {found_columns}")
        
        # Validate that we have the minimum required columns
        required_fields = ['project_title', 'year', 'species', 'number_of_animals']
        missing_fields = [field for field in required_fields if field not in found_columns]
        if missing_fields:
            error_msg = f"Missing required columns: {missing_fields}. Available columns: {list(df.columns)}"
            print(f"CRITICAL ERROR: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Process each row
        created_translocations = []
        errors = []
        
        print(f"Starting to process {len(df)} rows...")
        
        for index, row in df.iterrows():
            try:
                print(f"\n=== Processing row {index+1} ===")
                print(f"Raw row data: {dict(row)}")
                
                # Extract data with proper error handling
                project_title = str(row[found_columns['project_title']]) if not pd.isna(row[found_columns['project_title']]) else f"Project {index+1}"
                print(f"Project title: {project_title}")
                
                # Handle year conversion
                year_val = row[found_columns['year']]
                if pd.isna(year_val):
                    year = 2024
                else:
                    year_str = str(year_val)
                    # Handle complex year formats like "2023 & 2023", "2022-2023", etc.
                    if '&' in year_str:
                        # Take the first year from "2023 & 2023"
                        year = int(year_str.split('&')[0].strip())
                    elif '-' in year_str and len(year_str.split('-')) == 2:
                        # Take the first year from "2022-2023"
                        year = int(year_str.split('-')[0].strip())
                    elif '/' in year_str:
                        # Take the first year from "2022/2023"
                        year = int(year_str.split('/')[0].strip())
                    else:
                        # Try normal conversion
                        try:
                            year = int(float(year_str))
                        except:
                            year = 2024  # Default fallback
                print(f"Year: {year}")
                
                # Handle number of animals
                number_val = row[found_columns['number_of_animals']]
                if pd.isna(number_val):
                    number_of_animals = 1
                else:
                    try:
                        number_of_animals = int(float(str(number_val)))
                    except:
                        number_of_animals = 1
                print(f"Number of animals: {number_of_animals}")
                
                # Get additional info first for species categorization
                additional_info_val = row[found_columns.get('additional_info', '')]
                additional_info = str(additional_info_val) if not pd.isna(additional_info_val) else ""
                if additional_info == 'nan':
                    additional_info = ""
                print(f"Additional info: {additional_info}")
                
                # Categorize species
                original_species = row[found_columns['species']] if not pd.isna(row[found_columns['species']]) else ""
                species = categorize_species(original_species, additional_info)
                print(f"Original species: {original_species} -> Categorized: {species}")
                
                # Validate species is one of our enum values
                valid_species = ["Elephant", "Black Rhino", "White Rhino", "Plains Game Species", "Other"]
                if species not in valid_species:
                    print(f"WARNING: Invalid species '{species}', defaulting to 'Other'")
                    species = "Other"
                
                # Source area
                source_name_val = row[found_columns.get('source_name', '')]
                source_name = str(source_name_val) if not pd.isna(source_name_val) else "Unknown Source"
                print(f"Source name: {source_name}")
                
                source_coordinates = validate_coordinates(row[found_columns.get('source_coordinates', '')])
                print(f"Source coordinates: {source_coordinates}")
                
                source_country_val = row[found_columns.get('source_country', '')]
                source_country = str(source_country_val) if not pd.isna(source_country_val) else "Unknown"
                print(f"Source country: {source_country}")
                
                # Recipient area
                recipient_name_val = row[found_columns.get('recipient_name', '')]
                recipient_name = str(recipient_name_val) if not pd.isna(recipient_name_val) else "Unknown Recipient"
                print(f"Recipient name: {recipient_name}")
                
                recipient_coordinates = validate_coordinates(row[found_columns.get('recipient_coordinates', '')])
                print(f"Recipient coordinates: {recipient_coordinates}")
                
                recipient_country_val = row[found_columns.get('recipient_country', '')]
                recipient_country = str(recipient_country_val) if not pd.isna(recipient_country_val) else "Unknown"
                print(f"Recipient country: {recipient_country}")
                
                # Transport and special project
                transport_val = row[found_columns.get('transport', '')]
                transport = str(transport_val) if not pd.isna(transport_val) else "Road"
                if transport.lower() not in ['road', 'air']:
                    transport = "Road"
                else:
                    transport = transport.capitalize()
                print(f"Transport: {transport}")
                
                special_project_val = row[found_columns.get('special_project', '')]
                special_project = str(special_project_val) if not pd.isna(special_project_val) else ""
                if special_project.lower() in ['nan', 'none', '']:
                    special_project = ""
                
                # Ensure special_project is a valid enum value
                valid_special_projects = ["Peace Parks", "African Parks", "Rhino Rewild", ""]
                if special_project not in valid_special_projects:
                    special_project = ""
                print(f"Special project: {special_project}")
                
                # Create translocation record
                translocation_data = {
                    "project_title": project_title,
                    "year": year,
                    "species": species,
                    "number_of_animals": number_of_animals,
                    "source_area": {
                        "name": source_name,
                        "coordinates": source_coordinates,
                        "country": source_country
                    },
                    "recipient_area": {
                        "name": recipient_name,
                        "coordinates": recipient_coordinates,
                        "country": recipient_country
                    },
                    "transport": transport,
                    "special_project": special_project,
                    "additional_info": additional_info
                }
                
                print(f"About to create Translocation object with data: {translocation_data}")
                
                translocation_obj = Translocation(**translocation_data)
                print(f"Created Translocation object successfully")
                
                result = await db.translocations.insert_one(translocation_obj.dict())
                print(f"Inserted into database with ID: {result.inserted_id}")
                
                created_translocations.append(translocation_obj)
                print(f"Row {index+1} processed successfully!")
                
            except Exception as row_error:
                error_msg = f"Error processing row {index+1}: {str(row_error)}"
                print(f"ERROR: {error_msg}")
                errors.append(error_msg)
                continue  # Skip problematic rows but continue processing
        
        success_message = f"Successfully imported {len(created_translocations)} translocations from {file.filename}"
        if errors:
            success_message += f". {len(errors)} rows had errors and were skipped."
        
        return {
            "message": success_message,
            "total_rows_processed": len(df),
            "successful_imports": len(created_translocations),
            "errors": errors[:5],  # Return first 5 errors for debugging
            "species_summary": {
                species: len([t for t in created_translocations if t.species == species])
                for species in set([t.species for t in created_translocations])
            }
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error processing file: {str(e)}")
        print(f"Detailed error: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

# 5. Setup FastAPI App
app.include_router(api_router, prefix="/api")

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