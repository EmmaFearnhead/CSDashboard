#!/usr/bin/env python3
import requests
import json
import sys
import tempfile
import os
import pandas as pd
import io

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://857026d2-a9bb-456a-b602-0940dc278560.preview.emergentagent.com"
API_URL = f"{BACKEND_URL}/api"

def print_separator():
    print("\n" + "="*80 + "\n")

def create_sample_csv(filename, content=None):
    """Create a sample CSV file with the specified content or default content"""
    if content is None:
        # Default content with the exact column structure from the user's data
        content = """Project Title,Year,Species,Number,Source Area: Name,Source Area: Co-Ordinates,Source Area: Country,Recipient Area: Name,Recipient Area: Co-Ordinates,Recipient Area: Country,Transport,Special Project,Additional Info
Test Elephant Move,2024,Elephant,25,Kruger National Park,-24.9947 31.5969,South Africa,Addo Elephant Park,-33.4833 25.7500,South Africa,Road,Peace Parks,Conservation relocation
Test Black Rhino,2024,Black Rhino,5,Hluhluwe-iMfolozi Park,-28.2167 31.9500,South Africa,Akagera National Park,-1.8794 30.7963,Rwanda,Air,African Parks,Breeding program
Test Plains Game,2024,Plains Game,120,Serengeti National Park,-2.3333 34.8333,Tanzania,Ngorongoro Conservation Area,-3.2000 35.5000,Tanzania,Road,,Buffalo (45); Impala (35); Zebra (40)
Test White Rhino,2024,White Rhino,8,Kruger National Park,-24.9947 31.5969,South Africa,Limpopo National Park,-23.9400 31.8700,Mozambique,Road,Peace Parks,
Test Lion Pride,2024,Lion,12,Serengeti National Park,-2.3333 34.8333,Tanzania,Ruaha National Park,-7.4833 34.6167,Tanzania,Air,,Pride relocation"""
    
    with open(filename, 'w') as f:
        f.write(content)
    return filename

def create_sample_excel(filename, content=None):
    """Create a sample Excel file with the specified content or default content"""
    if content is None:
        # Create a DataFrame with the same structure as the CSV
        data = {
            "Project Title": ["Test Elephant Move", "Test Black Rhino", "Test Plains Game", "Test White Rhino", "Test Lion Pride"],
            "Year": [2024, 2024, 2024, 2024, 2024],
            "Species": ["Elephant", "Black Rhino", "Plains Game", "White Rhino", "Lion"],
            "Number": [25, 5, 120, 8, 12],
            "Source Area: Name": ["Kruger National Park", "Hluhluwe-iMfolozi Park", "Serengeti National Park", "Kruger National Park", "Serengeti National Park"],
            "Source Area: Co-Ordinates": ["-24.9947, 31.5969", "-28.2167, 31.9500", "-2.3333, 34.8333", "-24.9947, 31.5969", "-2.3333, 34.8333"],
            "Source Area: Country": ["South Africa", "South Africa", "Tanzania", "South Africa", "Tanzania"],
            "Recipient Area: Name": ["Addo Elephant Park", "Akagera National Park", "Ngorongoro Conservation Area", "Limpopo National Park", "Ruaha National Park"],
            "Recipient Area: Co-Ordinates": ["-33.4833, 25.7500", "-1.8794, 30.7963", "-3.2000, 35.5000", "-23.9400, 31.8700", "-7.4833, 34.6167"],
            "Recipient Area: Country": ["South Africa", "Rwanda", "Tanzania", "Mozambique", "Tanzania"],
            "Transport": ["Road", "Air", "Road", "Road", "Air"],
            "Special Project": ["Peace Parks", "African Parks", "", "Peace Parks", ""],
            "Additional Info": ["Conservation relocation", "Breeding program", "Buffalo (45); Impala (35); Zebra (40)", "", "Pride relocation"]
        }
        df = pd.DataFrame(data)
    else:
        # Parse the content as CSV and convert to DataFrame
        df = pd.read_csv(io.StringIO(content))
    
    # Write to Excel file
    df.to_excel(filename, index=False)
    return filename

def test_csv_upload_with_correct_columns():
    """Test uploading a CSV file with the correct column structure"""
    print("Testing CSV upload with correct column structure...")
    
    try:
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        create_sample_csv(temp_file_path)
        
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
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        print("✅ CSV upload with correct column structure test passed!")
        return True
    except Exception as e:
        print(f"❌ CSV upload with correct column structure test failed: {str(e)}")
        return False

