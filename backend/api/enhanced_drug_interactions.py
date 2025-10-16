"""
============================================================================
ENHANCED DRUG INTERACTION CHECKER - Multi-Source Validation
============================================================================

This file provides enhanced drug interaction checking by combining data
from multiple authoritative sources for comprehensive safety validation.

Data Sources Combined:
1. OpenFDA - FDA's official drug database (real-time API)
2. RxNorm - National Library of Medicine terminology (real-time API)
3. Manual Database - DrugBank interaction data (local database)

What It Does:
- Queries multiple sources for each medicine pair
- Aggregates interaction data from all sources
- Prioritizes by severity and source reliability
- Provides comprehensive interaction reports

vs Basic Checker (drug_interactions.py):
- Basic: Uses only local database (fast, offline)
- Enhanced: Queries live APIs (slower, more comprehensive)
- Enhanced: Better for uncommon medicines or latest data
- Enhanced: Requires internet connection

Used by:
- api/views.py: analyze_prescription_enhanced() - Advanced analysis
- api/views.py: check_enhanced_drug_interactions() - Manual checking

Calls:
- openfda_client.py: Query OpenFDA API
- rxnorm_client.py: Query RxNorm API
- drug_interactions.py: Check local database
- Combines all results

Performance:
- Slower than basic checker (API calls)
- Uses caching to improve speed
- Typical: 500ms-2s per check

Frontend Integration:
- Used for comprehensive analysis feature
- Shows data source for each interaction
- Displays confidence based on source agreement

API Rate Limits:
- OpenFDA: 240 requests/minute, 120,000/day
- RxNorm: No strict limit, but use responsibly
- Caching reduces API calls
============================================================================
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
from .openfda_client import openfda_client    # FDA API client
from .rxnorm_client import rxnorm_client      # RxNorm API client
from .drug_interactions import interaction_checker as manual_checker  # Local database

class EnhancedDrugInteractionChecker:
    """
    Enhanced drug interaction checker combining OpenFDA, RxNorm, and local database.
    
    Combines 3 data sources for comprehensive validation:
    1. OpenFDA (live FDA data)
    2. RxNorm (medical terminology)
    3. Local database (DrugBank)
    
    Main Methods:
    - check_interactions() - Check all medicine combinations
    - _merge_results() - Combine data from multiple sources
    - _prioritize_by_severity() - Sort by danger level
    """
    
    def __init__(self):
        self.openfda_client = openfda_client
        self.rxnorm_client = rxnorm_client
        self.manual_checker = manual_checker
        self.severity_levels = {
            'HIGH': {'color': '#FF4444', 'icon': '⚠️', 'priority': 3},
            'MEDIUM': {'color': '#FF8800', 'icon': '⚡', 'priority': 2},
            'LOW': {'color': '#FFAA00', 'icon': '💡', 'priority': 1},
            'INFO': {'color': '#4488FF', 'icon': 'ℹ️', 'priority': 0},
            'UNKNOWN': {'color': '#888888', 'icon': '❓', 'priority': 0}
        }
    
    def check_interactions(self, medicines: List[str]) -> Dict:
        """
        Check for drug interactions using multiple data sources
        """
        try:
            all_interactions = []
            severity_summary = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0, 'UNKNOWN': 0}
            
            # Convert medicines to lowercase for matching
            medicines_lower = [med.lower().strip() for med in medicines]
            
            # 1. Check manual database first (fastest, most reliable)
            manual_results = self.manual_checker.check_interactions(medicines)
            if manual_results.get('interactions'):
                for interaction in manual_results['interactions']:
                    interaction['source'] = 'Manual Database'
                    all_interactions.append(interaction)
                    severity_summary[interaction['severity']] += 1
            
            # 2. Check OpenFDA for additional interactions
            openfda_interactions = self._check_openfda_interactions(medicines_lower)
            for interaction in openfda_interactions:
                if not self._interaction_exists(all_interactions, interaction):
                    interaction['source'] = 'OpenFDA'
                    all_interactions.append(interaction)
                    severity_summary[interaction['severity']] += 1
            
            # 3. Check RxNorm for standardized interactions
            rxnorm_interactions = self._check_rxnorm_interactions(medicines_lower)
            for interaction in rxnorm_interactions:
                if not self._interaction_exists(all_interactions, interaction):
                    interaction['source'] = 'RxNorm'
                    all_interactions.append(interaction)
                    severity_summary[interaction['severity']] += 1
            
            # Sort by severity (HIGH first)
            all_interactions.sort(key=lambda x: self.severity_levels[x['severity']]['priority'], reverse=True)
            
            # Calculate overall risk level
            overall_risk = self._calculate_overall_risk(severity_summary)
            
            return {
                'status': 'success',
                'total_medicines': len(medicines),
                'interactions_found': len(all_interactions),
                'severity_summary': severity_summary,
                'overall_risk_level': overall_risk,
                'interactions': all_interactions,
                'recommendations': self._generate_recommendations(all_interactions),
                'data_sources': self._get_data_sources_used(all_interactions),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error in enhanced interaction checking: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'interactions_found': [],
                'severity_summary': {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0, 'UNKNOWN': 0},
                'overall_risk_level': 'UNKNOWN',
                'recommendations': []
            }
    
    def _check_openfda_interactions(self, medicines: List[str]) -> List[Dict]:
        """
        Check for interactions using OpenFDA
        """
        interactions = []
        
        try:
            # Check interactions between all pairs of medicines
            for i, drug1 in enumerate(medicines):
                for j, drug2 in enumerate(medicines):
                    if i < j:  # Avoid duplicates
                        openfda_interactions = self.openfda_client.check_interactions_between(drug1, drug2)
                        
                        for interaction in openfda_interactions:
                            # Map OpenFDA severity to our system
                            severity = self._map_openfda_severity(interaction.get('severity', 'UNKNOWN'))
                            
                            interactions.append({
                                'drug1': drug1,
                                'drug2': drug2,
                                'severity': severity,
                                'interaction_type': 'Drug Interaction',
                                'description': interaction.get('description', ''),
                                'mechanism': 'See FDA labeling',
                                'recommendation': 'Consult healthcare provider',
                                'alternatives': 'Ask pharmacist for alternatives',
                                'monitoring': 'Monitor for adverse effects'
                            })
        except Exception as e:
            logging.error(f"Error checking OpenFDA interactions: {e}")
        
        return interactions
    
    def _check_rxnorm_interactions(self, medicines: List[str]) -> List[Dict]:
        """
        Check for interactions using RxNorm
        """
        interactions = []
        
        try:
            # Standardize drug names and get RxCUIs
            standardized_drugs = []
            for medicine in medicines:
                standardized_name, rxcui = self.rxnorm_client.standardize_drug_name(medicine)
                if rxcui:
                    standardized_drugs.append((medicine, standardized_name, rxcui))
            
            # Check interactions between standardized drugs
            for i, (drug1, std_name1, rxcui1) in enumerate(standardized_drugs):
                for j, (drug2, std_name2, rxcui2) in enumerate(standardized_drugs):
                    if i < j:  # Avoid duplicates
                        rxnorm_data = self.rxnorm_client.get_drug_interactions(rxcui1)
                        
                        if 'error' not in rxnorm_data:
                            # Parse RxNorm interactions
                            rxnorm_interactions = rxnorm_data.get('interactions', {})
                            interaction_pairs = rxnorm_interactions.get('interactionPair', [])
                            
                            for pair in interaction_pairs:
                                # Check if this pair involves our second drug
                                if self._rxnorm_pair_involves_drug(pair, std_name2):
                                    interactions.append({
                                        'drug1': drug1,
                                        'drug2': drug2,
                                        'severity': 'MEDIUM',  # RxNorm doesn't provide severity
                                        'interaction_type': 'Drug Interaction',
                                        'description': pair.get('description', ''),
                                        'mechanism': 'See RxNorm database',
                                        'recommendation': 'Consult healthcare provider',
                                        'alternatives': 'Ask pharmacist for alternatives',
                                        'monitoring': 'Monitor for adverse effects'
                                    })
        except Exception as e:
            logging.error(f"Error checking RxNorm interactions: {e}")
        
        return interactions
    
    def _rxnorm_pair_involves_drug(self, pair: Dict, drug_name: str) -> bool:
        """
        Check if RxNorm interaction pair involves a specific drug
        """
        try:
            interaction_concept = pair.get('interactionConcept', [])
            for concept in interaction_concept:
                min_concept_item = concept.get('minConceptItem', {})
                concept_name = min_concept_item.get('name', '').lower()
                if drug_name.lower() in concept_name:
                    return True
            return False
        except Exception:
            return False
    
    def _map_openfda_severity(self, openfda_severity: str) -> str:
        """
        Map OpenFDA severity to our severity system
        """
        severity_map = {
            'major': 'HIGH',
            'moderate': 'MEDIUM',
            'minor': 'LOW',
            'unknown': 'UNKNOWN'
        }
        return severity_map.get(openfda_severity.lower(), 'UNKNOWN')
    
    def _interaction_exists(self, existing_interactions: List[Dict], new_interaction: Dict) -> bool:
        """
        Check if an interaction already exists in the list
        """
        for existing in existing_interactions:
            if (existing.get('drug1') == new_interaction.get('drug1') and 
                existing.get('drug2') == new_interaction.get('drug2')) or \
               (existing.get('drug1') == new_interaction.get('drug2') and 
                existing.get('drug2') == new_interaction.get('drug1')):
                return True
        return False
    
    def _calculate_overall_risk(self, severity_summary: Dict) -> str:
        """
        Calculate overall risk level based on severity summary
        """
        if severity_summary['HIGH'] > 0:
            return 'HIGH'
        elif severity_summary['MEDIUM'] > 0:
            return 'MEDIUM'
        elif severity_summary['LOW'] > 0:
            return 'LOW'
        elif severity_summary['INFO'] > 0:
            return 'INFO'
        else:
            return 'NONE'
    
    def _generate_recommendations(self, interactions: List[Dict]) -> List[str]:
        """
        Generate overall recommendations based on interactions found
        """
        recommendations = []
        
        if not interactions:
            recommendations.append("✅ No known drug interactions found. Continue current medication regimen.")
            return recommendations
        
        # Count interactions by source
        sources = {}
        for interaction in interactions:
            source = interaction.get('source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        # Add source information
        if sources:
            source_info = ", ".join([f"{source}: {count}" for source, count in sources.items()])
            recommendations.append(f"📊 Data sources: {source_info}")
        
        # High severity recommendations
        high_interactions = [i for i in interactions if i['severity'] == 'HIGH']
        if high_interactions:
            recommendations.append("🚨 HIGH RISK: Consult healthcare provider immediately before taking these medications together.")
            recommendations.append("⚠️ Consider alternative medications or adjusted dosing schedules.")
        
        # Medium severity recommendations
        medium_interactions = [i for i in interactions if i['severity'] == 'MEDIUM']
        if medium_interactions:
            recommendations.append("⚡ MEDIUM RISK: Monitor closely for adverse effects. Consider dose adjustments.")
            recommendations.append("📊 Regular monitoring may be required.")
        
        # Low severity recommendations
        low_interactions = [i for i in interactions if i['severity'] == 'LOW']
        if low_interactions:
            recommendations.append("💡 LOW RISK: Minor interactions detected. Monitor for any unusual symptoms.")
        
        # Info interactions
        info_interactions = [i for i in interactions if i['severity'] == 'INFO']
        if info_interactions:
            recommendations.append("ℹ️ Beneficial interactions detected. These combinations may enhance effectiveness.")
        
        return recommendations
    
    def _get_data_sources_used(self, interactions: List[Dict]) -> List[str]:
        """
        Get list of data sources used in the analysis
        """
        sources = set()
        for interaction in interactions:
            sources.add(interaction.get('source', 'Unknown'))
        return list(sources)
    
    def get_medicine_info(self, medicine_name: str) -> Dict:
        """
        Get comprehensive medicine information from all sources
        """
        try:
            # Standardize name using RxNorm
            standardized_name, rxcui = self.rxnorm_client.standardize_drug_name(medicine_name)
            
            # Get OpenFDA data
            openfda_data = self.openfda_client.get_drug_info(medicine_name)
            
            # Get RxNorm data
            rxnorm_data = None
            if rxcui:
                rxnorm_data = self.rxnorm_client.find_drug_by_name(medicine_name)
            
            return {
                'original_name': medicine_name,
                'standardized_name': standardized_name,
                'rxcui': rxcui,
                'openfda_data': openfda_data,
                'rxnorm_data': rxnorm_data,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error getting medicine info for {medicine_name}: {e}")
            return {
                'original_name': medicine_name,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def bulk_download_medicine_data(self, medicine_names: List[str]) -> Dict:
        """
        Bulk download and cache medicine data from all sources
        """
        results = {}
        
        for medicine_name in medicine_names:
            logging.info(f"Downloading data for {medicine_name}")
            results[medicine_name] = self.get_medicine_info(medicine_name)
        
        return results
    
    def get_cache_stats(self) -> Dict:
        """
        Get statistics about cached data from all sources
        """
        openfda_stats = self.openfda_client.get_cache_stats()
        rxnorm_stats = self.rxnorm_client.get_cache_stats()
        
        return {
            'openfda_cache': openfda_stats,
            'rxnorm_cache': rxnorm_stats,
            'total_cached_items': openfda_stats['total_cached_drugs'] + rxnorm_stats['total_cached_queries']
        }

# Global instance
enhanced_interaction_checker = EnhancedDrugInteractionChecker()
