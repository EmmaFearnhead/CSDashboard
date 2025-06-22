#!/usr/bin/env python3
import requests
import json
import sys
from datetime import datetime
import uuid

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://37ac102f-355e-47cc-bda4-c15f9d8e9667.preview.emergentagent.com"
API_URL = f"{BACKEND_URL}/api"

def print_separator():
    print("\n" + "="*80 + "\n")

def test_health_check():
    """Test the basic health check endpoint"""
    print("Testing health check endpoint (GET /api/)...")
    
    try:
        response = requests.get(f"{API_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        assert "message" in response.json(), "Response should contain 'message' field"
        assert response.json()["message"] == "Wildlife Conservation Dashboard API", "Incorrect health check message"
        
        print("✅ Health check test passed!")
        return True
    except Exception as e:
        print(f"❌ Health check test failed: {str(e)}")
        return False

def test_get_translocations():
    """Test fetching all translocations"""
    print("Testing get all translocations endpoint (GET /api/translocations)...")
    
    try:
        response = requests.get(f"{API_URL}/translocations")
        print(f"Status Code: {response.status_code}")
        
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        translocations = response.json()
        print(f"Number of translocations retrieved: {len(translocations)}")
        
        # If we have translocations, verify the structure of the first one
        if translocations:
            first_translocation = translocations[0]
            required_fields = ["id", "project_title", "species", "number_of_animals", "year", 
                              "source_area", "recipient_area", "transport", 
                              "special_project", "additional_info", "created_at"]
            
            for field in required_fields:
                assert field in first_translocation, f"Translocation missing required field: {field}"
            
            # Verify location data structure
            for location_type in ["source_area", "recipient_area"]:
                location = first_translocation[location_type]
                assert "name" in location, f"{location_type} missing 'name' field"
                assert "country" in location, f"{location_type} missing 'country' field"
                assert "coordinates" in location, f"{location_type} missing 'coordinates' field"
            
            # Verify African coordinates (rough check)
            for location_type in ["source_area", "recipient_area"]:
                location = first_translocation[location_type]
                coords = location["coordinates"].split(",")
                if len(coords) == 2:
                    lat = float(coords[0].strip())
                    lng = float(coords[1].strip())
                    assert -35 <= lat <= 35, f"Latitude {lat} is not within African range"
                    assert -20 <= lng <= 50, f"Longitude {lng} is not within African range"
        
        print("✅ Get all translocations test passed!")
        return True
    except Exception as e:
        print(f"❌ Get all translocations test failed: {str(e)}")
        return False

def test_import_complete_excel_data():
    """Test importing complete historical data from Excel"""
    print("Testing import complete Excel data endpoint (POST /api/translocations/import-complete-excel-data)...")
    
    try:
        response = requests.post(f"{API_URL}/translocations/import-complete-excel-data")
        print(f"Status Code: {response.status_code}")
        
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        result = response.json()
        
        assert "message" in result, "Response should contain 'message' field"
        assert "translocations" in result, "Response should contain 'translocations' field"
        
        translocations = result["translocations"]
        print(f"Number of imported translocations: {len(translocations)}")
        assert len(translocations) >= 49, f"Expected at least 49 translocations, got {len(translocations)}"
        
        # Verify years span from 2016 to 2025
        years = set(t["year"] for t in translocations)
        print(f"Years in dataset: {sorted(years)}")
        assert min(years) <= 2016, f"Expected earliest year to be 2016 or earlier, got {min(years)}"
        assert max(years) >= 2025, f"Expected latest year to be 2025 or later, got {max(years)}"
        
        # Verify species diversity
        species = set(t["species"] for t in translocations)
        print(f"Species in dataset: {sorted(species)}")
        assert len(species) >= 5, f"Expected at least 5 different species, got {len(species)}"
        
        # Verify key locations
        locations = set()
        for t in translocations:
            locations.add(t["source_area"]["name"])
            locations.add(t["recipient_area"]["name"])
        
        key_locations = ["Liwonde National Park", "Akagera National Park", "Zinave National Park"]
        for location in key_locations:
            assert location in locations, f"Expected to find {location} in dataset"
        
        print("✅ Import complete Excel data test passed!")
        return True
    except Exception as e:
        print(f"❌ Import complete Excel data test failed: {str(e)}")
        return False

def test_get_translocation_stats():
    """Test fetching translocation statistics"""
    print("Testing translocation statistics endpoint (GET /api/translocations/stats)...")
    
    try:
        response = requests.get(f"{API_URL}/translocations/stats")
        print(f"Status Code: {response.status_code}")
        
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        stats = response.json()
        print(f"Statistics: {json.dumps(stats, indent=2)}")
        
        # Verify Plains Game Species has the largest count
        assert "Plains Game Species" in stats, "Plains Game Species should be in the statistics"
        plains_game_count = stats["Plains Game Species"]["total_animals"]
        
        # Verify Elephant has the second largest count
        assert "Elephant" in stats, "Elephant should be in the statistics"
        elephant_count = stats["Elephant"]["total_animals"]
        
        # Check if Plains Game Species has more animals than Elephant
        print(f"Plains Game Species count: {plains_game_count}, Elephant count: {elephant_count}")
        assert plains_game_count > elephant_count, f"Expected Plains Game Species count ({plains_game_count}) to be greater than Elephant count ({elephant_count})"
        
        # Verify that total_animals and total_translocations are integers for all species
        for species, species_stats in stats.items():
            assert "total_animals" in species_stats, f"Statistics for {species} missing 'total_animals' field"
            assert "total_translocations" in species_stats, f"Statistics for {species} missing 'total_translocations' field"
            assert isinstance(species_stats["total_animals"], int), f"total_animals for {species} should be an integer"
            assert isinstance(species_stats["total_translocations"], int), f"total_translocations for {species} should be an integer"
        
        print("✅ Translocation statistics test passed!")
        return True
    except Exception as e:
        print(f"❌ Translocation statistics test failed: {str(e)}")
        return False

def test_filtered_translocations():
    """Test fetching translocations with filters"""
    print("Testing filtered translocations endpoint (GET /api/translocations with filters)...")
    
    try:
        # Test filtering by species
        species_filter = "Elephant"
        response = requests.get(f"{API_URL}/translocations?species={species_filter}")
        print(f"Status Code (species filter): {response.status_code}")
        
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        species_translocations = response.json()
        print(f"Number of {species_filter} translocations: {len(species_translocations)}")
        
        if species_translocations:
            for translocation in species_translocations:
                assert translocation["species"] == species_filter, f"Expected species {species_filter}, got {translocation['species']}"
        
        # Test filtering by year
        year_filter = 2025
        response = requests.get(f"{API_URL}/translocations?year={year_filter}")
        print(f"Status Code (year filter): {response.status_code}")
        
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        year_translocations = response.json()
        print(f"Number of translocations from {year_filter}: {len(year_translocations)}")
        
        if year_translocations:
            for translocation in year_translocations:
                assert translocation["year"] == year_filter, f"Expected year {year_filter}, got {translocation['year']}"
        
        # Test filtering by transport mode
        transport_filter = "Road"
        response = requests.get(f"{API_URL}/translocations?transport={transport_filter}")
        print(f"Status Code (transport mode filter): {response.status_code}")
        
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        transport_translocations = response.json()
        print(f"Number of {transport_filter} translocations: {len(transport_translocations)}")
        
        if transport_translocations:
            for translocation in transport_translocations:
                assert translocation["transport"] == transport_filter, f"Expected transport {transport_filter}, got {translocation['transport']}"
        
        # Test filtering by special project
        project_filter = "Peace Parks"
        response = requests.get(f"{API_URL}/translocations?special_project={project_filter}")
        print(f"Status Code (special project filter): {response.status_code}")
        
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        project_translocations = response.json()
        print(f"Number of {project_filter} translocations: {len(project_translocations)}")
        
        if project_translocations:
            for translocation in project_translocations:
                assert translocation["special_project"] == project_filter, f"Expected special_project {project_filter}, got {translocation['special_project']}"
        
        # Test combined filters
        response = requests.get(f"{API_URL}/translocations?species={species_filter}&transport={transport_filter}")
        print(f"Status Code (combined filters): {response.status_code}")
        
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        combined_translocations = response.json()
        print(f"Number of {species_filter} translocations by {transport_filter}: {len(combined_translocations)}")
        
        if combined_translocations:
            for translocation in combined_translocations:
                assert translocation["species"] == species_filter, f"Expected species {species_filter}, got {translocation['species']}"
                assert translocation["transport"] == transport_filter, f"Expected transport {transport_filter}, got {translocation['transport']}"
        
        print("✅ Filtered translocations test passed!")
        return True
    except Exception as e:
        print(f"❌ Filtered translocations test failed: {str(e)}")
        return False

def test_create_update_delete_translocation():
    """Test CRUD operations for translocations"""
    print("Testing CRUD operations for translocations...")
    
    try:
        # 1. CREATE: Create a new translocation
        new_translocation = {
            "project_title": "Test Lion Translocation",
            "year": 2024,
            "species": "Other",  # Using "Other" for Lion in the new categorization
            "number_of_animals": 12,
            "source_area": {
                "name": "Serengeti National Park",
                "coordinates": "-2.3333, 34.8333",
                "country": "Tanzania"
            },
            "recipient_area": {
                "name": "Ngorongoro Conservation Area",
                "coordinates": "-3.2000, 35.5000",
                "country": "Tanzania"
            },
            "transport": "Road",
            "special_project": "African Parks",
            "additional_info": "Primary species: Lion - Pride relocation for territorial management"
        }
        
        print("Creating new translocation...")
        response = requests.post(
            f"{API_URL}/translocations",
            json=new_translocation
        )
        
        print(f"Status Code: {response.status_code}")
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        
        created_translocation = response.json()
        print(f"Created translocation ID: {created_translocation.get('id', 'No ID')}")
        
        # Verify the created translocation has all required fields
        required_fields = ["id", "project_title", "species", "number_of_animals", "year", 
                          "source_area", "recipient_area", "transport", 
                          "special_project", "additional_info", "created_at"]
        
        for field in required_fields:
            assert field in created_translocation, f"Created translocation missing required field: {field}"
        
        # Verify the data matches what we sent
        assert created_translocation["project_title"] == new_translocation["project_title"]
        assert created_translocation["species"] == new_translocation["species"]
        assert created_translocation["number_of_animals"] == new_translocation["number_of_animals"]
        assert created_translocation["year"] == new_translocation["year"]
        assert created_translocation["transport"] == new_translocation["transport"]
        assert created_translocation["special_project"] == new_translocation["special_project"]
        assert created_translocation["additional_info"] == new_translocation["additional_info"]
        
        # 2. UPDATE: Update the created translocation
        translocation_id = created_translocation["id"]
        updated_data = new_translocation.copy()
        updated_data["number_of_animals"] = 15
        updated_data["additional_info"] = "Primary species: Lion - Updated: Pride relocation with additional animals"
        
        print(f"Updating translocation with ID: {translocation_id}...")
        response = requests.put(
            f"{API_URL}/translocations/{translocation_id}",
            json=updated_data
        )
        
        print(f"Status Code: {response.status_code}")
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        
        updated_translocation = response.json()
        assert updated_translocation["number_of_animals"] == 15, f"Expected updated number_of_animals to be 15, got {updated_translocation['number_of_animals']}"
        assert updated_translocation["additional_info"] == updated_data["additional_info"], "Additional info was not updated correctly"
        
        # 3. DELETE: Delete the created translocation
        print(f"Deleting translocation with ID: {translocation_id}...")
        response = requests.delete(f"{API_URL}/translocations/{translocation_id}")
        
        print(f"Status Code: {response.status_code}")
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        
        # Verify the translocation was deleted
        response = requests.get(f"{API_URL}/translocations")
        translocations = response.json()
        translocation_ids = [t["id"] for t in translocations]
        assert translocation_id not in translocation_ids, f"Translocation with ID {translocation_id} was not deleted"
        
        print("✅ CRUD operations test passed!")
        return True
    except Exception as e:
        print(f"❌ CRUD operations test failed: {str(e)}")
        return False

def test_import_simplified_data():
    """Test importing data with simplified species categorization"""
    print("Testing import simplified data endpoint (POST /api/translocations/import-simplified-data)...")
    
    try:
        response = requests.post(f"{API_URL}/translocations/import-simplified-data")
        print(f"Status Code: {response.status_code}")
        
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        result = response.json()
        
        assert "message" in result, "Response should contain 'message' field"
        assert "translocations" in result, "Response should contain 'translocations' field"
        
        translocations = result["translocations"]
        print(f"Number of imported translocations: {len(translocations)}")
        
        # Get statistics to verify species categorization
        stats_response = requests.get(f"{API_URL}/translocations/stats")
        assert stats_response.status_code == 200, f"Expected status code 200 for stats, got {stats_response.status_code}"
        stats = stats_response.json()
        print(f"Statistics: {json.dumps(stats, indent=2)}")
        
        # Verify the simplified species categorization
        species_categories = set(t["species"] for t in translocations)
        print(f"Species categories: {sorted(species_categories)}")
        
        expected_categories = {"Elephant", "Black Rhino", "White Rhino", "Plains Game Species", "Other"}
        for category in expected_categories:
            assert category in species_categories, f"Expected category '{category}' not found in data"
        
        # Verify Plains Game Species has the highest count
        assert "Plains Game Species" in stats, "Plains Game Species should be in the statistics"
        plains_game_count = stats["Plains Game Species"]["total_animals"]
        
        # Verify Elephant has the second highest count
        assert "Elephant" in stats, "Elephant should be in the statistics"
        elephant_count = stats["Elephant"]["total_animals"]
        
        # Verify the expected counts (with some tolerance)
        print(f"Plains Game Species count: {plains_game_count}")
        print(f"Elephant count: {elephant_count}")
        print(f"Other count: {stats.get('Other', {'total_animals': 0})['total_animals']}")
        print(f"White Rhino count: {stats.get('White Rhino', {'total_animals': 0})['total_animals']}")
        print(f"Black Rhino count: {stats.get('Black Rhino', {'total_animals': 0})['total_animals']}")
        
        # Check if Plains Game Species has more animals than Elephant
        assert plains_game_count > elephant_count, f"Expected Plains Game Species count ({plains_game_count}) to be greater than Elephant count ({elephant_count})"
        
        # Verify counts are close to expected values (with 10% tolerance)
        assert abs(plains_game_count - 3442) / 3442 < 0.1, f"Plains Game Species count ({plains_game_count}) is not close to expected (~3,442)"
        assert abs(elephant_count - 1101) / 1101 < 0.1, f"Elephant count ({elephant_count}) is not close to expected (~1,101)"
        assert abs(stats.get("Other", {"total_animals": 0})["total_animals"] - 687) / 687 < 0.1, f"Other count is not close to expected (~687)"
        assert abs(stats.get("White Rhino", {"total_animals": 0})["total_animals"] - 186) / 186 < 0.1, f"White Rhino count is not close to expected (~186)"
        assert abs(stats.get("Black Rhino", {"total_animals": 0})["total_animals"] - 77) / 77 < 0.1, f"Black Rhino count is not close to expected (~77)"
        
        # Check Plains Game Species entries have proper breakdowns in additional_info
        plains_game_entries = [t for t in translocations if t["species"] == "Plains Game Species"]
        for entry in plains_game_entries:
            assert entry["additional_info"], f"Plains Game Species entry {entry['id']} should have additional_info"
            # Check for common plains game species in the additional_info
            plains_game_keywords = ["buffalo", "impala", "sable", "kudu", "warthog", "waterbuck", "eland", "zebra", "hartebeest"]
            has_species_breakdown = any(keyword.lower() in entry["additional_info"].lower() for keyword in plains_game_keywords)
            assert has_species_breakdown, f"Plains Game Species entry {entry['id']} should have species breakdown in additional_info"
        
        # Check Other entries have primary species noted
        other_entries = [t for t in translocations if t["species"] == "Other"]
        for entry in other_entries:
            assert "Primary species:" in entry["additional_info"], f"Other entry {entry['id']} should have primary species noted in additional_info"
        
        print("✅ Import simplified data test passed!")
        return True
    except Exception as e:
        print(f"❌ Import simplified data test failed: {str(e)}")
        return False

def run_all_tests():
    """Run all tests and return overall success status"""
    print_separator()
    print("CONSERVATION SOLUTIONS TRANSLOCATION DASHBOARD API TESTS")
    print_separator()
    
    # First, import the complete dataset to ensure we have data to test with
    print("Importing complete historical dataset...")
    requests.post(f"{API_URL}/translocations/import-complete-excel-data")
    
    test_results = {
        "Health Check": test_health_check(),
        "Get All Translocations": test_get_translocations(),
        "Import Complete Excel Data": test_import_complete_excel_data(),
        "Import Simplified Data": test_import_simplified_data(),
        "Get Translocation Stats": test_get_translocation_stats(),
        "Filtered Translocations": test_filtered_translocations(),
        "CRUD Operations": test_create_update_delete_translocation()
    }
    
    print_separator()
    print("TEST SUMMARY")
    print_separator()
    
    all_passed = True
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        if not result:
            all_passed = False
        print(f"{test_name}: {status}")
    
    print_separator()
    overall_status = "✅ ALL TESTS PASSED!" if all_passed else "❌ SOME TESTS FAILED"
    print(f"OVERALL STATUS: {overall_status}")
    print_separator()
    
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)