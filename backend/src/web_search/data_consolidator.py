from typing import Dict, List, Any

class DataConsolidator:
    def __init__(self):
        self.confidence_weights = {
            'linkedin.com': 0.9,
            'crunchbase.com': 0.95,
            'forbes.com': 0.8,
            'bloomberg.com': 0.85,
            'techcrunch.com': 0.7,
            'company_website': 0.9
        }
    
    def consolidate_person_data(self, analyzed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Consolidate and deduplicate person information"""
        
        consolidated = {
            'people': [],
            'company_info': {},
            'data_quality': {
                'sources_used': [],
                'confidence_score': 0.0,
                'last_updated': None
            }
        }
        
        # Process person data
        people_data = analyzed_data.get('person_and_roles', [])
        for person in people_data:
            consolidated_person = self._consolidate_person_info(person)
            consolidated['people'].append(consolidated_person)
        
        # Calculate overall confidence score
        consolidated['data_quality']['confidence_score'] = self._calculate_confidence(analyzed_data)
        
        return consolidated
    
    def _consolidate_person_info(self, person_data: Dict) -> Dict:
        """Consolidate information for a single person"""
        return {
            'name': person_data.get('name', ''),
            'current_role': person_data.get('current_role', ''),
            'education': self._consolidate_education(person_data.get('education', [])),
            'experience': self._consolidate_experience(person_data.get('experience', [])),
            'entrepreneurial_background': person_data.get('entrepreneurial_background', []),
            'achievements': person_data.get('achievements', []),
            'skills': person_data.get('skills', [])
        }
    
    def _consolidate_education(self, education_list: List[Dict]) -> List[Dict]:
        """Deduplicate and consolidate education information"""
        consolidated = []
        seen_institutions = set()
        
        for edu in education_list:
            institution = edu.get('institution', '').lower()
            if institution and institution not in seen_institutions:
                consolidated.append(edu)
                seen_institutions.add(institution)
        
        return consolidated
    
    def _consolidate_experience(self, experience_list: List[Dict]) -> List[Dict]:
        """Deduplicate and consolidate work experience"""
        consolidated = []
        seen_companies = set()
        
        for exp in experience_list:
            company = exp.get('company', '').lower()
            if company and company not in seen_companies:
                consolidated.append(exp)
                seen_companies.add(company)
        
        return consolidated
    
    def _calculate_confidence(self, data: Dict) -> float:
        """Calculate confidence score based on source quality"""
        return 0.75  # Placeholder
