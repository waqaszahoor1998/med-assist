"""
============================================================================
UNIFIED DRUG INTERACTION CHECKER - Comprehensive Safety Validation
============================================================================

This file combines both basic and enhanced drug interaction checkers into
one comprehensive system that runs automatically during prescription analysis.

Strategy:
1. Run Basic Checker first (fast, reliable, offline)
2. Run Enhanced Checker second (comprehensive, online APIs)
3. Merge and prioritize results
4. Return unified safety report

Benefits:
- Maximum safety coverage (both local + online data)
- Fast initial response (basic checker)
- Comprehensive validation (enhanced checker)
- No user choice needed - runs automatically
- Best of both worlds

Used by:
- api/views.py: analyze_prescription() - Main prescription analysis
- api/views.py: analyze_prescription_enhanced() - Enhanced analysis
- Frontend: Automatic safety checking

Performance:
- Basic checker: ~50ms (local database)
- Enhanced checker: ~500ms-2s (API calls)
- Total time: ~550ms-2s (acceptable for safety)
- Caching reduces repeated API calls

Data Sources Combined:
1. Local Database (DrugBank) - Basic checker
2. OpenFDA API - Enhanced checker
3. RxNorm API - Enhanced checker
4. Manual validation - Both checkers

Result Priority:
1. HIGH severity from any source
2. MEDIUM severity from any source
3. LOW severity from any source
4. INFO from any source
5. Source agreement increases confidence
============================================================================
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
from .drug_interactions import interaction_checker as basic_checker
from .enhanced_drug_interactions import enhanced_interaction_checker

class UnifiedDrugInteractionChecker:
    """
    Unified drug interaction checker that combines basic and enhanced systems.
    
    Runs both checkers automatically and merges results for maximum safety.
    No user choice needed - provides comprehensive validation.
    
    Main Methods:
    - check_interactions() - Run both checkers and merge results
    - _merge_results() - Combine results from both systems
    - _prioritize_interactions() - Sort by severity and source agreement
    - _generate_unified_recommendations() - Create comprehensive recommendations
    """
    
    def __init__(self):
        self.basic_checker = basic_checker
        self.enhanced_checker = enhanced_interaction_checker
        self.severity_levels = {
            'HIGH': {'color': '#FF4444', 'icon': '⚠️', 'priority': 3},
            'MEDIUM': {'color': '#FF8800', 'icon': '⚡', 'priority': 2},
            'LOW': {'color': '#FFAA00', 'icon': '💡', 'priority': 1},
            'INFO': {'color': '#4488FF', 'icon': 'ℹ️', 'priority': 0},
            'UNKNOWN': {'color': '#888888', 'icon': '❓', 'priority': 0}
        }
    
    def check_interactions(self, medicines: List[str]) -> Dict:
        """
        Check for drug interactions using both basic and enhanced systems.
        
        This is the main method that runs both checkers automatically.
        No user choice needed - provides maximum safety coverage.
        
        Args:
            medicines: List of medicine names to check
            
        Returns:
            Unified interaction results from both systems
        """
        try:
            logging.info(f"Starting unified drug interaction check for {len(medicines)} medicines")
            
            # Step 1: Run basic checker first (fast, reliable)
            basic_results = self._run_basic_checker(medicines)
            
            # Step 2: Run enhanced checker (comprehensive, slower)
            enhanced_results = self._run_enhanced_checker(medicines)
            
            # Step 3: Merge results from both systems
            unified_results = self._merge_results(basic_results, enhanced_results)
            
            # Step 4: Prioritize and sort interactions
            unified_results = self._prioritize_interactions(unified_results)
            
            # Step 5: Generate unified recommendations
            unified_results['recommendations'] = self._generate_unified_recommendations(unified_results)
            
            # Step 6: Add metadata
            unified_results.update({
                'checker_used': 'Unified (Basic + Enhanced)',
                'basic_checker_status': basic_results.get('status', 'unknown'),
                'enhanced_checker_status': enhanced_results.get('status', 'unknown'),
                'total_sources': len(set([i.get('source', 'Unknown') for i in unified_results.get('interactions', [])])),
                'timestamp': datetime.now().isoformat()
            })
            
            logging.info(f"Unified check completed: {unified_results['interactions_found']} interactions found")
            return unified_results
            
        except Exception as e:
            logging.error(f"Error in unified drug interaction checking: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'interactions_found': [],
                'severity_summary': {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0, 'UNKNOWN': 0},
                'overall_risk_level': 'UNKNOWN',
                'recommendations': ['Error occurred during interaction checking. Please try again.'],
                'checker_used': 'Unified (Error)',
                'timestamp': datetime.now().isoformat()
            }
    
    def _run_basic_checker(self, medicines: List[str]) -> Dict:
        """
        Run basic drug interaction checker (fast, local database)
        """
        try:
            logging.info("Running basic drug interaction checker")
            results = self.basic_checker.check_interactions(medicines)
            
            # Add source information to each interaction
            if results.get('interactions'):
                for interaction in results['interactions']:
                    interaction['source'] = 'Local Database (DrugBank)'
                    interaction['checker_type'] = 'Basic'
            
            logging.info(f"Basic checker found {len(results.get('interactions', []))} interactions")
            return results
            
        except Exception as e:
            logging.error(f"Basic checker failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'interactions': [],
                'severity_summary': {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0}
            }
    
    def _run_enhanced_checker(self, medicines: List[str]) -> Dict:
        """
        Run enhanced drug interaction checker (comprehensive, online APIs)
        """
        try:
            logging.info("Running enhanced drug interaction checker")
            results = self.enhanced_checker.check_interactions(medicines)
            
            # Add checker type information
            if results.get('interactions'):
                for interaction in results['interactions']:
                    interaction['checker_type'] = 'Enhanced'
            
            logging.info(f"Enhanced checker found {len(results.get('interactions', []))} interactions")
            return results
            
        except Exception as e:
            logging.error(f"Enhanced checker failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'interactions': [],
                'severity_summary': {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0, 'UNKNOWN': 0}
            }
    
    def _merge_results(self, basic_results: Dict, enhanced_results: Dict) -> Dict:
        """
        Merge results from both checkers into unified format
        """
        try:
            # Start with basic results as foundation
            unified = {
                'status': 'success',
                'total_medicines': basic_results.get('total_medicines', 0),
                'interactions': [],
                'severity_summary': {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0, 'UNKNOWN': 0},
                'overall_risk_level': 'NONE',
                'data_sources': set(),
                'checker_agreement': {}
            }
            
            # Add basic interactions
            basic_interactions = basic_results.get('interactions', [])
            for interaction in basic_interactions:
                unified['interactions'].append(interaction)
                unified['data_sources'].add(interaction.get('source', 'Unknown'))
            
            # Add enhanced interactions (avoid duplicates)
            enhanced_interactions = enhanced_results.get('interactions', [])
            for interaction in enhanced_interactions:
                if not self._interaction_exists(unified['interactions'], interaction):
                    unified['interactions'].append(interaction)
                    unified['data_sources'].add(interaction.get('source', 'Unknown'))
                else:
                    # Update existing interaction with enhanced data
                    self._update_existing_interaction(unified['interactions'], interaction)
            
            # Calculate unified severity summary
            for interaction in unified['interactions']:
                severity = interaction.get('severity', 'UNKNOWN')
                if severity in unified['severity_summary']:
                    unified['severity_summary'][severity] += 1
            
            # Calculate overall risk level
            unified['overall_risk_level'] = self._calculate_overall_risk(unified['severity_summary'])
            
            # Count interactions found
            unified['interactions_found'] = len(unified['interactions'])
            
            # Convert data_sources set to list
            unified['data_sources'] = list(unified['data_sources'])
            
            # Calculate checker agreement
            unified['checker_agreement'] = self._calculate_checker_agreement(basic_interactions, enhanced_interactions)
            
            return unified
            
        except Exception as e:
            logging.error(f"Error merging results: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'interactions': [],
                'severity_summary': {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0, 'UNKNOWN': 0},
                'overall_risk_level': 'UNKNOWN'
            }
    
    def _interaction_exists(self, existing_interactions: List[Dict], new_interaction: Dict) -> bool:
        """
        Check if an interaction already exists in the list
        """
        for existing in existing_interactions:
            if self._interactions_match(existing, new_interaction):
                return True
        return False
    
    def _interactions_match(self, interaction1: Dict, interaction2: Dict) -> bool:
        """
        Check if two interactions are the same (same drug pair)
        """
        # Get drug names from both interactions
        drugs1 = self._extract_drug_names(interaction1)
        drugs2 = self._extract_drug_names(interaction2)
        
        # Check if they have the same drug pair
        return set(drugs1) == set(drugs2)
    
    def _extract_drug_names(self, interaction: Dict) -> List[str]:
        """
        Extract drug names from an interaction
        """
        drugs = []
        if 'drug1' in interaction:
            drugs.append(interaction['drug1'].lower())
        if 'drug2' in interaction:
            drugs.append(interaction['drug2'].lower())
        if 'medicine1' in interaction:
            drugs.append(interaction['medicine1'].lower())
        if 'medicine2' in interaction:
            drugs.append(interaction['medicine2'].lower())
        return drugs
    
    def _update_existing_interaction(self, interactions: List[Dict], enhanced_interaction: Dict):
        """
        Update existing interaction with enhanced data
        """
        for i, existing in enumerate(interactions):
            if self._interactions_match(existing, enhanced_interaction):
                # Merge enhanced data into existing interaction (avoid circular references)
                enhanced_summary = {
                    'severity': enhanced_interaction.get('severity', 'UNKNOWN'),
                    'description': enhanced_interaction.get('description', ''),
                    'interaction_type': enhanced_interaction.get('interaction_type', ''),
                    'source': enhanced_interaction.get('source', 'Unknown')
                }
                interactions[i].update({
                    'enhanced_data': enhanced_summary,
                    'sources': [existing.get('source', 'Unknown'), enhanced_interaction.get('source', 'Unknown')],
                    'confidence_boost': True
                })
                break
    
    def _calculate_checker_agreement(self, basic_interactions: List[Dict], enhanced_interactions: List[Dict]) -> Dict:
        """
        Calculate agreement between basic and enhanced checkers
        """
        basic_count = len(basic_interactions)
        enhanced_count = len(enhanced_interactions)
        
        # Find overlapping interactions
        overlapping = 0
        for basic_interaction in basic_interactions:
            for enhanced_interaction in enhanced_interactions:
                if self._interactions_match(basic_interaction, enhanced_interaction):
                    overlapping += 1
                    break
        
        total_unique = basic_count + enhanced_count - overlapping
        
        return {
            'basic_interactions': basic_count,
            'enhanced_interactions': enhanced_count,
            'overlapping_interactions': overlapping,
            'total_unique_interactions': total_unique,
            'agreement_percentage': (overlapping / max(basic_count, enhanced_count, 1)) * 100
        }
    
    def _prioritize_interactions(self, results: Dict) -> Dict:
        """
        Sort interactions by severity and source agreement
        """
        interactions = results.get('interactions', [])
        
        # Sort by severity first (HIGH to LOW)
        interactions.sort(key=lambda x: self.severity_levels.get(x.get('severity', 'UNKNOWN'), {}).get('priority', 0), reverse=True)
        
        # Then by source agreement (more sources = higher priority)
        interactions.sort(key=lambda x: len(x.get('sources', [x.get('source', 'Unknown')])), reverse=True)
        
        results['interactions'] = interactions
        return results
    
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
    
    def _generate_unified_recommendations(self, results: Dict) -> List[str]:
        """
        Generate comprehensive recommendations based on unified results
        """
        recommendations = []
        interactions = results.get('interactions', [])
        checker_agreement = results.get('checker_agreement', {})
        
        if not interactions:
            recommendations.append("✅ No known drug interactions found. Continue current medication regimen.")
            return recommendations
        
        # Add source information
        data_sources = results.get('data_sources', [])
        if data_sources:
            source_info = ", ".join(data_sources)
            recommendations.append(f"📊 Data sources: {source_info}")
        
        # Add checker agreement information
        if checker_agreement.get('agreement_percentage', 0) > 50:
            recommendations.append(f"✅ High agreement between checkers ({checker_agreement['agreement_percentage']:.1f}%)")
        elif checker_agreement.get('agreement_percentage', 0) > 25:
            recommendations.append(f"⚠️ Moderate agreement between checkers ({checker_agreement['agreement_percentage']:.1f}%)")
        else:
            recommendations.append(f"ℹ️ Low agreement between checkers ({checker_agreement['agreement_percentage']:.1f}%) - Multiple sources provide different information")
        
        # Severity-based recommendations
        high_interactions = [i for i in interactions if i['severity'] == 'HIGH']
        if high_interactions:
            recommendations.append("🚨 HIGH RISK: Consult healthcare provider immediately before taking these medications together.")
            recommendations.append("⚠️ Consider alternative medications or adjusted dosing schedules.")
        
        medium_interactions = [i for i in interactions if i['severity'] == 'MEDIUM']
        if medium_interactions:
            recommendations.append("⚡ MEDIUM RISK: Monitor closely for adverse effects. Consider dose adjustments.")
            recommendations.append("📊 Regular monitoring may be required.")
        
        low_interactions = [i for i in interactions if i['severity'] == 'LOW']
        if low_interactions:
            recommendations.append("💡 LOW RISK: Minor interactions detected. Monitor for any unusual symptoms.")
        
        info_interactions = [i for i in interactions if i['severity'] == 'INFO']
        if info_interactions:
            recommendations.append("ℹ️ Beneficial interactions detected. These combinations may enhance effectiveness.")
        
        # Add specific interaction details
        if len(interactions) <= 3:
            for interaction in interactions:
                recommendations.append(f"🔍 {interaction.get('interaction_type', 'Interaction')}: {interaction.get('description', 'See details above')}")
        
        return recommendations
    
    def get_medicine_safety_profile(self, medicine_name: str) -> Dict:
        """
        Get comprehensive safety profile for a single medicine
        """
        try:
            # Get basic safety info
            basic_interactions = self.basic_checker.get_medicine_interactions(medicine_name)
            
            # Get enhanced safety info
            enhanced_info = self.enhanced_checker.get_medicine_info(medicine_name)
            
            return {
                'medicine_name': medicine_name,
                'basic_interactions': basic_interactions,
                'enhanced_info': enhanced_info,
                'safety_score': self._calculate_safety_score(basic_interactions, enhanced_info),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error getting safety profile for {medicine_name}: {e}")
            return {
                'medicine_name': medicine_name,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _calculate_safety_score(self, basic_interactions: List[Dict], enhanced_info: Dict) -> float:
        """
        Calculate safety score for a medicine (0-100, higher is safer)
        """
        try:
            score = 100.0
            
            # Deduct points for basic interactions
            for interaction in basic_interactions:
                severity = interaction.get('severity', 'LOW')
                if severity == 'HIGH':
                    score -= 30
                elif severity == 'MEDIUM':
                    score -= 15
                elif severity == 'LOW':
                    score -= 5
            
            # Deduct points for enhanced interactions
            if enhanced_info.get('openfda_data', {}).get('warnings'):
                score -= 10
            
            return max(0.0, min(100.0, score))
            
        except Exception:
            return 50.0  # Default neutral score

# Global instance
unified_interaction_checker = UnifiedDrugInteractionChecker()
