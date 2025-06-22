#!/usr/bin/env python3
import requests
import json
import sys
from datetime import datetime

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://999caf0b-2699-456b-bed8-df8245ee1a85.preview.emergentagent.com"
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

def test_create_sample_data():
    """Test the sample data creation endpoint"""
    print("Testing sample data creation endpoint (POST /api/translocations/sample-data)...")
    
    try:
        response = requests.post(f"{API_URL}/translocations/sample-data")
        print(f"Status Code: {response.status_code}")
        print(f"Response message: {response.json().get('message', 'No message')}")
        print(f"Number of translocations created: {len(response.json().get('translocations', []))}")
        
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        assert "message" in response.json(), "Response should contain 'message' field"
        assert "translocations" in response.json(), "Response should contain 'translocations' field"
        
        translocations = response.json()["translocations"]
        assert len(translocations) > 0, "No sample translocations were created"
        
        # Verify the structure of the first translocation
        first_translocation = translocations[0]
        required_fields = ["id", "species", "number_of_animals", "month", "year", 
                          "source_reserve", "recipient_reserve", "transport_mode", 
                          "additional_notes", "created_at"]
        
        for field in required_fields:
            assert field in first_translocation, f"Translocation missing required field: {field}"
        
        # Verify location data structure
        for location_type in ["source_reserve", "recipient_reserve"]:
            location = first_translocation[location_type]
            assert "name" in location, f"{location_type} missing 'name' field"
            assert "country" in location, f"{location_type} missing 'country' field"
            assert "latitude" in location, f"{location_type} missing 'latitude' field"
            assert "longitude" in location, f"{location_type} missing 'longitude' field"
        
        # Verify African coordinates (rough check)
        for location_type in ["source_reserve", "recipient_reserve"]:
            location = first_translocation[location_type]
            lat = location["latitude"]
            lng = location["longitude"]
            assert -35 <= lat <= 35, f"Latitude {lat} is not within African range"
            assert -20 <= lng <= 50, f"Longitude {lng} is not within African range"
        
        print("✅ Sample data creation test passed!")
        return True
    except Exception as e:
        print(f"❌ Sample data creation test failed: {str(e)}")
        return False

def test_get_translocations():
    """Test fetching all translocations"""
    print("Testing get all translocations endpoint (GET /api/translocations)...")
    
    try:
        response = requests.get(f"{API_URL}/translocations")
        print(f"Status Code: {response.status_code}")
        print(f"Number of translocations retrieved: {len(response.json())}")
        
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        translocations = response.json()
        
        # If we have translocations, verify the structure of the first one
        if translocations:
            first_translocation = translocations[0]
            required_fields = ["id", "species", "number_of_animals", "month", "year", 
                              "source_reserve", "recipient_reserve", "transport_mode", 
                              "additional_notes", "created_at"]
            
            for field in required_fields:
                assert field in first_translocation, f"Translocation missing required field: {field}"
        
        print("✅ Get all translocations test passed!")
        return True
    except Exception as e:
        print(f"❌ Get all translocations test failed: {str(e)}")
        return False

