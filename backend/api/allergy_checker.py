"""
Allergy Checker Module
=====================

This module provides functionality to check for potential allergic reactions
between prescribed medicines and user's known allergies.

Features:
- Check medicine allergies against user's allergy list
- Identify cross-reactivity between similar substances
- Provide detailed allergy warnings and recommendations
- Support both authenticated and anonymous allergy checking
"""

import logging
import re
from typing import List, Dict, Any, Optional
from django.contrib.auth.models import User
from .models import UserProfile

logger = logging.getLogger(__name__)

class AllergyChecker:
    """Handles allergy checking for medicines and user profiles"""
    
    # Common allergy cross-reactivity groups
    ALLERGY_GROUPS = {
        'penicillin_group': [
            'penicillin', 'amoxicillin', 'ampicillin', 'cloxacillin', 
            'dicloxacillin', 'flucloxacillin', 'piperacillin', 'ticarcillin'
        ],
        'sulfa_group': [
            'sulfamethoxazole', 'sulfasalazine', 'sulfadiazine', 
            'sulfisoxazole', 'sulfacetamide', 'sulfadoxine'
        ],
        'nsaid_group': [
            'aspirin', 'ibuprofen', 'naproxen', 'diclofenac', 'indomethacin',
            'ketorolac', 'meloxicam', 'celecoxib', 'rofecoxib'
        ],
        'opioid_group': [
            'morphine', 'codeine', 'hydrocodone', 'oxycodone', 'fentanyl',
            'tramadol', 'meperidine', 'hydromorphone'
        ],
        'ace_inhibitor_group': [
            'captopril', 'enalapril', 'lisinopril', 'ramipril', 'quinapril',
            'benazepril', 'fosinopril', 'moexipril', 'trandolapril'
        ]
    }
    
    def __init__(self):
        self.logger = logger
    
    def check_medicine_allergies(self, medicine_name: str, user_allergies: List[str]) -> Dict[str, Any]:
        """
        Check if a medicine has potential allergic reactions with user's allergies
        
        Args:
            medicine_name: Name of the prescribed medicine
            user_allergies: List of user's known allergies
            
        Returns:
            Dict containing allergy check results
        """
        medicine_lower = medicine_name.lower()
        user_allergies_lower = [allergy.lower() for allergy in user_allergies]
        
        # Direct allergy matches
        direct_matches = []
        for allergy in user_allergies_lower:
            if allergy in medicine_lower or medicine_lower in allergy:
                direct_matches.append(allergy)
        
        # Cross-reactivity group checks
        cross_reactions = []
        for group_name, group_medicines in self.ALLERGY_GROUPS.items():
            # Check if user is allergic to any medicine in this group
            user_allergic_to_group = any(
                any(allergy in med or med in allergy for allergy in user_allergies_lower)
                for med in group_medicines
            )
            
            # Check if prescribed medicine is in the same group
            if user_allergic_to_group and any(med in medicine_lower for med in group_medicines):
                cross_reactions.append({
                    'group': group_name,
                    'reason': f'Cross-reactivity with {group_name.replace("_", " ")}',
                    'medicines_in_group': group_medicines
                })
        
        # Determine risk level
        risk_level = 'low'
        if direct_matches:
            risk_level = 'high'
        elif cross_reactions:
            risk_level = 'medium'
        
        return {
            'has_allergy_risk': len(direct_matches) > 0 or len(cross_reactions) > 0,
            'risk_level': risk_level,
            'direct_matches': direct_matches,
            'cross_reactions': cross_reactions,
            'recommendations': self._get_allergy_recommendations(risk_level, direct_matches, cross_reactions),
            'medicine_checked': medicine_name,
            'user_allergies_checked': user_allergies
        }
    
    def _get_allergy_recommendations(self, risk_level: str, direct_matches: List[str], cross_reactions: List[Dict]) -> List[str]:
        """Generate recommendations based on allergy risk"""
        recommendations = []
        
        if risk_level == 'high':
            recommendations.extend([
                "⚠️ HIGH RISK: Direct allergy match detected",
                "❌ DO NOT take this medication",
                "🩺 Consult your doctor immediately",
                "📋 Inform healthcare provider of this allergy"
            ])
        elif risk_level == 'medium':
            recommendations.extend([
                "⚠️ MEDIUM RISK: Potential cross-reactivity detected",
                "🔍 Consult your doctor before taking",
                "🧪 Consider allergy testing",
                "📝 Monitor for allergic reactions if prescribed"
            ])
        else:
            recommendations.append("✅ No known allergy risks detected")
        
        return recommendations
    
    def get_user_allergies(self, user: Optional[User] = None, allergies_list: Optional[List[str]] = None) -> List[str]:
        """
        Get user's allergies from database or provided list
        
        Args:
            user: Django User object (optional)
            allergies_list: Direct list of allergies (optional)
            
        Returns:
            List of user's allergies
        """
        if allergies_list:
            return allergies_list
        
        if user:
            try:
                profile = UserProfile.objects.get(user=user)
                return profile.allergies if profile.allergies else []
            except UserProfile.DoesNotExist:
                self.logger.warning(f"User profile not found for user: {user.username}")
                return []
        
        return []
    
    def check_prescription_allergies(self, medicines: List[Dict[str, Any]], 
                                   user: Optional[User] = None, 
                                   allergies_list: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Check all medicines in a prescription for allergy risks
        
        Args:
            medicines: List of medicine dictionaries
            user: Django User object (optional)
            allergies_list: Direct list of allergies (optional)
            
        Returns:
            Comprehensive allergy check results
        """
        user_allergies = self.get_user_allergies(user, allergies_list)
        
        if not user_allergies:
            return {
                'has_allergy_risk': False,
                'overall_risk_level': 'low',
                'medicine_checks': [],
                'summary': 'No user allergies provided for checking',
                'user_allergies': []
            }
        
        medicine_checks = []
        overall_risk_level = 'low'
        
        for medicine in medicines:
            medicine_name = medicine.get('name', '')
            if medicine_name:
                check_result = self.check_medicine_allergies(medicine_name, user_allergies)
                medicine_checks.append(check_result)
                
                # Update overall risk level
                if check_result['risk_level'] == 'high':
                    overall_risk_level = 'high'
                elif check_result['risk_level'] == 'medium' and overall_risk_level != 'high':
                    overall_risk_level = 'medium'
        
        has_any_risk = any(check['has_allergy_risk'] for check in medicine_checks)
        
        return {
            'has_allergy_risk': has_any_risk,
            'overall_risk_level': overall_risk_level,
            'medicine_checks': medicine_checks,
            'summary': self._generate_allergy_summary(medicine_checks, overall_risk_level),
            'user_allergies': user_allergies
        }
    
    def _generate_allergy_summary(self, medicine_checks: List[Dict], risk_level: str) -> str:
        """Generate a summary of allergy checking results"""
        high_risk_count = sum(1 for check in medicine_checks if check['risk_level'] == 'high')
        medium_risk_count = sum(1 for check in medicine_checks if check['risk_level'] == 'medium')
        
        if high_risk_count > 0:
            return f"⚠️ {high_risk_count} medicine(s) have HIGH allergy risk - DO NOT TAKE"
        elif medium_risk_count > 0:
            return f"🔍 {medium_risk_count} medicine(s) have MEDIUM allergy risk - Consult doctor"
        else:
            return "✅ No allergy risks detected in this prescription"

# Global instance
allergy_checker = AllergyChecker()
