#!/usr/bin/env python3
"""
Medicine Data Collection Script
Collects medicine information from various public APIs and sources
"""

import requests
import json
import csv
import time
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MedicineDataCollector:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.raw_dir = self.base_dir / "raw"
        self.processed_dir = self.base_dir / "processed"
        
        # Create directories if they don't exist
        self.raw_dir.mkdir(exist_ok=True)
        self.processed_dir.mkdir(exist_ok=True)

    def collect_openfda_data(self, limit=1000):
        """
        Collect drug data from OpenFDA API (no API key required for basic access)
        """
        logger.info("Collecting data from OpenFDA...")
        
        base_url = "https://api.fda.gov/drug/label.json"
        medicines = []
        
        try:
            # Get drug labels with basic information
            params = {
                'limit': min(limit, 100),  # API limit is 100 per request
                'search': 'effective_time:[20200101+TO+20241231]'  # Recent drugs
            }
            
            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            for result in data.get('results', []):
                medicine = {
                    'name': self._extract_drug_name(result),
                    'generic_name': result.get('generic_name', [''])[0] if result.get('generic_name') else '',
                    'brand_name': result.get('openfda', {}).get('brand_name', [''])[0] if result.get('openfda', {}).get('brand_name') else '',
                    'manufacturer': result.get('openfda', {}).get('manufacturer_name', [''])[0] if result.get('openfda', {}).get('manufacturer_name') else '',
                    'dosage_form': result.get('dosage_form', [''])[0] if result.get('dosage_form') else '',
                    'route': result.get('route', [''])[0] if result.get('route') else '',
                    'warnings': self._extract_warnings(result),
                    'indications': self._extract_indications(result),
                    'dosage_info': self._extract_dosage_info(result),
                    'source': 'OpenFDA'
                }
                
                if medicine['name']:  # Only add if we have a name
                    medicines.append(medicine)
            
            # Save raw data
            output_file = self.raw_dir / "openfda_medicines.json"
            with open(output_file, 'w') as f:
                json.dump(medicines, f, indent=2)
            
            logger.info(f"Collected {len(medicines)} medicines from OpenFDA")
            return medicines
            
        except requests.RequestException as e:
            logger.error(f"Error collecting OpenFDA data: {e}")
            return []

    def collect_common_medicines(self):
        """
        Create a dataset of common medicines with basic information
        This serves as a fallback if APIs are unavailable
        """
        logger.info("Creating common medicines dataset...")
        
        common_medicines = [
            {
                'name': 'Paracetamol',
                'generic_name': 'Acetaminophen',
                'brand_names': ['Tylenol', 'Panadol', 'Calpol'],
                'dosage_forms': ['tablet', 'capsule', 'liquid', 'suppository'],
                'common_doses': ['500mg', '650mg', '1000mg'],
                'indications': ['pain relief', 'fever reduction'],
                'warnings': ['liver damage with overdose', 'alcohol interaction'],
                'max_daily_dose': '4000mg',
                'frequency': 'every 4-6 hours',
                'source': 'manual'
            },
            {
                'name': 'Ibuprofen',
                'generic_name': 'Ibuprofen',
                'brand_names': ['Advil', 'Motrin', 'Nurofen'],
                'dosage_forms': ['tablet', 'capsule', 'liquid', 'gel'],
                'common_doses': ['200mg', '400mg', '600mg', '800mg'],
                'indications': ['pain relief', 'inflammation', 'fever'],
                'warnings': ['stomach irritation', 'kidney problems', 'heart risks'],
                'max_daily_dose': '2400mg',
                'frequency': 'every 6-8 hours',
                'source': 'manual'
            },
            {
                'name': 'Amoxicillin',
                'generic_name': 'Amoxicillin',
                'brand_names': ['Amoxil', 'Trimox'],
                'dosage_forms': ['capsule', 'tablet', 'liquid'],
                'common_doses': ['250mg', '500mg', '875mg'],
                'indications': ['bacterial infections', 'respiratory infections'],
                'warnings': ['allergic reactions', 'diarrhea', 'complete course required'],
                'frequency': 'every 8 hours',
                'duration': '7-10 days',
                'source': 'manual'
            },
            {
                'name': 'Metformin',
                'generic_name': 'Metformin',
                'brand_names': ['Glucophage', 'Glumetza'],
                'dosage_forms': ['tablet', 'extended-release tablet'],
                'common_doses': ['500mg', '850mg', '1000mg'],
                'indications': ['type 2 diabetes', 'blood sugar control'],
                'warnings': ['lactic acidosis', 'kidney function monitoring'],
                'frequency': 'twice daily with meals',
                'source': 'manual'
            },
            {
                'name': 'Lisinopril',
                'generic_name': 'Lisinopril',
                'brand_names': ['Prinivil', 'Zestril'],
                'dosage_forms': ['tablet'],
                'common_doses': ['5mg', '10mg', '20mg', '40mg'],
                'indications': ['high blood pressure', 'heart failure'],
                'warnings': ['cough', 'low blood pressure', 'kidney problems'],
                'frequency': 'once daily',
                'source': 'manual'
            },
            {
                'name': 'Atorvastatin',
                'generic_name': 'Atorvastatin',
                'brand_names': ['Lipitor'],
                'dosage_forms': ['tablet'],
                'common_doses': ['10mg', '20mg', '40mg', '80mg'],
                'indications': ['high cholesterol', 'heart disease prevention'],
                'warnings': ['muscle pain', 'liver problems'],
                'frequency': 'once daily',
                'source': 'manual'
            },
            {
                'name': 'Omeprazole',
                'generic_name': 'Omeprazole',
                'brand_names': ['Prilosec', 'Losec'],
                'dosage_forms': ['capsule', 'tablet'],
                'common_doses': ['20mg', '40mg'],
                'indications': ['acid reflux', 'stomach ulcers', 'GERD'],
                'warnings': ['bone fractures with long-term use', 'vitamin B12 deficiency'],
                'frequency': 'once daily before meals',
                'source': 'manual'
            }
        ]
        
        # Save to file
        output_file = self.raw_dir / "common_medicines.json"
        with open(output_file, 'w') as f:
            json.dump(common_medicines, f, indent=2)
        
        logger.info(f"Created dataset with {len(common_medicines)} common medicines")
        return common_medicines

    def _extract_drug_name(self, result):
        """Extract the primary drug name from FDA result"""
        # Try different fields to get the drug name
        if result.get('openfda', {}).get('generic_name'):
            return result['openfda']['generic_name'][0]
        elif result.get('openfda', {}).get('brand_name'):
            return result['openfda']['brand_name'][0]
        elif result.get('active_ingredient'):
            return result['active_ingredient'][0] if result['active_ingredient'] else ''
        return ''

    def _extract_warnings(self, result):
        """Extract warnings from FDA result"""
        warnings = []
        if result.get('warnings'):
            warnings.extend(result['warnings'])
        if result.get('contraindications'):
            warnings.extend(result['contraindications'])
        return warnings[:3]  # Limit to first 3 warnings

    def _extract_indications(self, result):
        """Extract indications/uses from FDA result"""
        indications = []
        if result.get('indications_and_usage'):
            indications.extend(result['indications_and_usage'])
        return indications[:3]  # Limit to first 3 indications

    def _extract_dosage_info(self, result):
        """Extract dosage information from FDA result"""
        dosage_info = {}
        if result.get('dosage_and_administration'):
            dosage_info['administration'] = result['dosage_and_administration'][0]
        if result.get('dosage_form'):
            dosage_info['form'] = result['dosage_form'][0]
        return dosage_info

    def run_collection(self):
        """Run the complete data collection process"""
        logger.info("Starting medicine data collection...")
        
        all_medicines = []
        
        # Collect from OpenFDA
        openfda_medicines = self.collect_openfda_data()
        all_medicines.extend(openfda_medicines)
        
        # Add common medicines
        common_medicines = self.collect_common_medicines()
        all_medicines.extend(common_medicines)
        
        # Save combined dataset
        output_file = self.processed_dir / "all_medicines.json"
        with open(output_file, 'w') as f:
            json.dump(all_medicines, f, indent=2)
        
        # Create CSV version for easier viewing
        csv_file = self.processed_dir / "all_medicines.csv"
        if all_medicines:
            with open(csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=all_medicines[0].keys())
                writer.writeheader()
                for medicine in all_medicines:
                    # Convert lists to strings for CSV
                    row = {}
                    for key, value in medicine.items():
                        if isinstance(value, list):
                            row[key] = '; '.join(str(v) for v in value)
                        else:
                            row[key] = str(value) if value else ''
                    writer.writerow(row)
        
        logger.info(f"Collection complete! Total medicines: {len(all_medicines)}")
        logger.info(f"Data saved to: {output_file}")
        logger.info(f"CSV saved to: {csv_file}")
        
        return all_medicines

if __name__ == "__main__":
    collector = MedicineDataCollector()
    medicines = collector.run_collection()
    print(f"Successfully collected {len(medicines)} medicines!")
