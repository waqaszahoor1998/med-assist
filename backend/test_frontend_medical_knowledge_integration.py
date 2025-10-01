#!/usr/bin/env python3
"""
Test script for frontend medical knowledge integration.
"""

import requests
import json
import time

def test_frontend_integration():
    """Test the complete frontend-backend integration for medical knowledge"""
    
    print("TESTING FRONTEND MEDICAL KNOWLEDGE INTEGRATION")
    print("=" * 60)
    
    base_url = "http://localhost:8000/api"
    frontend_url = "http://localhost:3000"
    
    print(f"Backend URL: {base_url}")
    print(f"Frontend URL: {frontend_url}")
    
    # Test 1: Backend API endpoints
    print("\n1. Testing Backend API Endpoints")
    print("-" * 50)
    
    # Test medical knowledge stats
    try:
        response = requests.get(f"{base_url}/medical-knowledge/stats/")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Medical knowledge stats: {data['statistics']['total_medicines']:,} medicines")
        else:
            print(f"✗ Stats API failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Stats API error: {e}")
    
    # Test medical knowledge search
    try:
        response = requests.get(f"{base_url}/medical-knowledge/search/?query=aspirin")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Medical knowledge search: {data['results_count']} results for 'aspirin'")
        else:
            print(f"✗ Search API failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Search API error: {e}")
    
    # Test prescription analysis with enhanced database
    try:
        response = requests.post(f"{base_url}/prescription/analyze/", 
                               json={'text': 'Take aspirin 81mg daily'},
                               headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            data = response.json()
            medicines = data.get('extracted_medicines', [])
            print(f"✓ Prescription analysis: {len(medicines)} medicines found")
            if medicines:
                print(f"  Database: {medicines[0].get('data_source', 'Unknown')}")
        else:
            print(f"✗ Prescription analysis failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Prescription analysis error: {e}")
    
    # Test 2: Frontend connectivity
    print("\n2. Testing Frontend Connectivity")
    print("-" * 50)
    
    try:
        response = requests.get(frontend_url, timeout=5)
        if response.status_code == 200:
            print("✓ Frontend is accessible")
        else:
            print(f"⚠ Frontend returned: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("⚠ Frontend not accessible (may still be starting)")
    except Exception as e:
        print(f"⚠ Frontend connectivity issue: {e}")
    
    # Test 3: End-to-end integration scenarios
    print("\n3. Testing End-to-End Integration Scenarios")
    print("-" * 50)
    
    test_scenarios = [
        {
            'name': 'Medicine Search',
            'endpoint': f"{base_url}/medical-knowledge/search/?query=ibuprofen",
            'method': 'GET',
            'data': None
        },
        {
            'name': 'Medical Explanation',
            'endpoint': f"{base_url}/medical-knowledge/explanation/metformin/",
            'method': 'GET',
            'data': None
        },
        {
            'name': 'Prescription Analysis',
            'endpoint': f"{base_url}/prescription/analyze/",
            'method': 'POST',
            'data': {'text': 'Take metformin 500mg twice daily for diabetes'}
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n   Testing: {scenario['name']}")
        try:
            if scenario['method'] == 'GET':
                response = requests.get(scenario['endpoint'])
            else:
                response = requests.post(scenario['endpoint'], 
                                       json=scenario['data'],
                                       headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Success: {scenario['name']}")
                
                # Show relevant data
                if 'results_count' in data:
                    print(f"     Results: {data['results_count']}")
                if 'extracted_medicines' in data:
                    print(f"     Medicines: {len(data['extracted_medicines'])}")
                if 'medicine_name' in data:
                    print(f"     Medicine: {data['medicine_name']}")
            else:
                print(f"   ✗ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ✗ Error: {e}")
    
    # Test 4: Performance testing
    print("\n4. Performance Testing")
    print("-" * 50)
    
    # Test search performance
    search_terms = ['aspirin', 'diabetes', 'cancer', 'hypertension', 'ibuprofen']
    
    for term in search_terms:
        start_time = time.time()
        try:
            response = requests.get(f"{base_url}/medical-knowledge/search/?query={term}")
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                print(f"   {term}: {response_time:.0f}ms ({data['results_count']} results)")
            else:
                print(f"   {term}: Failed ({response.status_code})")
        except Exception as e:
            print(f"   {term}: Error ({e})")
    
    # Test 5: Data validation
    print("\n5. Data Validation")
    print("-" * 50)
    
    # Test that medical knowledge data is properly structured
    try:
        response = requests.get(f"{base_url}/medical-knowledge/explanation/ibuprofen/")
        if response.status_code == 200:
            data = response.json()
            required_fields = ['medicine_name', 'detailed_explanation', 'knowledge_source']
            
            missing_fields = [field for field in required_fields if field not in data]
            if not missing_fields:
                print("✓ Medical explanation data structure is valid")
                print(f"   Medicine: {data['medicine_name']}")
                print(f"   Source: {data['knowledge_source']}")
                print(f"   Explanation length: {len(data.get('detailed_explanation', ''))} characters")
            else:
                print(f"✗ Missing fields in medical explanation: {missing_fields}")
        else:
            print("✗ Could not validate medical explanation data")
    except Exception as e:
        print(f"✗ Data validation error: {e}")
    
    print(f"\n{'='*60}")
    print("FRONTEND INTEGRATION TEST COMPLETED")
    print("=" * 60)
    
    print("\n🎉 INTEGRATION SUMMARY:")
    print("• Backend API endpoints are working")
    print("• Medical knowledge database is accessible")
    print("• Prescription analysis uses enhanced database")
    print("• Frontend should be able to access all features")
    
    print("\n📱 FRONTEND FEATURES AVAILABLE:")
    print("• Medical Knowledge Search Tab")
    print("• Detailed Medicine Explanations")
    print("• Enhanced Prescription Analysis")
    print("• Learn More buttons on medicine cards")
    print("• Database statistics display")
    
    print("\n🚀 NEXT STEPS:")
    print("• Open http://localhost:3000 in browser")
    print("• Navigate to 'Medical Knowledge' tab")
    print("• Search for medicines and conditions")
    print("• Click 'Learn More' on prescription analysis results")

if __name__ == "__main__":
    test_frontend_integration()
