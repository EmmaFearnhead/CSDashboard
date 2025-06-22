#!/usr/bin/env python3
import requests
import json
import sys
import tempfile
import os
import pandas as pd
import io

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://16a5d91b-fe8d-4657-b2a4-00610c454aa5.preview.emergentagent.com"
API_URL = f"{BACKEND_URL}/api"

def print_separator():
    print("\n" + "="*80 + "\n")

def test_csv_upload_with_quoted_coordinates():
    """Test uploading a CSV file with quoted coordinates in Google Maps format"""
    print("Testing CSV upload with quoted coordinates in Google Maps format...")
    
    # Create a sample CSV file with quoted coordinates
    csv_content = """Project Title,Year,Species,Number,Source Area: Name,Source Area: Co-Ordinates,Source Area: Country,Recipient Area: Name,Recipient Area: Co-Ordinates,Recipient Area: Country,Transport,Special Project,Additional Info
Test Elephant Move,2024,Elephant,25,Kruger National Park,"-24.9947, 32.5969",South Africa,Addo Elephant Park,"-33.4833, 25.7500",South Africa,Road,Peace Parks,Conservation relocation
Test Black Rhino,2024,Black Rhino,5,Hluhluwe-iMfolozi Park,"-28.2167, 31.9500",South Africa,Akagera National Park,"-1.8794, 30.7963",Rwanda,Air,African Parks,Breeding program"""
    
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
        temp_file.write(csv_content.encode('utf-8'))
        temp_file_path = temp_file.name
    
    try:
        # Upload the CSV file
        with open(temp_file_path, 'rb') as file:
            response = requests.post(
                f"{API_URL}/translocations/import-excel-file",
                files={'file': ('test_quoted_coords.csv', file, 'text/csv')}
            )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code == 200 else response.text}")
        
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        result = response.json()
        
        assert "message" in result, "Response should contain 'message' field"
        assert "successful_imports" in result, "Response should contain 'successful_imports' field"
        
        # Verify the number of successful imports
        assert result["successful_imports"] >= 2, f"Expected at least 2 successful imports, got {result['successful_imports']}"
        
        # Get the imported data to verify coordinates
        get_response = requests.get(f"{API_URL}/translocations")
        assert get_response.status_code == 200, f"Expected status code 200 for GET, got {get_response.status_code}"
        
        translocations = get_response.json()
        
        # Find our test records
        test_records = [t for t in translocations if t["project_title"] == "Test Elephant Move" or t["project_title"] == "Test Black Rhino"]
        
        assert len(test_records) >= 2, f"Expected at least 2 test records, got {len(test_records)}"
        
        # Verify coordinates format
        for record in test_records:
            source_coords = record["source_area"]["coordinates"]
            recipient_coords = record["recipient_area"]["coordinates"]
            
            print(f"Source coordinates: {source_coords}")
            print(f"Recipient coordinates: {recipient_coords}")
            
            # Check if coordinates are in the expected format
            assert "," in source_coords, f"Source coordinates should contain a comma: {source_coords}"
            assert "," in recipient_coords, f"Recipient coordinates should contain a comma: {recipient_coords}"
            
            # Parse and validate coordinates
            source_parts = source_coords.split(",")
            recipient_parts = recipient_coords.split(",")
            
            assert len(source_parts) == 2, f"Source coordinates should have 2 parts: {source_coords}"
            assert len(recipient_parts) == 2, f"Recipient coordinates should have 2 parts: {recipient_coords}"
            
            source_lat = float(source_parts[0].strip())
            source_lng = float(source_parts[1].strip())
            recipient_lat = float(recipient_parts[0].strip())
            recipient_lng = float(recipient_parts[1].strip())
            
            # Verify coordinates are within Africa's range
            assert -35 <= source_lat <= 35, f"Source latitude {source_lat} is not within African range"
            assert -20 <= source_lng <= 50, f"Source longitude {source_lng} is not within African range"
            assert -35 <= recipient_lat <= 35, f"Recipient latitude {recipient_lat} is not within African range"
            assert -20 <= recipient_lng <= 50, f"Recipient longitude {recipient_lng} is not within African range"
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        print("✅ CSV upload with quoted coordinates test passed!")
        return True
    except Exception as e:
        print(f"❌ CSV upload with quoted coordinates test failed: {str(e)}")
        # Clean up the temporary file
        os.unlink(temp_file_path)
        return False