def test_get_translocation_stats():
    """Test fetching translocation statistics"""
    print("Testing translocation statistics endpoint (GET /api/translocations/stats)...")
    
    try:
        response = requests.get(f"{API_URL}/translocations/stats")
        print(f"Status Code: {response.status_code}")
        print(f"Statistics: {json.dumps(response.json(), indent=2)}")
        
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        stats = response.json()
        
        # If we have stats, verify the structure
        if stats:
            # Get a sample species
            sample_species = list(stats.keys())[0]
            species_stats = stats[sample_species]
            
            assert "total_animals" in species_stats, "Statistics missing 'total_animals' field"
            assert "total_translocations" in species_stats, "Statistics missing 'total_translocations' field"
            
            # Verify that total_animals and total_translocations are integers
            assert isinstance(species_stats["total_animals"], int), "total_animals should be an integer"
            assert isinstance(species_stats["total_translocations"], int), "total_translocations should be an integer"
        
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
        species_filter = "elephant"
        response = requests.get(f"{API_URL}/translocations?species={species_filter}")
        print(f"Status Code (species filter): {response.status_code}")
        species_translocations = response.json()
        print(f"Number of {species_filter} translocations: {len(species_translocations)}")
        
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        if species_translocations:
            for translocation in species_translocations:
                assert translocation["species"] == species_filter, f"Expected species {species_filter}, got {translocation['species']}"
        
        # Test filtering by year
        year_filter = 2024
        response = requests.get(f"{API_URL}/translocations?year={year_filter}")
        print(f"Status Code (year filter): {response.status_code}")
        year_translocations = response.json()
        print(f"Number of translocations from {year_filter}: {len(year_translocations)}")
        
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        if year_translocations:
            for translocation in year_translocations:
                assert translocation["year"] == year_filter, f"Expected year {year_filter}, got {translocation['year']}"
        
        # Test filtering by transport mode
        transport_filter = "road"
        response = requests.get(f"{API_URL}/translocations?transport_mode={transport_filter}")
        print(f"Status Code (transport mode filter): {response.status_code}")
        transport_translocations = response.json()
        print(f"Number of {transport_filter} translocations: {len(transport_translocations)}")
        
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        if transport_translocations:
            for translocation in transport_translocations:
                assert translocation["transport_mode"] == transport_filter, f"Expected transport_mode {transport_filter}, got {translocation['transport_mode']}"
        
        # Test combined filters
        response = requests.get(f"{API_URL}/translocations?species={species_filter}&transport_mode={transport_filter}")
        print(f"Status Code (combined filters): {response.status_code}")
        combined_translocations = response.json()
        print(f"Number of {species_filter} translocations by {transport_filter}: {len(combined_translocations)}")
        
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        if combined_translocations:
            for translocation in combined_translocations:
                assert translocation["species"] == species_filter, f"Expected species {species_filter}, got {translocation['species']}"
                assert translocation["transport_mode"] == transport_filter, f"Expected transport_mode {transport_filter}, got {translocation['transport_mode']}"
        
        print("✅ Filtered translocations test passed!")
        return True
    except Exception as e:
        print(f"❌ Filtered translocations test failed: {str(e)}")
        return False

def test_create_translocation():
    """Test creating a new translocation"""
    print("Testing create translocation endpoint (POST /api/translocations)...")
    
    try:
        # Create a new translocation with realistic data
        new_translocation = {
            "species": "lion",
            "number_of_animals": 12,
            "month": 5,
            "year": 2024,
            "source_reserve": {
                "name": "Serengeti National Park",
                "country": "Tanzania",
                "latitude": -2.3333,
                "longitude": 34.8333
            },
            "recipient_reserve": {
                "name": "Ngorongoro Conservation Area",
                "country": "Tanzania",
                "latitude": -3.2000,
                "longitude": 35.5000
            },
            "transport_mode": "road",
            "additional_notes": "Lion pride relocation for territorial management"
        }
        
        response = requests.post(
            f"{API_URL}/translocations",
            json=new_translocation
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"Created translocation ID: {response.json().get('id', 'No ID')}")
        else:
            print(f"Error response: {response.text}")
        
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        created_translocation = response.json()
        
        # Verify the created translocation has all required fields
        required_fields = ["id", "species", "number_of_animals", "month", "year", 
                          "source_reserve", "recipient_reserve", "transport_mode", 
                          "additional_notes", "created_at"]
        
        for field in required_fields:
            assert field in created_translocation, f"Created translocation missing required field: {field}"
        
        # Verify the data matches what we sent
        assert created_translocation["species"] == new_translocation["species"]
        assert created_translocation["number_of_animals"] == new_translocation["number_of_animals"]
        assert created_translocation["month"] == new_translocation["month"]
        assert created_translocation["year"] == new_translocation["year"]
        assert created_translocation["transport_mode"] == new_translocation["transport_mode"]
        assert created_translocation["additional_notes"] == new_translocation["additional_notes"]
        
        # Verify source and recipient reserves
        for location_type in ["source_reserve", "recipient_reserve"]:
            assert created_translocation[location_type]["name"] == new_translocation[location_type]["name"]
            assert created_translocation[location_type]["country"] == new_translocation[location_type]["country"]
            assert created_translocation[location_type]["latitude"] == new_translocation[location_type]["latitude"]
            assert created_translocation[location_type]["longitude"] == new_translocation[location_type]["longitude"]
        
        print("✅ Create translocation test passed!")
        return True
    except Exception as e:
        print(f"❌ Create translocation test failed: {str(e)}")
        return False

def run_all_tests():
    """Run all tests and return overall success status"""
    print_separator()
    print("WILDLIFE CONSERVATION DASHBOARD API TESTS")
    print_separator()
    
    test_results = {
        "Health Check": test_health_check(),
        "Create Sample Data": test_create_sample_data(),
        "Get All Translocations": test_get_translocations(),
        "Get Translocation Stats": test_get_translocation_stats(),
        "Filtered Translocations": test_filtered_translocations(),
        "Create Translocation": test_create_translocation()
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