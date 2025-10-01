#!/usr/bin/env python3
"""
Test script for Drug Interaction Checking System
Tests all drug interaction endpoints and functionality
"""

import sys
import os
import requests
import json
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

def test_drug_interaction_checking():
    """Test drug interaction checking functionality"""
    print("\n🧪 Testing Drug Interaction Checking")
    print("=" * 50)
    
    # Test cases with known interactions
    test_cases = [
        {
            'name': 'High Risk - Warfarin + Aspirin',
            'medicines': ['warfarin', 'aspirin'],
            'expected_severity': 'HIGH',
            'expected_interactions': 1
        },
        {
            'name': 'Medium Risk - Atorvastatin + Grapefruit',
            'medicines': ['atorvastatin', 'grapefruit'],
            'expected_severity': 'MEDIUM',
            'expected_interactions': 1
        },
        {
            'name': 'Low Risk - Calcium Carbonate + Tetracycline',
            'medicines': ['calcium carbonate', 'tetracycline'],
            'expected_severity': 'LOW',
            'expected_interactions': 1
        },
        {
            'name': 'Info - Vitamin D + Calcium',
            'medicines': ['vitamin d', 'calcium'],
            'expected_severity': 'INFO',
            'expected_interactions': 1
        },
        {
            'name': 'No Interactions - Safe Combination',
            'medicines': ['metformin', 'vitamin d'],
            'expected_severity': 'NONE',
            'expected_interactions': 0
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n📋 Testing: {test_case['name']}")
        print(f"   Medicines: {test_case['medicines']}")
        
        try:
            response = requests.post('http://localhost:8000/api/interactions/check/', 
                                   json={'medicines': test_case['medicines']})
            
            if response.status_code == 200:
                data = response.json()
                interaction_data = data['data']
                
                actual_severity = interaction_data['overall_risk_level']
                actual_interactions = interaction_data['interactions_found']
                
                print(f"   Expected Severity: {test_case['expected_severity']}")
                print(f"   Actual Severity: {actual_severity}")
                print(f"   Expected Interactions: {test_case['expected_interactions']}")
                print(f"   Actual Interactions: {actual_interactions}")
                
                # Check if results match expectations
                severity_match = actual_severity == test_case['expected_severity']
                interactions_match = actual_interactions == test_case['expected_interactions']
                
                if severity_match and interactions_match:
                    print("   ✅ PASS")
                    results.append(True)
                else:
                    print("   ❌ FAIL")
                    results.append(False)
                
                # Show interaction details if found
                if interaction_data['interactions']:
                    for interaction in interaction_data['interactions']:
                        print(f"   🚨 {interaction['severity']} - {interaction['interaction_type']}")
                        print(f"      Description: {interaction['description']}")
                        print(f"      Recommendation: {interaction['recommendation']}")
                
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
    print(f"\n📊 Drug Interaction Tests: {passed}/{total} passed")
    
    return passed == total

def test_medicine_specific_interactions():
    """Test getting interactions for specific medicines"""
    print("\n🔍 Testing Medicine-Specific Interactions")
    print("=" * 50)
    
    test_medicines = ['warfarin', 'metformin', 'aspirin', 'vitamin d']
    
    for medicine in test_medicines:
        print(f"\n📋 Testing interactions for: {medicine}")
        
        try:
            response = requests.get(f'http://localhost:8000/api/interactions/medicine/{medicine}/')
            
            if response.status_code == 200:
                data = response.json()
                interactions = data['interactions']
                total = data['total_interactions']
                
                print(f"   Total interactions found: {total}")
                
                if interactions:
                    for interaction in interactions[:3]:  # Show first 3
                        print(f"   🚨 {interaction['severity']} - {interaction['interaction_type']}")
                        print(f"      With: {interaction.get('other_medicine', 'Unknown')}")
                        print(f"      Description: {interaction['description']}")
                else:
                    print("   ✅ No known interactions")
                
            else:
                print(f"   ❌ API Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Test Error: {e}")

def test_interaction_details():
    """Test getting detailed interaction information"""
    print("\n📖 Testing Interaction Details")
    print("=" * 50)
    
    test_pairs = [
        ('warfarin', 'aspirin'),
        ('metformin', 'alcohol'),
        ('vitamin d', 'calcium')
    ]
    
    for med1, med2 in test_pairs:
        print(f"\n📋 Testing interaction details: {med1} + {med2}")
        
        try:
            response = requests.get(f'http://localhost:8000/api/interactions/{med1}/{med2}/')
            
            if response.status_code == 200:
                data = response.json()
                interaction = data['interaction']
                
                if interaction:
                    print(f"   Severity: {interaction['severity']}")
                    print(f"   Type: {interaction['interaction_type']}")
                    print(f"   Description: {interaction['description']}")
                    print(f"   Mechanism: {interaction['mechanism']}")
                    print(f"   Recommendation: {interaction['recommendation']}")
                    print(f"   Alternatives: {', '.join(interaction['alternatives'])}")
                    print(f"   Monitoring: {interaction['monitoring']}")
                else:
                    print("   ✅ No interaction found")
                
            else:
                print(f"   ❌ API Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Test Error: {e}")

def test_prescription_safety_validation():
    """Test prescription safety validation"""
    print("\n🛡️ Testing Prescription Safety Validation")
    print("=" * 50)
    
    test_prescriptions = [
        {
            'name': 'Safe Prescription',
            'extracted_medicines': [
                {'name': 'metformin', 'dosage': '500mg', 'frequency': 'twice daily'},
                {'name': 'vitamin d', 'dosage': '1000 IU', 'frequency': 'daily'}
            ]
        },
        {
            'name': 'High Risk Prescription',
            'extracted_medicines': [
                {'name': 'warfarin', 'dosage': '5mg', 'frequency': 'daily'},
                {'name': 'aspirin', 'dosage': '81mg', 'frequency': 'daily'}
            ]
        }
    ]
    
    for prescription in test_prescriptions:
        print(f"\n📋 Testing: {prescription['name']}")
        print(f"   Medicines: {[med['name'] for med in prescription['extracted_medicines']]}")
        
        try:
            response = requests.post('http://localhost:8000/api/interactions/validate-safety/', 
                                   json=prescription)
            
            if response.status_code == 200:
                data = response.json()
                safety_data = data['data']
                
                safety_level = safety_data['safety_level']
                interaction_results = safety_data['interaction_results']
                
                print(f"   Safety Level: {safety_level}")
                print(f"   Interactions Found: {interaction_results['interactions_found']}")
                print(f"   Severity Summary: {interaction_results['severity_summary']}")
                
                if safety_data['recommendations']:
                    print("   Recommendations:")
                    for rec in safety_data['recommendations']:
                        print(f"      {rec}")
                
            else:
                print(f"   ❌ API Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Test Error: {e}")

def test_prescription_analysis_with_safety():
    """Test prescription analysis with safety checking"""
    print("\n🔬 Testing Prescription Analysis with Safety")
    print("=" * 50)
    
    test_prescriptions = [
        "Take warfarin 5mg daily and aspirin 81mg daily for blood thinning",
        "Take metformin 500mg twice daily with meals for diabetes",
        "Take atorvastatin 20mg daily and avoid grapefruit juice"
    ]
    
    for i, prescription in enumerate(test_prescriptions, 1):
        print(f"\n📋 Test {i}: {prescription}")
        
        try:
            response = requests.post('http://localhost:8000/api/prescription/analyze-with-safety/', 
                                   json={'text': prescription})
            
            if response.status_code == 200:
                data = response.json()
                
                medicines = data['extracted_medicines']
                processing_method = data['processing_method']
                confidence = data['confidence_score']
                interactions = data['drug_interactions']
                safety = data['safety_validation']
                
                print(f"   Processing Method: {processing_method}")
                print(f"   Confidence Score: {confidence}")
                print(f"   Medicines Found: {len(medicines)}")
                
                for med in medicines:
                    print(f"      - {med['name']} ({med['dosage']}) {med['frequency']}")
                
                print(f"   Safety Level: {safety['safety_level']}")
                print(f"   Interactions Found: {interactions['interactions_found']}")
                
                if interactions['interactions']:
                    print("   🚨 Interactions Detected:")
                    for interaction in interactions['interactions']:
                        print(f"      {interaction['severity']} - {interaction['interaction_type']}")
                        print(f"      {interaction['description']}")
                
            else:
                print(f"   ❌ API Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Test Error: {e}")

def main():
    """Run all drug interaction tests"""
    print("🧪 Drug Interaction Checking System Tests")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test API connectivity first
    if not test_api_connectivity():
        print("\n❌ API is not running. Please start the Django server first.")
        return
    
    # Run all tests
    test_results = []
    
    test_results.append(test_drug_interaction_checking())
    test_medicine_specific_interactions()
    test_interaction_details()
    test_prescription_safety_validation()
    test_prescription_analysis_with_safety()
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎉 Drug Interaction Testing Complete!")
    
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    print(f"📊 Test Results: {passed_tests}/{total_tests} core tests passed")
    
    if passed_tests == total_tests:
        print("✅ All core tests passed! Drug interaction system is working correctly.")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    print("\n🔗 Available Endpoints:")
    print("   POST /api/interactions/check/ - Check drug interactions")
    print("   POST /api/interactions/validate-safety/ - Validate prescription safety")
    print("   GET /api/interactions/medicine/<name>/ - Get medicine interactions")
    print("   GET /api/interactions/<med1>/<med2>/ - Get interaction details")
    print("   POST /api/prescription/analyze-with-safety/ - Analyze with safety")

if __name__ == "__main__":
    main()