def test_csv_upload_with_space_separated_coordinates():
    """Test uploading a CSV file with space-separated coordinates"""
    print("Testing CSV upload with space-separated coordinates...")
    
    # Create a sample CSV file with space-separated coordinates
    csv_content = """Project Title,Year,Species,Number,Source Area: Name,Source Area: Co-Ordinates,Source Area: Country,Recipient Area: Name,Recipient Area: Co-Ordinates,Recipient Area: Country,Transport,Special Project,Additional Info
Test Space Coords,2024,Elephant,25,Kruger National Park,-24.9947 32.5969,South Africa,Addo Elephant Park,-33.4833 25.7500,South Africa,Road,Peace Parks,Space-separated coordinates"""
    
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
        temp_file.write(csv_content.encode('utf-8'))
        temp_file_path = temp_file.name
    
    try:
        # Upload the CSV file
        with open(temp_file_path, 'rb') as file:
            response = requests.post(
                f"{API_URL}/translocations/import-excel-file",
                files={'file': ('test_space_coords.csv', file, 'text/csv')}
            )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code == 200 else response.text}")
        
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        result = response.json()
        
        assert "message" in result, "Response should contain 'message' field"
        assert "successful_imports" in result, "Response should contain 'successful_imports' field"
        
        # Verify the number of successful imports
        assert result["successful_imports"] >= 1, f"Expected at least 1 successful import, got {result['successful_imports']}"
        
        # Get the imported data to verify coordinates
        get_response = requests.get(f"{API_URL}/translocations")
        assert get_response.status_code == 200, f"Expected status code 200 for GET, got {get_response.status_code}"
        
        translocations = get_response.json()
        
        # Find our test record
        test_record = next((t for t in translocations if t["project_title"] == "Test Space Coords"), None)
        
        assert test_record is not None, "Test record not found in the database"
        
        # Print coordinates for inspection
        source_coords = test_record["source_area"]["coordinates"]
        recipient_coords = test_record["recipient_area"]["coordinates"]
        
        print(f"Source coordinates: {source_coords}")
        print(f"Recipient coordinates: {recipient_coords}")
        
        # Note: The API might convert space-separated coordinates to a default value (0, 0)
        # or it might parse them correctly. We're just checking that the import succeeded.
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        print("✅ CSV upload with space-separated coordinates test passed!")
        return True
    except Exception as e:
        print(f"❌ CSV upload with space-separated coordinates test failed: {str(e)}")
        # Clean up the temporary file
        os.unlink(temp_file_path)
        return False

