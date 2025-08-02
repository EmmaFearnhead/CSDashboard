#!/usr/bin/env python3
import requests
import json
import sys
from datetime import datetime
import uuid

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://857026d2-a9bb-456a-b602-0940dc278560.preview.emergentagent.com"
API_URL = f"{BACKEND_URL}/api"

def print_separator():
    print("\n" + "="*80 + "\n")

def test_authentication_system():
    """Test the complete authentication system"""
    print("Testing authentication system...")
    
    # Test 1: Unauthenticated requests to protected endpoints should return 401
    print("\n1. Testing unauthenticated requests to protected endpoints...")
    
    protected_endpoints = [
        "/",
        "/translocations",
        "/translocations/stats"
    ]
    
    for endpoint in protected_endpoints:
        try:
            response = requests.get(f"{API_URL}{endpoint}")
            print(f"  GET {endpoint}: Status {response.status_code}")
            assert response.status_code == 401, f"Expected 401 for unauthenticated request to {endpoint}, got {response.status_code}"
        except Exception as e:
            print(f"  ❌ Failed testing unauthenticated access to {endpoint}: {str(e)}")
            return False
    
    print("  ✅ All protected endpoints correctly return 401 for unauthenticated requests")
    
    # Test 2: Login with correct password should return JWT token
    print("\n2. Testing login with correct password...")
    
    try:
        login_data = {"password": "conservation2024"}
        response = requests.post(f"{API_URL}/auth/login", json=login_data)
        print(f"  Login response status: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200 for correct login, got {response.status_code}"
        
        login_result = response.json()
        assert "access_token" in login_result, "Login response should contain access_token"
        assert "token_type" in login_result, "Login response should contain token_type"
        assert login_result["token_type"] == "bearer", f"Expected token_type 'bearer', got {login_result['token_type']}"
        
        # Store the token for further tests
        valid_token = login_result["access_token"]
        print(f"  ✅ Login successful, received JWT token: {valid_token[:20]}...")
        
    except Exception as e:
        print(f"  ❌ Failed testing login with correct password: {str(e)}")
        return False
    
    # Test 3: Login with wrong password should return 401
    print("\n3. Testing login with wrong password...")
    
    try:
        wrong_login_data = {"password": "wrongpassword"}
        response = requests.post(f"{API_URL}/auth/login", json=wrong_login_data)
        print(f"  Wrong password login status: {response.status_code}")
        
        assert response.status_code == 401, f"Expected 401 for wrong password, got {response.status_code}"
        
        error_result = response.json()
        assert "detail" in error_result, "Error response should contain detail field"
        print(f"  ✅ Wrong password correctly rejected with: {error_result['detail']}")
        
    except Exception as e:
        print(f"  ❌ Failed testing login with wrong password: {str(e)}")
        return False
    
    # Test 4: Authenticated requests with valid JWT token should work
    print("\n4. Testing authenticated requests with valid JWT token...")
    
    try:
        headers = {"Authorization": f"Bearer {valid_token}"}
        
        # Test health check endpoint
        response = requests.get(f"{API_URL}/", headers=headers)
        print(f"  Authenticated health check status: {response.status_code}")
        assert response.status_code == 200, f"Expected 200 for authenticated health check, got {response.status_code}"
        
        health_result = response.json()
        assert "message" in health_result, "Health check should return message"
        assert health_result["message"] == "Wildlife Conservation Dashboard API", "Incorrect health check message"
        
        # Test translocations endpoint
        response = requests.get(f"{API_URL}/translocations", headers=headers)
        print(f"  Authenticated translocations status: {response.status_code}")
        assert response.status_code == 200, f"Expected 200 for authenticated translocations, got {response.status_code}"
        
        translocations = response.json()
        print(f"  Retrieved {len(translocations)} translocations with valid token")
        
        # Test stats endpoint
        response = requests.get(f"{API_URL}/translocations/stats", headers=headers)
        print(f"  Authenticated stats status: {response.status_code}")
        assert response.status_code == 200, f"Expected 200 for authenticated stats, got {response.status_code}"
        
        stats = response.json()
        print(f"  Retrieved stats for {len(stats)} species with valid token")
        
        print("  ✅ All authenticated requests work correctly with valid JWT token")
        
    except Exception as e:
        print(f"  ❌ Failed testing authenticated requests: {str(e)}")
        return False
    
    # Test 5: Test /api/auth/verify endpoint with valid token
    print("\n5. Testing /api/auth/verify endpoint with valid token...")
    
    try:
        headers = {"Authorization": f"Bearer {valid_token}"}
        response = requests.post(f"{API_URL}/auth/verify", headers=headers)
        print(f"  Token verification status: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200 for token verification, got {response.status_code}"
        
        verify_result = response.json()
        assert "authenticated" in verify_result, "Verify response should contain authenticated field"
        assert verify_result["authenticated"] == True, "Token should be verified as authenticated"
        assert "user" in verify_result, "Verify response should contain user field"
        
        print(f"  ✅ Token verification successful: {verify_result}")
        
    except Exception as e:
        print(f"  ❌ Failed testing token verification: {str(e)}")
        return False
    
    # Test 6: Test with invalid token
    print("\n6. Testing with invalid JWT token...")
    
    try:
        invalid_headers = {"Authorization": "Bearer invalid_token_here"}
        response = requests.get(f"{API_URL}/", headers=invalid_headers)
        print(f"  Invalid token request status: {response.status_code}")
        
        assert response.status_code == 401, f"Expected 401 for invalid token, got {response.status_code}"
        
        error_result = response.json()
        assert "detail" in error_result, "Error response should contain detail field"
        print(f"  ✅ Invalid token correctly rejected with: {error_result['detail']}")
        
    except Exception as e:
        print(f"  ❌ Failed testing invalid token: {str(e)}")
        return False
    
    # Test 7: Test token verification with invalid token
    print("\n7. Testing /api/auth/verify with invalid token...")
    
    try:
        invalid_headers = {"Authorization": "Bearer invalid_token_here"}
        response = requests.post(f"{API_URL}/auth/verify", headers=invalid_headers)
        print(f"  Invalid token verification status: {response.status_code}")
        
        assert response.status_code == 401, f"Expected 401 for invalid token verification, got {response.status_code}"
        
        error_result = response.json()
        assert "detail" in error_result, "Error response should contain detail field"
        print(f"  ✅ Invalid token verification correctly rejected with: {error_result['detail']}")
        
    except Exception as e:
        print(f"  ❌ Failed testing invalid token verification: {str(e)}")
        return False
    
    print("\n✅ ALL AUTHENTICATION TESTS PASSED!")
    return True

def get_auth_headers():
    """Get authentication headers with valid JWT token"""
    try:
        login_data = {"password": "conservation2024"}
        response = requests.post(f"{API_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            return {"Authorization": f"Bearer {token}"}
        else:
            print(f"Failed to get auth token: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting auth headers: {str(e)}")
        return None

def test_health_check():
    """Test the basic health check endpoint"""
    print("Testing health check endpoint (GET /api/)...")
    
    try:
        headers = get_auth_headers()
        if not headers:
            print("❌ Failed to get authentication headers")
            return False
            
        response = requests.get(f"{API_URL}/", headers=headers)
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
        headers = get_auth_headers()
        if not headers:
            print("❌ Failed to get authentication headers")
            return False
            
        response = requests.get(f"{API_URL}/translocations", headers=headers)
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

def test_excel_file_upload():
    """Test uploading Excel/CSV file with translocation data"""
    print("Testing Excel/CSV file upload endpoint (POST /api/translocations/import-excel-file)...")
    
    try:
        # Create a sample CSV file with translocation data
        csv_content = """Project Title,Year,Species,Number of Animals,Source Area: Name,Source Area: Co-Ordinates,Source Area: Country,Recipient Area: Name,Recipient Area: Co-Ordinates,Recipient Area: Country,Transport,Special Project,Additional Info
Test Elephant Move,2024,Elephant,25,Kruger National Park,-24.9947,31.5969,Addo Elephant Park,-33.4833,25.7500,Road,Peace Parks,Conservation relocation
Test Black Rhino,2024,Black Rhino,5,Hluhluwe-iMfolozi Park,-28.2167,31.9500,Akagera National Park,-1.8794,30.7963,Air,African Parks,Breeding program
Test Plains Game,2024,Plains Game,120,Serengeti National Park,-2.3333,34.8333,Ngorongoro Conservation Area,-3.2000,35.5000,Road,,Buffalo (45); Impala (35); Zebra (40)
Test White Rhino,2024,White Rhino,8,Kruger National Park,-24.9947,31.5969,Limpopo National Park,-23.9400,31.8700,Road,Peace Parks,
Test Lion Pride,2024,Lion,12,Serengeti National Park,-2.3333,34.8333,Ruaha National Park,-7.4833,34.6167,Air,,Pride relocation"""
        
        # Create a temporary CSV file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
            temp_file.write(csv_content.encode('utf-8'))
            temp_file_path = temp_file.name
        
        # Upload the CSV file
        with open(temp_file_path, 'rb') as file:
            response = requests.post(
                f"{API_URL}/translocations/import-excel-file",
                files={'file': ('test_translocations.csv', file, 'text/csv')}
            )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        result = response.json()
        
        assert "message" in result, "Response should contain 'message' field"
        assert "successful_imports" in result, "Response should contain 'successful_imports' field"
        assert "species_summary" in result, "Response should contain 'species_summary' field"
        
        # Verify the number of successful imports
        assert result["successful_imports"] >= 4, f"Expected at least 4 successful imports, got {result['successful_imports']}"
        
        # Verify species categorization
        species_summary = result["species_summary"]
        assert "Elephant" in species_summary, "Elephant should be in the species summary"
        assert "Black Rhino" in species_summary, "Black Rhino should be in the species summary"
        assert "White Rhino" in species_summary, "White Rhino should be in the species summary"
        assert "Plains Game Species" in species_summary, "Plains Game Species should be in the species summary"
        assert "Other" in species_summary, "Other should be in the species summary"
        
        # Verify the data was imported correctly by checking the stats
        stats_response = requests.get(f"{API_URL}/translocations/stats")
        assert stats_response.status_code == 200, f"Expected status code 200 for stats, got {stats_response.status_code}"
        stats = stats_response.json()
        
        # Check that our uploaded species are in the stats
        assert "Elephant" in stats, "Elephant should be in the statistics"
        assert "Black Rhino" in stats, "Black Rhino should be in the statistics"
        assert "White Rhino" in stats, "White Rhino should be in the statistics"
        assert "Plains Game Species" in stats, "Plains Game Species should be in the statistics"
        assert "Other" in stats, "Other should be in the statistics"
        
        # Clean up the temporary file
        import os
        os.unlink(temp_file_path)
        
        print("✅ Excel/CSV file upload test passed!")
        return True
    except Exception as e:
        print(f"❌ Excel/CSV file upload test failed: {str(e)}")
        return False

def test_invalid_file_upload():
    """Test uploading invalid file types"""
    print("Testing invalid file type upload...")
    
    try:
        # Create a sample text file (not CSV or Excel)
        text_content = "This is not a valid CSV or Excel file."
        
        # Create a temporary text file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
            temp_file.write(text_content.encode('utf-8'))
            temp_file_path = temp_file.name
        
        # Upload the text file
        with open(temp_file_path, 'rb') as file:
            response = requests.post(
                f"{API_URL}/translocations/import-excel-file",
                files={'file': ('test_invalid.txt', file, 'text/plain')}
            )
        
        print(f"Status Code: {response.status_code}")
        
        # We expect a 400 Bad Request for invalid file type
        assert response.status_code == 400, f"Expected status code 400 for invalid file type, got {response.status_code}"
        
        # Clean up the temporary file
        import os
        os.unlink(temp_file_path)
        
        print("✅ Invalid file upload test passed!")
        return True
    except Exception as e:
        print(f"❌ Invalid file upload test failed: {str(e)}")
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
        "CRUD Operations": test_create_update_delete_translocation(),
        "Excel File Upload": test_excel_file_upload(),
        "Invalid File Upload": test_invalid_file_upload()
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