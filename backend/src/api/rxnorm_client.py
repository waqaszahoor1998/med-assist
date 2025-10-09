"""
RxNorm Client for Drug Name Standardization
Provides access to NLM's RxNorm database for drug name mapping
"""

import requests
import json
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import time

class RxNormClient:
    """
    Client for accessing RxNorm drug database
    """
    
    def __init__(self, cache_dir="datasets/cache/rxnorm"):
        self.base_url = "https://rxnav.nlm.nih.gov/REST"
        self.cache_dir = cache_dir
        self.cache_duration = timedelta(days=30)  # Cache for 30 days (RxNorm changes less frequently)
        
        # Create cache directory
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests
    
    def _rate_limit(self):
        """Ensure we don't exceed API rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_time = time.time()
    
    def _get_cache_path(self, query: str, endpoint: str) -> str:
        """Get cache file path for a query"""
        safe_query = query.lower().replace(' ', '_').replace('/', '_').replace('?', '').replace('&', '')
        return os.path.join(self.cache_dir, f"{endpoint}_{safe_query}.json")
    
    def _is_cache_valid(self, cache_path: str) -> bool:
        """Check if cache file is still valid"""
        if not os.path.exists(cache_path):
            return False
        
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        return datetime.now() - file_time < self.cache_duration
    
    def _save_to_cache(self, query: str, endpoint: str, data: Dict):
        """Save data to cache"""
        cache_path = self._get_cache_path(query, endpoint)
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f, indent=2)
            logging.info(f"Cached RxNorm data for {endpoint}: {query}")
        except Exception as e:
            logging.error(f"Error caching RxNorm data: {e}")
    
    def _load_from_cache(self, query: str, endpoint: str) -> Optional[Dict]:
        """Load data from cache"""
        cache_path = self._get_cache_path(query, endpoint)
        
        if not self._is_cache_valid(cache_path):
            return None
        
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
            logging.info(f"Loaded cached RxNorm data for {endpoint}: {query}")
            return data
        except Exception as e:
            logging.error(f"Error loading cached RxNorm data: {e}")
            return None
    
    def search_drugs(self, drug_name: str, use_cache: bool = True) -> Dict:
        """
        Search for drugs by name in RxNorm
        """
        # Check cache first
        if use_cache:
            cached_data = self._load_from_cache(drug_name, "search")
            if cached_data:
                return cached_data
        
        # Make API request
        self._rate_limit()
        
        try:
            url = f"{self.base_url}/drugs.json?name={drug_name}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                processed_data = {
                    'query': drug_name,
                    'results': data,
                    'fetched_at': datetime.now().isoformat(),
                    'source': 'RxNorm'
                }
                
                # Save to cache
                if use_cache:
                    self._save_to_cache(drug_name, "search", processed_data)
                
                return processed_data
            else:
                logging.error(f"RxNorm API error for {drug_name}: {response.status_code}")
                return {'query': drug_name, 'error': f'API error: {response.status_code}'}
                
        except Exception as e:
            logging.error(f"Error fetching RxNorm data for {drug_name}: {e}")
            return {'query': drug_name, 'error': str(e)}
    
    def get_drug_info(self, rxcui: str, use_cache: bool = True) -> Dict:
        """
        Get detailed drug information by RxCUI (RxNorm Concept Unique Identifier)
        """
        # Check cache first
        if use_cache:
            cached_data = self._load_from_cache(rxcui, "drug_info")
            if cached_data:
                return cached_data
        
        # Make API request
        self._rate_limit()
        
        try:
            url = f"{self.base_url}/rxcui/{rxcui}/properties.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                processed_data = {
                    'rxcui': rxcui,
                    'properties': data,
                    'fetched_at': datetime.now().isoformat(),
                    'source': 'RxNorm'
                }
                
                # Save to cache
                if use_cache:
                    self._save_to_cache(rxcui, "drug_info", processed_data)
                
                return processed_data
            else:
                logging.error(f"RxNorm API error for RxCUI {rxcui}: {response.status_code}")
                return {'rxcui': rxcui, 'error': f'API error: {response.status_code}'}
                
        except Exception as e:
            logging.error(f"Error fetching RxNorm drug info for {rxcui}: {e}")
            return {'rxcui': rxcui, 'error': str(e)}
    
    def get_drug_interactions(self, rxcui: str, use_cache: bool = True) -> Dict:
        """
        Get drug interactions by RxCUI
        """
        # Check cache first
        if use_cache:
            cached_data = self._load_from_cache(rxcui, "interactions")
            if cached_data:
                return cached_data
        
        # Make API request
        self._rate_limit()
        
        try:
            url = f"{self.base_url}/rxcui/{rxcui}/interactions.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                processed_data = {
                    'rxcui': rxcui,
                    'interactions': data,
                    'fetched_at': datetime.now().isoformat(),
                    'source': 'RxNorm'
                }
                
                # Save to cache
                if use_cache:
                    self._save_to_cache(rxcui, "interactions", processed_data)
                
                return processed_data
            else:
                logging.error(f"RxNorm interactions API error for RxCUI {rxcui}: {response.status_code}")
                return {'rxcui': rxcui, 'error': f'API error: {response.status_code}'}
                
        except Exception as e:
            logging.error(f"Error fetching RxNorm interactions for {rxcui}: {e}")
            return {'rxcui': rxcui, 'error': str(e)}
    
    def standardize_drug_name(self, drug_name: str) -> Tuple[str, Optional[str]]:
        """
        Standardize drug name using RxNorm
        Returns (standardized_name, rxcui)
        """
        search_result = self.search_drugs(drug_name)
        
        if 'error' in search_result:
            return drug_name, None
        
        # Extract drug concepts from search results
        drug_group = search_result.get('results', {}).get('drugGroup', {})
        concepts = drug_group.get('conceptGroup', [])
        
        for concept_group in concepts:
            if concept_group.get('tty') == 'IN':  # Ingredient
                concepts_list = concept_group.get('conceptProperties', [])
                if concepts_list:
                    first_concept = concepts_list[0]
                    standardized_name = first_concept.get('name', drug_name)
                    rxcui = first_concept.get('rxcui', None)
                    return standardized_name, rxcui
        
        # If no ingredient found, return first concept
        for concept_group in concepts:
            concepts_list = concept_group.get('conceptProperties', [])
            if concepts_list:
                first_concept = concepts_list[0]
                standardized_name = first_concept.get('name', drug_name)
                rxcui = first_concept.get('rxcui', None)
                return standardized_name, rxcui
        
        return drug_name, None
    
    def get_all_drug_names(self, rxcui: str) -> List[str]:
        """
        Get all names (brand, generic, etc.) for a drug by RxCUI
        """
        search_result = self.search_drugs(f"rxcui:{rxcui}")
        
        if 'error' in search_result:
            return []
        
        drug_names = []
        drug_group = search_result.get('results', {}).get('drugGroup', {})
        concepts = drug_group.get('conceptGroup', [])
        
        for concept_group in concepts:
            concepts_list = concept_group.get('conceptProperties', [])
            for concept in concepts_list:
                name = concept.get('name', '')
                if name and name not in drug_names:
                    drug_names.append(name)
        
        return drug_names
    
    def find_drug_by_name(self, drug_name: str) -> Optional[Dict]:
        """
        Find drug information by name, returning standardized data
        """
        standardized_name, rxcui = self.standardize_drug_name(drug_name)
        
        if not rxcui:
            return None
        
        drug_info = self.get_drug_info(rxcui)
        interactions = self.get_drug_interactions(rxcui)
        all_names = self.get_all_drug_names(rxcui)
        
        return {
            'original_name': drug_name,
            'standardized_name': standardized_name,
            'rxcui': rxcui,
            'all_names': all_names,
            'drug_info': drug_info,
            'interactions': interactions,
            'source': 'RxNorm'
        }
    
    def get_cache_stats(self) -> Dict:
        """
        Get statistics about cached data
        """
        cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.json')]
        
        total_files = len(cache_files)
        valid_files = 0
        expired_files = 0
        
        for file in cache_files:
            file_path = os.path.join(self.cache_dir, file)
            if self._is_cache_valid(file_path):
                valid_files += 1
            else:
                expired_files += 1
        
        return {
            'total_cached_queries': total_files,
            'valid_cache_files': valid_files,
            'expired_cache_files': expired_files,
            'cache_directory': self.cache_dir
        }
    
    def clear_cache(self):
        """
        Clear all cached data
        """
        try:
            for file in os.listdir(self.cache_dir):
                if file.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, file))
            logging.info("RxNorm cache cleared successfully")
        except Exception as e:
            logging.error(f"Error clearing RxNorm cache: {e}")

# Global instance
rxnorm_client = RxNormClient()
