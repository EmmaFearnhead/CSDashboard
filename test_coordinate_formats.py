#!/usr/bin/env python3
import requests
import json
import sys
import tempfile
import os

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://16a5d91b-fe8d-4657-b2a4-00610c454aa5.preview.emergentagent.com"
API_URL = f"{BACKEND_URL}/api"

def print_separator():
    print("\n" + "="*80 + "\n")

def test_google_maps_coordinates():
    """Test uploading a CSV file with Google Maps format coordinates"""
    print("Testing CSV upload with Google Maps format coordinates...")
    
    # Create a sample CSV file with Google Maps format coordinates
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
                files={'file': ('test_google_maps_coords.csv', file, 'text/csv')}
            )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code == 200 else response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Successfully imported {result.get('successful_imports', 0)} translocations")
            
            # Get the imported data to verify coordinates
            get_response = requests.get(f"{API_URL}/translocations")
            if get_response.status_code == 200:
                translocations = get_response.json()
                
                # Find our test records
                test_records = [t for t in translocations if t["project_title"] == "Test Elephant Move" or t["project_title"] == "Test Black Rhino"]
                
                if test_records:
                    print(f"Found {len(test_records)} test records")
                    # Print coordinates for inspection
                    for record in test_records:
                        print(f"Record: {record['project_title']}")
                        print(f"Source coordinates: {record['source_area']['coordinates']}")
                        print(f"Recipient coordinates: {record['recipient_area']['coordinates']}")
                else:
                    print("No test records found in the database")
            else:
                print(f"Failed to get translocations: {get_response.status_code}")
        else:
            print(f"Failed to upload file: {response.status_code}")
            print(f"Error: {response.text}")
    
    except Exception as e:
        print(f"Error: {str(e)}")
    
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)

def test_coordinate_formats():
    """Test different coordinate formats to see which ones work"""
    print("Testing different coordinate formats...")
    
    formats = [
        # Format 1: Comma-separated with quotes
        """Project Title,Year,Species,Number,Source Area: Name,Source Area: Co-Ordinates,Source Area: Country,Recipient Area: Name,Recipient Area: Co-Ordinates,Recipient Area: Country,Transport,Special Project,Additional Info
Test Format 1,2024,Elephant,25,Kruger National Park,"-24.9947, 32.5969",South Africa,Addo Elephant Park,"-33.4833, 25.7500",South Africa,Road,Peace Parks,Format 1""",
        
        # Format 2: Comma-separated without quotes
        """Project Title,Year,Species,Number,Source Area: Name,Source Area: Co-Ordinates,Source Area: Country,Recipient Area: Name,Recipient Area: Co-Ordinates,Recipient Area: Country,Transport,Special Project,Additional Info
Test Format 2,2024,Elephant,25,Kruger National Park,-24.9947, 32.5969,South Africa,Addo Elephant Park,-33.4833, 25.7500,South Africa,Road,Peace Parks,Format 2""",
        
        # Format 3: Space-separated
        """Project Title,Year,Species,Number,Source Area: Name,Source Area: Co-Ordinates,Source Area: Country,Recipient Area: Name,Recipient Area: Co-Ordinates,Recipient Area: Country,Transport,Special Project,Additional Info
Test Format 3,2024,Elephant,25,Kruger National Park,-24.9947 32.5969,South Africa,Addo Elephant Park,-33.4833 25.7500,South Africa,Road,Peace Parks,Format 3""",
        
        # Format 4: No separator (should fail)
        """Project Title,Year,Species,Number,Source Area: Name,Source Area: Co-Ordinates,Source Area: Country,Recipient Area: Name,Recipient Area: Co-Ordinates,Recipient Area: Country,Transport,Special Project,Additional Info
Test Format 4,2024,Elephant,25,Kruger National Park,-24.994732.5969,South Africa,Addo Elephant Park,-33.483325.7500,South Africa,Road,Peace Parks,Format 4"""
    ]
    
    for i, format_content in enumerate(formats, 1):
        print(f"\nTesting Format {i}...")
        
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
            temp_file.write(format_content.encode('utf-8'))
            temp_file_path = temp_file.name
        
        try:
            # Upload the CSV file
            with open(temp_file_path, 'rb') as file:
                response = requests.post(
                    f"{API_URL}/translocations/import-excel-file",
                    files={'file': (f'test_format_{i}.csv', file, 'text/csv')}
                )
            
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"Successfully imported {result.get('successful_imports', 0)} translocations")
                
                # Get the imported data to verify coordinates
                get_response = requests.get(f"{API_URL}/translocations")
                if get_response.status_code == 200:
                    translocations = get_response.json()
                    
                    # Find our test record
                    test_record = next((t for t in translocations if t["project_title"] == f"Test Format {i}"), None)
                    
                    if test_record:
                        print(f"Source coordinates: {test_record['source_area']['coordinates']}")
                        print(f"Recipient coordinates: {test_record['recipient_area']['coordinates']}")
                    else:
                        print(f"No record found for Format {i}")
            else:
                print(f"Failed to upload file: {response.text}")
        
        except Exception as e:
            print(f"Error: {str(e)}")
        
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)

