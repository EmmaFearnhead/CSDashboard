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
        # Remove MongoDB ObjectId for JSON serialization
        if '_id' in translocation:
            del translocation['_id']
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
    """Import translocation data from Excel or CSV file upload - ROBUST VERSION"""
    
    try:
        # Clear existing data first
        delete_result = await db.translocations.delete_many({})
        print(f"Cleared {delete_result.deleted_count} existing records")
        
        # Read file content
        content = await file.read()
        
        # Determine file type and read accordingly
        if file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
            df = pd.read_excel(io.BytesIO(content))
        elif file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="File must be Excel (.xlsx, .xls) or CSV (.csv)")
        
        print(f"File read successfully. Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # Flexible column mapping - find ANY column that might contain the data
        def find_column(df, patterns):
            for pattern in patterns:
                for col in df.columns:
                    if pattern.lower() in str(col).lower():
                        return col
            return None
        
        # Find columns with very flexible matching
        project_col = find_column(df, ['project', 'title', 'name'])
        year_col = find_column(df, ['year', 'date'])
        species_col = find_column(df, ['species', 'animal'])
        number_col = find_column(df, ['number', 'count', 'animals'])
        source_name_col = find_column(df, ['source', 'origin'])
        source_coord_col = find_column(df, ['source', 'coord', 'coordinates'])
        source_country_col = find_column(df, ['source', 'country'])
        dest_name_col = find_column(df, ['recipient', 'destination', 'dest'])
        dest_coord_col = find_column(df, ['recipient', 'destination', 'dest', 'coord'])
        dest_country_col = find_column(df, ['recipient', 'destination', 'dest', 'country'])
        transport_col = find_column(df, ['transport', 'method'])
        project_col_alt = find_column(df, ['special', 'project'])
        info_col = find_column(df, ['info', 'additional', 'notes'])
        
        print(f"Found columns:")
        print(f"  Project: {project_col}")
        print(f"  Year: {year_col}")
        print(f"  Species: {species_col}")
        print(f"  Number: {number_col}")
        print(f"  Source name: {source_name_col}")
        print(f"  Source coords: {source_coord_col}")
        
        # Process each row - VERY PERMISSIVE
        created_translocations = []
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Skip completely empty rows
                if row.isna().all():
                    print(f"Skipping empty row {index+1}")
                    continue
                
                # Extract with maximum flexibility - preserve exact text from spreadsheet
                project_title_val = row[project_col] if project_col and not pd.isna(row[project_col]) else None
                project_title = str(project_title_val).strip() if project_title_val is not None else f"Project {index+1}"
                # Keep project title exactly as written in spreadsheet
                
                # Year - handle ANY format
                year = 2024  # default
                if year_col and not pd.isna(row[year_col]):
                    year_str = str(row[year_col]).strip()
                    # Extract first 4-digit number from any string
                    import re
                    year_match = re.search(r'(20\d{2}|19\d{2})', year_str)
                    if year_match:
                        year = int(year_match.group(1))
                
                # Species - be very flexible
                species = "Other"  # default
                if species_col and not pd.isna(row[species_col]):
                    species_str = str(row[species_col]).lower()
                    if "elephant" in species_str:
                        species = "Elephant"
                    elif "black rhino" in species_str or "black-rhino" in species_str:
                        species = "Black Rhino"
                    elif "white rhino" in species_str or "white-rhino" in species_str:
                        species = "White Rhino"
                    elif "plains" in species_str or "multiple" in species_str or "game" in species_str:
                        species = "Plains Game Species"
                
                # Number - extract any number
                number_of_animals = 1  # default
                if number_col and not pd.isna(row[number_col]):
                    try:
                        # Extract first number from string
                        import re
                        num_str = str(row[number_col])
                        num_match = re.search(r'(\d+)', num_str)
                        if num_match:
                            number_of_animals = int(num_match.group(1))
                    except:
                        number_of_animals = 1
                
                # Source area - preserve exact names from spreadsheet
                source_name_val = row[source_name_col] if source_name_col and not pd.isna(row[source_name_col]) else None
                source_name = str(source_name_val).strip() if source_name_val is not None else "Unknown Source"
                # Don't modify the name, keep it exactly as in spreadsheet
                
                source_coords = "0, 0"
                if source_coord_col and not pd.isna(row[source_coord_col]):
                    coord_str = str(row[source_coord_col]).strip()
                    print(f"Processing source coordinates: '{coord_str}'")
                    # Extract coordinates from any format - handle Google Maps format
                    if ',' in coord_str:
                        # Handle formats like "-28.2628, 31.9685" or "-28.262800, 31.968500"
                        coord_str_clean = coord_str.replace('"', '').replace("'", "").strip()
                        parts = coord_str_clean.split(',')
                        if len(parts) >= 2:
                            try:
                                lat = float(parts[0].strip())
                                lng = float(parts[1].strip())
                                # Validate coordinates are reasonable for Africa
                                if (-40 <= lat <= 40) and (-25 <= lng <= 55):
                                    source_coords = f"{lat}, {lng}"
                                    print(f"Successfully parsed source coordinates: {source_coords}")
                                else:
                                    print(f"Source coordinates outside Africa range: {lat}, {lng}")
                            except ValueError as e:
                                print(f"Error parsing source coordinates: {e}")
                    else:
                        # Fallback: extract numbers with regex
                        import re
                        coord_match = re.findall(r'-?\d+\.?\d*', coord_str)
                        if len(coord_match) >= 2:
                            try:
                                lat = float(coord_match[0])
                                lng = float(coord_match[1])
                                if (-40 <= lat <= 40) and (-25 <= lng <= 55):
                                    source_coords = f"{lat}, {lng}"
                                    print(f"Regex parsed source coordinates: {source_coords}")
                            except ValueError as e:
                                print(f"Error with regex parsing source coordinates: {e}")
                
                source_country_val = row[source_country_col] if source_country_col and not pd.isna(row[source_country_col]) else None
                source_country = str(source_country_val).strip() if source_country_val is not None else "Unknown"
                # Don't modify the country name, keep it exactly as in spreadsheet
                
                # Destination area - preserve exact names from spreadsheet
                dest_name_val = row[dest_name_col] if dest_name_col and not pd.isna(row[dest_name_col]) else None
                dest_name = str(dest_name_val).strip() if dest_name_val is not None else "Unknown Destination"
                # Don't modify the name, keep it exactly as in spreadsheet
                
                dest_coords = "0, 0"
                if dest_coord_col and not pd.isna(row[dest_coord_col]):
                    coord_str = str(row[dest_coord_col]).strip()
                    print(f"Processing destination coordinates: '{coord_str}'")
                    # Extract coordinates from any format - handle Google Maps format
                    if ',' in coord_str:
                        # Handle formats like "-25.0194, 31.4659" or "-25.019400, 31.465900"
                        coord_str_clean = coord_str.replace('"', '').replace("'", "").strip()
                        parts = coord_str_clean.split(',')
                        if len(parts) >= 2:
                            try:
                                lat = float(parts[0].strip())
                                lng = float(parts[1].strip())
                                # Validate coordinates are reasonable for Africa
                                if (-40 <= lat <= 40) and (-25 <= lng <= 55):
                                    dest_coords = f"{lat}, {lng}"
                                    print(f"Successfully parsed destination coordinates: {dest_coords}")
                                else:
                                    print(f"Destination coordinates outside Africa range: {lat}, {lng}")
                            except ValueError as e:
                                print(f"Error parsing destination coordinates: {e}")
                    else:
                        # Fallback: extract numbers with regex
                        import re
                        coord_match = re.findall(r'-?\d+\.?\d*', coord_str)
                        if len(coord_match) >= 2:
                            try:
                                lat = float(coord_match[0])
                                lng = float(coord_match[1])
                                if (-40 <= lat <= 40) and (-25 <= lng <= 55):
                                    dest_coords = f"{lat}, {lng}"
                                    print(f"Regex parsed destination coordinates: {dest_coords}")
                            except ValueError as e:
                                print(f"Error with regex parsing destination coordinates: {e}")
                
                dest_country_val = row[dest_country_col] if dest_country_col and not pd.isna(row[dest_country_col]) else None
                dest_country = str(dest_country_val).strip() if dest_country_val is not None else "Unknown"
                # Don't modify the country name, keep it exactly as in spreadsheet
                
                # Transport
                transport = "Road"
                if transport_col and not pd.isna(row[transport_col]):
                    transport_str = str(row[transport_col]).lower()
                    if "air" in transport_str or "plane" in transport_str or "fly" in transport_str:
                        transport = "Air"
                
                # Special project
                special_project = ""
                if project_col_alt and not pd.isna(row[project_col_alt]):
                    proj_str = str(row[project_col_alt])
                    if "african parks" in proj_str.lower():
                        special_project = "African Parks"
                    elif "peace parks" in proj_str.lower():
                        special_project = "Peace Parks"
                    elif "rhino rewild" in proj_str.lower():
                        special_project = "Rhino Rewild"
                
                # Additional info - preserve exactly as written in spreadsheet
                additional_info_val = row[info_col] if info_col and not pd.isna(row[info_col]) else None
                additional_info = str(additional_info_val).strip() if additional_info_val is not None else ""
                if additional_info.lower() in ['nan', 'none', 'null', '']:
                    additional_info = ""
                # Keep additional info exactly as written in spreadsheet
                
                # Create record
                translocation_data = {
                    "project_title": project_title,
                    "year": year,
                    "species": species,
                    "number_of_animals": number_of_animals,
                    "source_area": {
                        "name": source_name,
                        "coordinates": source_coords,
                        "country": source_country
                    },
                    "recipient_area": {
                        "name": dest_name,
                        "coordinates": dest_coords,
                        "country": dest_country
                    },
                    "transport": transport,
                    "special_project": special_project,
                    "additional_info": additional_info
                }
                
                print(f"Row {index+1}: {project_title} - {species} ({number_of_animals})")
                
                translocation_obj = Translocation(**translocation_data)
                result = await db.translocations.insert_one(translocation_obj.dict())
                created_translocations.append(translocation_obj)
                
            except Exception as row_error:
                error_msg = f"Row {index+1}: {str(row_error)}"
                print(f"ERROR: {error_msg}")
                errors.append(error_msg)
                continue  # Always continue processing
        
        success_message = f"Successfully imported {len(created_translocations)} translocations from {file.filename}"
        if errors:
            success_message += f". {len(errors)} rows had errors and were skipped."
        
        return {
            "message": success_message,
            "total_rows_processed": len(df),
            "successful_imports": len(created_translocations),
            "errors": errors[:10],  # Show first 10 errors
            "species_summary": {
                species: len([t for t in created_translocations if t.species == species])
                for species in set([t.species for t in created_translocations])
            }
        }
        
    except Exception as e:
        print(f"Critical error: {str(e)}")
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