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

def test_user_csv_upload():
    """Test uploading a CSV file with the exact column structure from the user's data"""
    print("Testing CSV upload with the exact column structure from the user's data...")
    
    # Create a sample CSV file with the exact column structure from the user's data
    csv_content = """Project Title,Year,Species,Number,Source Area: Name,Source Area: Co-Ordinates,Source Area: Country,Recipient Area: Name,Recipient Area: Co-Ordinates,Recipient Area: Country,Transport,Special Project,Additional Info
Test Elephant Move,2024,Elephant,25,Kruger National Park,"-24.9947, 32.5969",South Africa,Addo Elephant Park,"-33.4833, 25.7500",South Africa,Road,Peace Parks,Conservation relocation
Test Black Rhino,2024,Black Rhino,5,Hluhluwe-iMfolozi Park,"-28.2167, 31.9500",South Africa,Akagera National Park,"-1.8794, 30.7963",Rwanda,Air,African Parks,Breeding program
Test Plains Game,2024,Plains Game,120,Serengeti National Park,"-2.3333, 34.8333",Tanzania,Ngorongoro Conservation Area,"-3.2000, 35.5000",Tanzania,Road,,Buffalo (45); Impala (35); Zebra (40)
Test White Rhino,2024,White Rhino,8,Kruger National Park,"-24.9947, 31.5969",South Africa,Limpopo National Park,"-23.9400, 31.8700",Mozambique,Road,Peace Parks,
Test Lion Pride,2024,Lion,12,Serengeti National Park,"-2.3333, 34.8333",Tanzania,Ruaha National Park,"-7.4833, 34.6167",Tanzania,Air,,Pride relocation"""
    
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
        temp_file.write(csv_content.encode('utf-8'))
        temp_file_path = temp_file.name
    
    try:
        # Upload the CSV file
        with open(temp_file_path, 'rb') as file:
            response = requests.post(
                f"{API_URL}/translocations/import-excel-file",
                files={'file': ('user_test_data.csv', file, 'text/csv')}
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
                
                # Find our test records
                test_records = [t for t in translocations if t["project_title"].startswith("Test ")]
                
                if test_records:
                    print(f"Found {len(test_records)} test records")
                    
                    # Print details of each record
                    for record in test_records:
                        print(f"\nRecord: {record['project_title']}")
                        print(f"Species: {record['species']}")
                        print(f"Number of animals: {record['number_of_animals']}")
                        print(f"Source coordinates: {record['source_area']['coordinates']}")
                        print(f"Recipient coordinates: {record['recipient_area']['coordinates']}")
                        print(f"Transport: {record['transport']}")
                        print(f"Special project: {record['special_project']}")
                        print(f"Additional info: {record['additional_info']}")
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

def test_multipart_form_data():
    """Test the /api/translocations/import-excel-file endpoint with proper multipart/form-data"""
    print("Testing /api/translocations/import-excel-file endpoint with proper multipart/form-data...")
    
    # Create a sample CSV file with the exact column structure from the user's data
    csv_content = """Project Title,Year,Species,Number,Source Area: Name,Source Area: Co-Ordinates,Source Area: Country,Recipient Area: Name,Recipient Area: Co-Ordinates,Recipient Area: Country,Transport,Special Project,Additional Info
Multipart Test,2024,Elephant,25,Kruger National Park,"-24.9947, 32.5969",South Africa,Addo Elephant Park,"-33.4833, 25.7500",South Africa,Road,Peace Parks,Testing multipart/form-data"""
    
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
        temp_file.write(csv_content.encode('utf-8'))
        temp_file_path = temp_file.name
    
    try:
        # Upload the CSV file with explicit multipart/form-data
        with open(temp_file_path, 'rb') as file:
            files = {'file': ('multipart_test.csv', file, 'text/csv')}
            response = requests.post(
                f"{API_URL}/translocations/import-excel-file",
                files=files
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
                test_record = next((t for t in translocations if t["project_title"] == "Multipart Test"), None)
                
                if test_record:
                    print(f"\nRecord: {test_record['project_title']}")
                    print(f"Species: {test_record['species']}")
                    print(f"Number of animals: {test_record['number_of_animals']}")
                    print(f"Source coordinates: {test_record['source_area']['coordinates']}")
                    print(f"Recipient coordinates: {test_record['recipient_area']['coordinates']}")
                    print(f"Transport: {test_record['transport']}")
                    print(f"Special project: {test_record['special_project']}")
                    print(f"Additional info: {test_record['additional_info']}")
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

if __name__ == "__main__":
    print_separator()
    print("CONSERVATION SOLUTIONS TRANSLOCATION DASHBOARD - USER DATA UPLOAD TEST")
    print_separator()
    
    # First, import the simplified dataset to ensure we have a clean state
    print("Importing simplified dataset for a clean state...")
    requests.post(f"{API_URL}/translocations/import-simplified-data")
    
    print_separator()
    test_user_csv_upload()
    
    print_separator()
    test_multipart_form_data()
    
    print_separator()
    print("TESTS COMPLETED")
    print_separator()