def test_missing_required_columns():
    """Test what happens when required columns are missing"""
    print("Testing missing required columns...")
    
    # Create a sample CSV file with missing required columns
    csv_content = """Project Title,Year,Species,Number,Source Area: Name,Source Area: Country,Recipient Area: Name,Recipient Area: Country,Transport
Test Missing Coords,2024,Elephant,25,Kruger National Park,South Africa,Addo Elephant Park,South Africa,Road"""
    
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
        temp_file.write(csv_content.encode('utf-8'))
        temp_file_path = temp_file.name
    
    try:
        # Upload the CSV file
        with open(temp_file_path, 'rb') as file:
            response = requests.post(
                f"{API_URL}/translocations/import-excel-file",
                files={'file': ('test_missing_required.csv', file, 'text/csv')}
            )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code == 200 else response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Successfully imported {result.get('successful_imports', 0)} translocations")
            
            # Get the imported data to verify
            get_response = requests.get(f"{API_URL}/translocations")
            if get_response.status_code == 200:
                translocations = get_response.json()
                
                # Find our test record
                test_record = next((t for t in translocations if t["project_title"] == "Test Missing Coords"), None)
                
                if test_record:
                    print(f"Record found with missing coordinates:")
                    print(f"Source coordinates: {test_record['source_area']['coordinates']}")
                    print(f"Recipient coordinates: {test_record['recipient_area']['coordinates']}")
                else:
                    print("No test record found in the database")
            else:
                print(f"Failed to get translocations: {get_response.status_code}")
        else:
            print(f"Failed to upload file: {response.status_code}")
            print(f"Error: {response.text}")
    
    except Exception as e:
        print(f"Error: {str(e)}")
    
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)

def test_invalid_file_type():
    """Test uploading an invalid file type"""
    print("Testing invalid file type...")
    
    # Create a sample text file (not CSV or Excel)
    text_content = "This is not a valid CSV or Excel file."
    
    # Create a temporary text file
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
        temp_file.write(text_content.encode('utf-8'))
        temp_file_path = temp_file.name
    
    try:
        # Upload the text file
        with open(temp_file_path, 'rb') as file:
            response = requests.post(
                f"{API_URL}/translocations/import-excel-file",
                files={'file': ('test_invalid.txt', file, 'text/plain')}
            )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        # We expect an error for invalid file type
        if response.status_code != 200:
            print(f"Received expected error for invalid file type")
        else:
            print(f"Unexpected success for invalid file type")
    
    except Exception as e:
        print(f"Error: {str(e)}")
    
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)

if __name__ == "__main__":
    print_separator()
    print("CONSERVATION SOLUTIONS TRANSLOCATION DASHBOARD - COORDINATE FORMAT TESTS")
    print_separator()
    
    # First, import the simplified dataset to ensure we have a clean state
    print("Importing simplified dataset for a clean state...")
    requests.post(f"{API_URL}/translocations/import-simplified-data")
    
    print_separator()
    test_google_maps_coordinates()
    
    print_separator()
    test_coordinate_formats()
    
    print_separator()
    test_missing_required_columns()
    
    print_separator()
    test_invalid_file_type()
    
    print_separator()
    print("TESTS COMPLETED")
    print_separator()