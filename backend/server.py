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
from math import isnan

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

# REMOVED - No more historical data imports

@api_router.post("/translocations/import-excel-file")
async def import_excel_file(file: UploadFile = File(...)):
    """Import translocation data from Excel or CSV file upload - ROBUST VERSION"""
    
    try:
        # FORCE clear all existing data - ensure no old data remains
        delete_result = await db.translocations.delete_many({})
        print(f"🗑️ CLEARED {delete_result.deleted_count} existing records - starting fresh")
        
        # Wait a moment to ensure delete completes
        import asyncio
        await asyncio.sleep(0.1)
        
        # Verify database is empty
        remaining_count = await db.translocations.count_documents({})
        print(f"📊 Database count after clear: {remaining_count}")
        
        if remaining_count > 0:
            print("⚠️ WARNING: Database not fully cleared, forcing another clear")
            await db.translocations.drop()
            print("🗑️ Database collection dropped and recreated")
        
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
        project_col = find_column(df, ['project', 'title'])
        year_col = find_column(df, ['year', 'date'])
        species_col = find_column(df, ['species', 'animal'])
        number_col = find_column(df, ['number', 'count', 'animals'])
        source_name_col = find_column(df, ['source area: name', 'source name'])
        source_coord_col = find_column(df, ['source area: co-ordinates', 'source coordinates', 'source coord'])
        source_country_col = find_column(df, ['source area: country', 'source country'])
        dest_name_col = find_column(df, ['recipient area: name', 'recipient name', 'destination name'])
        dest_coord_col = find_column(df, ['recipient area: co-ordinates', 'recipient coordinates', 'destination coord'])
        dest_country_col = find_column(df, ['recipient area: country', 'recipient country', 'destination country'])
        transport_col = find_column(df, ['transport', 'method'])
        project_col_alt = find_column(df, ['special project', 'special'])
        info_col = find_column(df, ['additional info', 'info', 'additional', 'notes'])
        
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
                    print(f"Backend processing source coordinates: '{coord_str}'")
                    
                    # Handle Google Maps format exactly: "-27.808400634565363, 32.34692072433984"
                    # Remove all quotes but preserve the exact decimal precision
                    coord_clean = coord_str.replace('"', '').replace("'", '').replace('°', '').strip()
                    
                    if ',' in coord_clean:
                        try:
                            parts = coord_clean.split(',')
                            lat_str = parts[0].strip()
                            lng_str = parts[1].strip()
                            
                            # Parse as float and validate for Google Maps format
                            lat = float(lat_str)
                            lng = float(lng_str)
                            
                            # Validate coordinates are reasonable (global range but Africa-focused)
                            # Latitude: -90 to 90, Longitude: -180 to 180
                            # Africa focus: Lat -40 to 40, Lng -25 to 55 
                            if (-90 <= lat <= 90) and (-180 <= lng <= 180):
                                # Store with precision maintained for map display
                                source_coords = f"{lat}, {lng}"
                                print(f"✅ Valid source coordinates: {source_coords}")
                            else:
                                print(f"❌ Source coordinates outside valid range: lat={lat}, lng={lng}")
                                source_coords = "0, 0"
                        except ValueError as e:
                            print(f"❌ Failed to parse source coordinates: {e}")
                            source_coords = "0, 0"
                    else:
                        print(f"❌ No comma found in source coordinates: {coord_clean}")
                        source_coords = "0, 0"
                
                source_country_val = row[source_country_col] if source_country_col and not pd.isna(row[source_country_col]) else None
                source_country = str(source_country_val).strip() if source_country_val is not None else "Unknown"
                
                # Destination area - preserve exact names from spreadsheet
                dest_name_val = row[dest_name_col] if dest_name_col and not pd.isna(row[dest_name_col]) else None
                dest_name = str(dest_name_val).strip() if dest_name_val is not None else "Unknown Destination"
                
                # Destination coordinates - exact same processing as source
                dest_coords = "0, 0"
                if dest_coord_col and not pd.isna(row[dest_coord_col]):
                    coord_str = str(row[dest_coord_col]).strip()
                    print(f"Backend processing destination coordinates: '{coord_str}'")
                    
                    # Handle Google Maps format exactly: "-25.1234567890123, 30.9876543210987"
                    # Remove all quotes but preserve the exact decimal precision
                    coord_clean = coord_str.replace('"', '').replace("'", '').replace('°', '').strip()
                    
                    if ',' in coord_clean:
                        try:
                            parts = coord_clean.split(',')
                            lat_str = parts[0].strip()
                            lng_str = parts[1].strip()
                            
                            # Parse as float but maintain precision when converting back to string
                            lat = float(lat_str)
                            lng = float(lng_str)
                            
                            # Validate coordinates are reasonable (global range but Africa-focused)
                            # Latitude: -90 to 90, Longitude: -180 to 180
                            # Africa focus: Lat -40 to 40, Lng -25 to 55
                            if (-90 <= lat <= 90) and (-180 <= lng <= 180):
                                # Store with precision maintained for map display
                                dest_coords = f"{lat}, {lng}"
                                print(f"✅ Valid destination coordinates: {dest_coords}")
                            else:
                                print(f"❌ Destination coordinates outside valid range: lat={lat}, lng={lng}")
                                dest_coords = "0, 0"
                        except ValueError as e:
                            print(f"❌ Failed to parse destination coordinates: {e}")
                            dest_coords = "0, 0"
                    else:
                        print(f"❌ No comma found in destination coordinates: {coord_clean}")
                        dest_coords = "0, 0"
                
                dest_country_val = row[dest_country_col] if dest_country_col and not pd.isna(row[dest_country_col]) else None
                dest_country = str(dest_country_val).strip() if dest_country_val is not None else "Unknown"
                
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