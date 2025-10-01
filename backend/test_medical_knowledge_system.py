#!/usr/bin/env python3
"""
Test script for the integrated medical knowledge system.
"""

import requests
import json
import time

def test_medical_knowledge_system():
    """Test the medical knowledge system endpoints"""
    
    print("TESTING INTEGRATED MEDICAL KNOWLEDGE SYSTEM")
    print("=" * 60)
    
    base_url = "http://localhost:8000/api"
    
    # Test 1: Get medical knowledge database statistics
    print("\n1. Testing Medical Knowledge Database Statistics")
    print("-" * 50)
    
    try:
        response = requests.get(f"{base_url}/medical-knowledge/stats/")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Database statistics retrieved successfully")
            print(f"  Total medicines: {data['statistics']['total_medicines']:,}")
            print(f"  With detailed explanations: {data['statistics']['with_detailed_explanations']:,}")
            print(f"  Enhancement coverage: {data['statistics']['enhancement_coverage']}%")
            print(f"  Average explanation length: {data['statistics']['average_explanation_length']:,} characters")
            print(f"  Data sources: {len(data['data_sources'])}")
        else:
            print(f"✗ Error: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Connection Error: {e}")
    
    # Test 2: Search medical knowledge
    print("\n2. Testing Medical Knowledge Search")
    print("-" * 50)
    
    search_queries = [
        "aspirin",
        "paracetamol poisoning",
        "diabetes",
        "cancer",
        "hypertension"
    ]
    
    for query in search_queries:
        print(f"\n   Searching for: '{query}'")
        try:
            response = requests.get(f"{base_url}/medical-knowledge/search/?query={query}")
            
            if response.status_code == 200:
                data = response.json()
                results_count = data['results_count']
                print(f"   ✓ Found {results_count} results")
                
                if results_count > 0:
                    # Show first result
                    first_result = data['results'][0]
                    print(f"   Top result: {first_result['name']}")
                    if first_result.get('has_detailed_explanation'):
                        print(f"   ✓ Has detailed explanation ({first_result['explanation_length']:,} chars)")
                        if first_result.get('relevant_explanation'):
                            preview = first_result['relevant_explanation'][:100] + "..." if len(first_result['relevant_explanation']) > 100 else first_result['relevant_explanation']
                            print(f"   Preview: {preview}")
                    else:
                        print("   ⚠ No detailed explanation available")
                else:
                    print("   ⚠ No results found")
            else:
                print(f"   ✗ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ✗ Connection Error: {e}")
    
    # Test 3: Get detailed medical explanations
    print("\n3. Testing Detailed Medical Explanations")
    print("-" * 50)
    
    test_medicines = [
        "aspirin",
        "paracetamol",
        "ibuprofen",
        "metformin",
        "lisinopril"
    ]
    
    for medicine in test_medicines:
        print(f"\n   Getting explanation for: '{medicine}'")
        try:
            response = requests.get(f"{base_url}/medical-knowledge/explanation/{medicine}/")
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success':
                    print(f"   ✓ Found detailed explanation")
                    print(f"   Medicine: {data['medicine_name']}")
                    print(f"   Generic: {data['generic_name']}")
                    print(f"   Explanation length: {data['explanation_length']:,} characters")
                    print(f"   Knowledge source: {data['knowledge_source']}")
                    print(f"   Categories: {data['categories']}")
                    
                    # Show preview of explanation
                    explanation = data['detailed_explanation']
                    preview = explanation[:200] + "..." if len(explanation) > 200 else explanation
                    print(f"   Preview: {preview}")
                else:
                    print(f"   ⚠ {data['message']}")
            elif response.status_code == 404:
                print(f"   ⚠ Medicine not found in knowledge database")
            else:
                print(f"   ✗ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ✗ Connection Error: {e}")
    
    # Test 4: Test prescription analysis with enhanced database
    print("\n4. Testing Prescription Analysis with Enhanced Database")
    print("-" * 50)
    
    test_prescriptions = [
        "Take aspirin 81mg daily for heart protection",
        "Use paracetamol 500mg twice daily for pain",
        "Take metformin 500mg with meals for diabetes"
    ]
    
    for i, prescription in enumerate(test_prescriptions, 1):
        print(f"\n   Test {i}: '{prescription}'")
        try:
            response = requests.post(f"{base_url}/prescription/analyze/", 
                                   json={'text': prescription},
                                   headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                data = response.json()
                medicines = data.get('extracted_medicines', [])
                
                print(f"   ✓ Analysis successful")
                print(f"   Medicines found: {len(medicines)}")
                print(f"   Processing method: {data.get('processing_method', 'Unknown')}")
                print(f"   Confidence score: {data.get('confidence_score', 'Unknown')}")
                
                for medicine in medicines:
                    name = medicine.get('name', 'Unknown')
                    source = medicine.get('data_source', 'Unknown')
                    alternatives = medicine.get('alternatives', 'None')
                    
                    print(f"   Medicine: {name}")
                    print(f"   Database: {source}")
                    print(f"   Alternatives: {alternatives[:50]}..." if len(alternatives) > 50 else f"   Alternatives: {alternatives}")
            else:
                print(f"   ✗ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ✗ Connection Error: {e}")
    
    # Test 5: Test enhanced prescription analysis
    print("\n5. Testing Enhanced Prescription Analysis")
    print("-" * 50)
    
    test_prescription = "Take aspirin 100mg and ibuprofen 400mg daily"
    print(f"   Testing: '{test_prescription}'")
    
    try:
        response = requests.post(f"{base_url}/prescription/analyze-enhanced/", 
                               json={'text': test_prescription},
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Enhanced analysis successful")
            print(f"   Processing method: {data.get('processing_method', 'Unknown')}")
            print(f"   Confidence score: {data.get('confidence_score', 'Unknown')}")
            print(f"   Medicines found: {len(data.get('extracted_medicines', []))}")
            print(f"   Drug interactions: {len(data.get('drug_interactions', []))}")
            print(f"   Data sources: {len(data.get('data_sources', {}))}")
        else:
            print(f"   ✗ Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ✗ Connection Error: {e}")
    
    print(f"\n{'='*60}")
    print("MEDICAL KNOWLEDGE SYSTEM TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_medical_knowledge_system()