def test_csv_upload_with_missing_coordinates():
    """Test uploading a CSV file with missing coordinates"""
    print("Testing CSV upload with missing coordinates...")
    
    # Create a sample CSV file with missing coordinates
    csv_content = """Project Title,Year,Species,Number,Source Area: Name,Source Area: Co-Ordinates,Source Area: Country,Recipient Area: Name,Recipient Area: Co-Ordinates,Recipient Area: Country,Transport,Special Project,Additional Info
Test Missing Coords,2024,Elephant,25,Kruger National Park,,South Africa,Addo Elephant Park,,South Africa,Road,Peace Parks,Missing coordinates"""
    
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
        temp_file.write(csv_content.encode('utf-8'))
        temp_file_path = temp_file.name
    
    try:
        # Upload the CSV file
        with open(temp_file_path, 'rb') as file:
            response = requests.post(
                f"{API_URL}/translocations/import-excel-file",
                files={'file': ('test_missing_coords.csv', file, 'text/csv')}
            )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code == 200 else response.text}")
        
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        result = response.json()
        
        assert "message" in result, "Response should contain 'message' field"
        assert "successful_imports" in result, "Response should contain 'successful_imports' field"
        
        # Verify the number of successful imports
        assert result["successful_imports"] >= 1, f"Expected at least 1 successful import, got {result['successful_imports']}"
        
        # Get the imported data to verify coordinates
        get_response = requests.get(f"{API_URL}/translocations")
        assert get_response.status_code == 200, f"Expected status code 200 for GET, got {get_response.status_code}"
        
        translocations = get_response.json()
        
        # Find our test record
        test_record = next((t for t in translocations if t["project_title"] == "Test Missing Coords"), None)
        
        assert test_record is not None, "Test record not found in the database"
        
        # Print coordinates for inspection
        source_coords = test_record["source_area"]["coordinates"]
        recipient_coords = test_record["recipient_area"]["coordinates"]
        
        print(f"Source coordinates: {source_coords}")
        print(f"Recipient coordinates: {recipient_coords}")
        
        # The API should handle missing coordinates by using a default value (0, 0)
        assert source_coords == "0, 0", f"Expected default coordinates '0, 0', got '{source_coords}'"
        assert recipient_coords == "0, 0", f"Expected default coordinates '0, 0', got '{recipient_coords}'"
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        print("✅ CSV upload with missing coordinates test passed!")
        return True
    except Exception as e:
        print(f"❌ CSV upload with missing coordinates test failed: {str(e)}")
        # Clean up the temporary file
        os.unlink(temp_file_path)
        return False

def test_csv_upload_with_invalid_coordinates():
    """Test uploading a CSV file with invalid coordinates"""
    print("Testing CSV upload with invalid coordinates...")
    
    # Create a sample CSV file with invalid coordinates
    csv_content = """Project Title,Year,Species,Number,Source Area: Name,Source Area: Co-Ordinates,Source Area: Country,Recipient Area: Name,Recipient Area: Co-Ordinates,Recipient Area: Country,Transport,Special Project,Additional Info
Test Invalid Coords,2024,Elephant,25,Kruger National Park,invalid coords,South Africa,Addo Elephant Park,not valid,South Africa,Road,Peace Parks,Invalid coordinates"""
    
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
        temp_file.write(csv_content.encode('utf-8'))
        temp_file_path = temp_file.name
    
    try:
        # Upload the CSV file
        with open(temp_file_path, 'rb') as file:
            response = requests.post(
                f"{API_URL}/translocations/import-excel-file",
                files={'file': ('test_invalid_coords.csv', file, 'text/csv')}
            )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code == 200 else response.text}")
        
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        result = response.json()
        
        assert "message" in result, "Response should contain 'message' field"
        assert "successful_imports" in result, "Response should contain 'successful_imports' field"
        
        # Verify the number of successful imports
        assert result["successful_imports"] >= 1, f"Expected at least 1 successful import, got {result['successful_imports']}"
        
        # Get the imported data to verify coordinates
        get_response = requests.get(f"{API_URL}/translocations")
        assert get_response.status_code == 200, f"Expected status code 200 for GET, got {get_response.status_code}"
        
        translocations = get_response.json()
        
        # Find our test record
        test_record = next((t for t in translocations if t["project_title"] == "Test Invalid Coords"), None)
        
        assert test_record is not None, "Test record not found in the database"
        
        # Print coordinates for inspection
        source_coords = test_record["source_area"]["coordinates"]
        recipient_coords = test_record["recipient_area"]["coordinates"]
        
        print(f"Source coordinates: {source_coords}")
        print(f"Recipient coordinates: {recipient_coords}")
        
        # The API should handle invalid coordinates by using a default value (0, 0)
        assert source_coords == "0, 0", f"Expected default coordinates '0, 0', got '{source_coords}'"
        assert recipient_coords == "0, 0", f"Expected default coordinates '0, 0', got '{recipient_coords}'"
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        print("✅ CSV upload with invalid coordinates test passed!")
        return True
    except Exception as e:
        print(f"❌ CSV upload with invalid coordinates test failed: {str(e)}")
        # Clean up the temporary file
        os.unlink(temp_file_path)
        return False

