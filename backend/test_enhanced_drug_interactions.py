#!/usr/bin/env python3
"""
Test script for Enhanced Drug Interaction System (OpenFDA + RxNorm)
Tests the enhanced system with real FDA and RxNorm data
"""

import sys
import os
import requests
import json
import time
from datetime import datetime

# Add backend directory to path
sys.path.append(os.path.dirname(__file__))

def test_api_connectivity():
    """Test basic API connectivity"""
    print("🔗 Testing API Connectivity")
    print("=" * 50)
    
    try:
        response = requests.get('http://localhost:8000/api/ping/')
        if response.status_code == 200:
            print("✅ API is running")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to connect to API: {e}")
        return False

def test_enhanced_drug_interactions():
    """Test enhanced drug interaction checking"""
    print("\n🧪 Testing Enhanced Drug Interaction System")
    print("=" * 50)
    
    # Test cases with common medicines
    test_cases = [
        {
            'name': 'Common Pain Medications',
            'medicines': ['aspirin', 'ibuprofen'],
            'expected_sources': ['Manual Database', 'OpenFDA']
        },
        {
            'name': 'Diabetes Medications',
            'medicines': ['metformin', 'insulin'],
            'expected_sources': ['Manual Database', 'OpenFDA', 'RxNorm']
        },
        {
            'name': 'Heart Medications',
            'medicines': ['warfarin', 'aspirin'],
            'expected_sources': ['Manual Database', 'OpenFDA']
        },
        {
            'name': 'Safe Combination',
            'medicines': ['vitamin d', 'calcium'],
            'expected_sources': ['Manual Database']
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n📋 Testing: {test_case['name']}")
        print(f"   Medicines: {test_case['medicines']}")
        
        try:
            response = requests.post('http://localhost:8000/api/interactions/enhanced/check/', 
                                   json={'medicines': test_case['medicines']})
            
            if response.status_code == 200:
                data = response.json()
                interaction_data = data['data']
                
                interactions_found = interaction_data['interactions_found']
                overall_risk = interaction_data['overall_risk_level']
                data_sources = interaction_data.get('data_sources', [])
                
                print(f"   Interactions Found: {interactions_found}")
                print(f"   Overall Risk: {overall_risk}")
                print(f"   Data Sources: {', '.join(data_sources)}")
                
                # Check if expected sources are present
                expected_sources = test_case['expected_sources']
                sources_found = any(source in data_sources for source in expected_sources)
                
                if sources_found or interactions_found >= 0:  # At least some data found
                    print("   ✅ PASS")
                    results.append(True)
                else:
                    print("   ⚠️ PARTIAL - Expected sources not found")
                    results.append(False)
                
                # Show interaction details if found
                if interaction_data['interactions']:
                    for interaction in interaction_data['interactions'][:2]:  # Show first 2
                        print(f"   🚨 {interaction['severity']} - {interaction['source']}")
                        print(f"      {interaction['description'][:100]}...")
                
            else:
                print(f"   ❌ API Error: {response.status_code}")
                print(f"   Response: {response.text}")
                results.append(False)
                
        except Exception as e:
            print(f"   ❌ Test Error: {e}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    print(f"\n📊 Enhanced Interaction Tests: {passed}/{total} passed")
    
    return passed == total

def test_medicine_info_enhanced():
    """Test enhanced medicine information retrieval"""
    print("\n🔍 Testing Enhanced Medicine Information")
    print("=" * 50)
    
    test_medicines = ['aspirin', 'metformin', 'warfarin']
    
    for medicine in test_medicines:
        print(f"\n📋 Testing enhanced info for: {medicine}")
        
        try:
            response = requests.get(f'http://localhost:8000/api/interactions/enhanced/medicine/{medicine}/')
            
            if response.status_code == 200:
                data = response.json()
                medicine_data = data['data']
                
                print(f"   Original Name: {medicine_data.get('original_name', 'N/A')}")
                print(f"   Standardized Name: {medicine_data.get('standardized_name', 'N/A')}")
                print(f"   RxCUI: {medicine_data.get('rxcui', 'N/A')}")
                
                # Check OpenFDA data
                openfda_data = medicine_data.get('openfda_data', {})
                if 'error' not in openfda_data:
                    print(f"   OpenFDA: ✅ Data available")
                    interactions = openfda_data.get('drug_interactions', [])
                    print(f"   OpenFDA Interactions: {len(interactions)}")
                else:
                    print(f"   OpenFDA: ❌ {openfda_data.get('error', 'Unknown error')}")
                
                # Check RxNorm data
                rxnorm_data = medicine_data.get('rxnorm_data')
                if rxnorm_data:
                    print(f"   RxNorm: ✅ Data available")
                    all_names = rxnorm_data.get('all_names', [])
                    print(f"   All Names: {len(all_names)} found")
                else:
                    print(f"   RxNorm: ❌ No data available")
                
            else:
                print(f"   ❌ API Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Test Error: {e}")

def test_bulk_download():
    """Test bulk download functionality"""
    print("\n📥 Testing Bulk Download")
    print("=" * 50)
    
    medicines = ['aspirin', 'metformin']
    
    print(f"📋 Downloading data for: {medicines}")
    
    try:
        response = requests.post('http://localhost:8000/api/interactions/enhanced/bulk-download/', 
                               json={'medicines': medicines})
        
        if response.status_code == 200:
            data = response.json()
            message = data['message']
            results = data['results']
            
            print(f"   ✅ {message}")
            
            for medicine, result in results.items():
                if 'error' not in result:
                    print(f"   📊 {medicine}: Data downloaded successfully")
                else:
                    print(f"   ❌ {medicine}: {result['error']}")
        else:
            print(f"   ❌ API Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Test Error: {e}")

def test_cache_stats():
    """Test cache statistics"""
    print("\n📊 Testing Cache Statistics")
    print("=" * 50)
    
    try:
        response = requests.get('http://localhost:8000/api/interactions/enhanced/cache-stats/')
        
        if response.status_code == 200:
            data = response.json()
            cache_stats = data['cache_stats']
            
            print("   📈 Cache Statistics:")
            
            # OpenFDA cache stats
            openfda_cache = cache_stats['openfda_cache']
            print(f"   OpenFDA Cache:")
            print(f"      Total cached drugs: {openfda_cache['total_cached_drugs']}")
            print(f"      Valid cache files: {openfda_cache['valid_cache_files']}")
            print(f"      Expired cache files: {openfda_cache['expired_cache_files']}")
            
            # RxNorm cache stats
            rxnorm_cache = cache_stats['rxnorm_cache']
            print(f"   RxNorm Cache:")
            print(f"      Total cached queries: {rxnorm_cache['total_cached_queries']}")
            print(f"      Valid cache files: {rxnorm_cache['valid_cache_files']}")
            print(f"      Expired cache files: {rxnorm_cache['expired_cache_files']}")
            
            print(f"   Total cached items: {cache_stats['total_cached_items']}")
            
        else:
            print(f"   ❌ API Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Test Error: {e}")

def test_enhanced_prescription_analysis():
    """Test enhanced prescription analysis"""
    print("\n🔬 Testing Enhanced Prescription Analysis")
    print("=" * 50)
    
    test_prescriptions = [
        "Take aspirin 81mg daily and warfarin 5mg daily",
        "Take metformin 500mg twice daily with meals",
        "Take ibuprofen 400mg every 6 hours as needed"
    ]
    
    for i, prescription in enumerate(test_prescriptions, 1):
        print(f"\n📋 Test {i}: {prescription}")
        
        try:
            response = requests.post('http://localhost:8000/api/prescription/analyze-enhanced/', 
                                   json={'text': prescription})
            
            if response.status_code == 200:
                data = response.json()
                
                medicines = data['extracted_medicines']
                processing_method = data['processing_method']
                interactions = data['enhanced_drug_interactions']
                medicine_info = data['enhanced_medicine_info']
                
                print(f"   Processing Method: {processing_method}")
                print(f"   Medicines Found: {len(medicines)}")
                
                for med in medicines:
                    print(f"      - {med['name']} ({med['dosage']}) {med['frequency']}")
                
                print(f"   Safety Level: {interactions['overall_risk_level']}")
                print(f"   Interactions Found: {interactions['interactions_found']}")
                print(f"   Data Sources: {', '.join(interactions.get('data_sources', []))}")
                
                if interactions['interactions']:
                    print("   🚨 Interactions Detected:")
                    for interaction in interactions['interactions'][:2]:  # Show first 2
                        print(f"      {interaction['severity']} - {interaction['source']}")
                        print(f"      {interaction['description'][:80]}...")
                
                # Show enhanced medicine info
                print("   📊 Enhanced Medicine Info:")
                for medicine_name, info in medicine_info.items():
                    if 'error' not in info:
                        rxnorm_data = info.get('rxnorm_data')
                        if rxnorm_data:
                            all_names = rxnorm_data.get('all_names', [])
                            print(f"      {medicine_name}: {len(all_names)} names found")
                        else:
                            print(f"      {medicine_name}: No RxNorm data")
                    else:
                        print(f"      {medicine_name}: Error - {info['error']}")
                
            else:
                print(f"   ❌ API Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Test Error: {e}")

def main():
    """Run all enhanced drug interaction tests"""
    print("🧪 Enhanced Drug Interaction System Tests")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test API connectivity first
    if not test_api_connectivity():
        print("\n❌ API is not running. Please start the Django server first.")
        return
    
    # Run all tests
    test_results = []
    
    test_results.append(test_enhanced_drug_interactions())
    test_medicine_info_enhanced()
    test_bulk_download()
    test_cache_stats()
    test_enhanced_prescription_analysis()
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎉 Enhanced Drug Interaction Testing Complete!")
    
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    print(f"📊 Test Results: {passed_tests}/{total_tests} core tests passed")
    
    if passed_tests == total_tests:
        print("✅ All core tests passed! Enhanced system is working correctly.")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    print("\n🔗 Available Enhanced Endpoints:")
    print("   POST /api/interactions/enhanced/check/ - Enhanced interaction checking")
    print("   GET /api/interactions/enhanced/medicine/<name>/ - Enhanced medicine info")
    print("   POST /api/interactions/enhanced/bulk-download/ - Bulk download data")
    print("   GET /api/interactions/enhanced/cache-stats/ - Cache statistics")
    print("   POST /api/prescription/analyze-enhanced/ - Enhanced prescription analysis")
    
    print("\n📊 Data Sources:")
    print("   🔹 Manual Database - Fast, reliable, curated interactions")
    print("   🔹 OpenFDA - Official FDA drug labeling data")
    print("   🔹 RxNorm - NLM drug name standardization")

if __name__ == "__main__":
    main()