def test_excel_upload_with_correct_columns():
    """Test uploading an Excel file with the correct column structure"""
    print("Testing Excel upload with correct column structure...")
    
    try:
        # Create a temporary Excel file
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        create_sample_excel(temp_file_path)
        
        # Upload the Excel file
        with open(temp_file_path, 'rb') as file:
            response = requests.post(
                f"{API_URL}/translocations/import-excel-file",
                files={'file': ('test_translocations.xlsx', file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
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
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        print("✅ Excel upload with correct column structure test passed!")
        return True
    except Exception as e:
        print(f"❌ Excel upload with correct column structure test failed: {str(e)}")
        return False

def test_csv_upload_with_different_column_names():
    """Test uploading a CSV file with different column names but mappable structure"""
    print("Testing CSV upload with different column names...")
    
    try:
        # Create a temporary CSV file with different column names
        different_columns_content = """Project,Year,Species,Animals,Source Name,Source Coordinates,Source Country,Recipient Name,Recipient Coordinates,Recipient Country,Transport,Special,Notes
Test Elephant Move,2024,Elephant,25,Kruger National Park,-24.9947 31.5969,South Africa,Addo Elephant Park,-33.4833 25.7500,South Africa,Road,Peace Parks,Conservation relocation
Test Black Rhino,2024,Black Rhino,5,Hluhluwe-iMfolozi Park,-28.2167 31.9500,South Africa,Akagera National Park,-1.8794 30.7963,Rwanda,Air,African Parks,Breeding program"""
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        create_sample_csv(temp_file_path, different_columns_content)
        
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
        assert result["successful_imports"] >= 2, f"Expected at least 2 successful imports, got {result['successful_imports']}"
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        print("✅ CSV upload with different column names test passed!")
        return True
    except Exception as e:
        print(f"❌ CSV upload with different column names test failed: {str(e)}")
        return False

def test_csv_upload_with_missing_columns():
    """Test uploading a CSV file with missing columns"""
    print("Testing CSV upload with missing columns...")
    
    try:
        # Create a temporary CSV file with missing columns
        missing_columns_content = """Project Title,Year,Species,Number,Source Area: Name,Source Area: Country,Recipient Area: Name,Recipient Area: Country,Transport
Test Elephant Move,2024,Elephant,25,Kruger National Park,South Africa,Addo Elephant Park,South Africa,Road
Test Black Rhino,2024,Black Rhino,5,Hluhluwe-iMfolozi Park,South Africa,Akagera National Park,Rwanda,Air"""
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        create_sample_csv(temp_file_path, missing_columns_content)
        
        # Upload the CSV file
        with open(temp_file_path, 'rb') as file:
            response = requests.post(
                f"{API_URL}/translocations/import-excel-file",
                files={'file': ('test_missing_columns.csv', file, 'text/csv')}
            )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code == 200 else response.text}")
        
        # The API should handle missing columns gracefully
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        result = response.json()
        
        assert "message" in result, "Response should contain 'message' field"
        assert "successful_imports" in result, "Response should contain 'successful_imports' field"
        
        # Verify the number of successful imports
        assert result["successful_imports"] >= 1, f"Expected at least 1 successful import, got {result['successful_imports']}"
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        print("✅ CSV upload with missing columns test passed!")
        return True
    except Exception as e:
        print(f"❌ CSV upload with missing columns test failed: {str(e)}")
        return False

def test_csv_upload_with_invalid_coordinates():
    """Test uploading a CSV file with invalid coordinates"""
    print("Testing CSV upload with invalid coordinates...")
    
    try:
        # Create a temporary CSV file with invalid coordinates
        invalid_coords_content = """Project Title,Year,Species,Number,Source Area: Name,Source Area: Co-Ordinates,Source Area: Country,Recipient Area: Name,Recipient Area: Co-Ordinates,Recipient Area: Country,Transport,Special Project,Additional Info
Test Elephant Move,2024,Elephant,25,Kruger National Park,invalid coords,South Africa,Addo Elephant Park,not valid,South Africa,Road,Peace Parks,Conservation relocation
Test Black Rhino,2024,Black Rhino,5,Hluhluwe-iMfolozi Park,200 200,South Africa,Akagera National Park,-1.8794 30.7963,Rwanda,Air,African Parks,Breeding program"""
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        create_sample_csv(temp_file_path, invalid_coords_content)
        
        # Upload the CSV file
        with open(temp_file_path, 'rb') as file:
            response = requests.post(
                f"{API_URL}/translocations/import-excel-file",
                files={'file': ('test_invalid_coords.csv', file, 'text/csv')}
            )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code == 200 else response.text}")
        
        # The API should handle invalid coordinates gracefully
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        result = response.json()
        
        assert "message" in result, "Response should contain 'message' field"
        assert "successful_imports" in result, "Response should contain 'successful_imports' field"
        
        # Verify the number of successful imports
        assert result["successful_imports"] >= 1, f"Expected at least 1 successful import, got {result['successful_imports']}"
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        print("✅ CSV upload with invalid coordinates test passed!")
        return True
    except Exception as e:
        print(f"❌ CSV upload with invalid coordinates test failed: {str(e)}")
        return False

def test_csv_upload_with_google_maps_coordinates():
    """Test uploading a CSV file with Google Maps format coordinates"""
    print("Testing CSV upload with Google Maps format coordinates...")
    
    try:
        # Create a temporary CSV file with Google Maps format coordinates
        google_maps_coords_content = """Project Title,Year,Species,Number,Source Area: Name,Source Area: Co-Ordinates,Source Area: Country,Recipient Area: Name,Recipient Area: Co-Ordinates,Recipient Area: Country,Transport,Special Project,Additional Info
Test Elephant Move,2024,Elephant,25,Kruger National Park,-24.9947, 31.5969,South Africa,Addo Elephant Park,-33.4833, 25.7500,South Africa,Road,Peace Parks,Conservation relocation
Test Black Rhino,2024,Black Rhino,5,Hluhluwe-iMfolozi Park,-28.2167, 31.9500,South Africa,Akagera National Park,-1.8794, 30.7963,Rwanda,Air,African Parks,Breeding program
Test Plains Game,2024,Plains Game,120,Serengeti National Park,-2.3333, 34.8333,Tanzania,Ngorongoro Conservation Area,-3.2000, 35.5000,Tanzania,Road,,Buffalo (45); Impala (35); Zebra (40)"""
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        create_sample_csv(temp_file_path, google_maps_coords_content)
        
        # Upload the CSV file
        with open(temp_file_path, 'rb') as file:
            response = requests.post(
                f"{API_URL}/translocations/import-excel-file",
                files={'file': ('test_google_maps_coords.csv', file, 'text/csv')}
            )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        result = response.json()
        
        assert "message" in result, "Response should contain 'message' field"
        assert "successful_imports" in result, "Response should contain 'successful_imports' field"
        
        # Verify the number of successful imports
        assert result["successful_imports"] >= 3, f"Expected at least 3 successful imports, got {result['successful_imports']}"
        
        # Get the imported data to verify coordinates
        get_response = requests.get(f"{API_URL}/translocations")
        assert get_response.status_code == 200, f"Expected status code 200 for GET, got {get_response.status_code}"
        
        translocations = get_response.json()
        
        # Find our test records
        test_records = [t for t in translocations if t["project_title"] == "Test Elephant Move" or t["project_title"] == "Test Black Rhino"]
        
        if test_records:
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
                source_lat, source_lng = map(float, source_coords.split(","))
                recipient_lat, recipient_lng = map(float, recipient_coords.split(","))
                
                # Verify coordinates are within Africa's range
                assert -35 <= source_lat <= 35, f"Source latitude {source_lat} is not within African range"
                assert -20 <= source_lng <= 50, f"Source longitude {source_lng} is not within African range"
                assert -35 <= recipient_lat <= 35, f"Recipient latitude {recipient_lat} is not within African range"
                assert -20 <= recipient_lng <= 50, f"Recipient longitude {recipient_lng} is not within African range"
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        print("✅ CSV upload with Google Maps format coordinates test passed!")
        return True
    except Exception as e:
        print(f"❌ CSV upload with Google Maps format coordinates test failed: {str(e)}")
        return False

def test_invalid_file_type_upload():
    """Test uploading an invalid file type"""
    print("Testing invalid file type upload...")
    
    try:
        # Create a temporary text file (not CSV or Excel)
        text_content = "This is not a valid CSV or Excel file."
        
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
        print(f"Response: {response.text}")
        
        # We expect a 400 Bad Request for invalid file type
        assert response.status_code == 400, f"Expected status code 400 for invalid file type, got {response.status_code}"
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        print("✅ Invalid file type upload test passed!")
        return True
    except Exception as e:
        print(f"❌ Invalid file type upload test failed: {str(e)}")
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
        "CSV Upload with Correct Columns": test_csv_upload_with_correct_columns(),
        "Excel Upload with Correct Columns": test_excel_upload_with_correct_columns(),
        "CSV Upload with Different Column Names": test_csv_upload_with_different_column_names(),
        "CSV Upload with Missing Columns": test_csv_upload_with_missing_columns(),
        "CSV Upload with Invalid Coordinates": test_csv_upload_with_invalid_coordinates(),
        "CSV Upload with Google Maps Coordinates": test_csv_upload_with_google_maps_coordinates(),
        "Invalid File Type Upload": test_invalid_file_type_upload()
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