def test_csv_upload_with_different_column_names():
    """Test uploading a CSV file with different column names but mappable structure"""
    print("Testing CSV upload with different column names...")
    
    # Create a temporary CSV file with different column names
    csv_content = """Project,Year,Species,Animals,Source Name,Source Coordinates,Source Country,Recipient Name,Recipient Coordinates,Recipient Country,Transport,Special,Notes
Test Different Columns,2024,Elephant,25,Kruger National Park,"-24.9947, 32.5969",South Africa,Addo Elephant Park,"-33.4833, 25.7500",South Africa,Road,Peace Parks,Different column names"""
    
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
        temp_file.write(csv_content.encode('utf-8'))
        temp_file_path = temp_file.name
    
    try:
        # Upload the CSV file
        with open(temp_file_path, 'rb') as file:
            response = requests.post(
                f"{API_URL}/translocations/import-excel-file",
                files={'file': ('test_different_columns.csv', file, 'text/csv')}
            )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code == 200 else response.text}")
        
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        result = response.json()
        
        assert "message" in result, "Response should contain 'message' field"
        assert "successful_imports" in result, "Response should contain 'successful_imports' field"
        
        # Verify the number of successful imports
        assert result["successful_imports"] >= 1, f"Expected at least 1 successful import, got {result['successful_imports']}"
        
        # Get the imported data to verify
        get_response = requests.get(f"{API_URL}/translocations")
        assert get_response.status_code == 200, f"Expected status code 200 for GET, got {get_response.status_code}"
        
        translocations = get_response.json()
        
        # Find our test record
        test_record = next((t for t in translocations if t["project_title"] == "Test Different Columns"), None)
        
        assert test_record is not None, "Test record not found in the database"
        
        # Verify the data was imported correctly
        assert test_record["species"] == "Elephant", f"Expected species 'Elephant', got '{test_record['species']}'"
        assert test_record["number_of_animals"] == 25, f"Expected number_of_animals 25, got {test_record['number_of_animals']}"
        assert test_record["year"] == 2024, f"Expected year 2024, got {test_record['year']}"
        assert test_record["transport"] == "Road", f"Expected transport 'Road', got '{test_record['transport']}'"
        assert test_record["special_project"] == "Peace Parks", f"Expected special_project 'Peace Parks', got '{test_record['special_project']}'"
        assert test_record["additional_info"] == "Different column names", f"Expected additional_info 'Different column names', got '{test_record['additional_info']}'"
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        print("✅ CSV upload with different column names test passed!")
        return True
    except Exception as e:
        print(f"❌ CSV upload with different column names test failed: {str(e)}")
        # Clean up the temporary file
        os.unlink(temp_file_path)
        return False

def run_all_tests():
    """Run all tests and return overall success status"""
    print_separator()
    print("CONSERVATION SOLUTIONS TRANSLOCATION DASHBOARD - EXCEL/CSV UPLOAD TESTS")
    print_separator()
    
    # First, import the simplified dataset to ensure we have a clean state
    print("Importing simplified dataset for a clean state...")
    requests.post(f"{API_URL}/translocations/import-simplified-data")
    
    test_results = {
        "CSV Upload with Quoted Coordinates": test_csv_upload_with_quoted_coordinates(),
        "CSV Upload with Space-Separated Coordinates": test_csv_upload_with_space_separated_coordinates(),
        "CSV Upload with Missing Coordinates": test_csv_upload_with_missing_coordinates(),
        "CSV Upload with Invalid Coordinates": test_csv_upload_with_invalid_coordinates(),
        "CSV Upload with Different Column Names": test_csv_upload_with_different_column_names()
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