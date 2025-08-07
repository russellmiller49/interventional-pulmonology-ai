from typing import TypedDict, List, Optional
from datetime import datetime

class ProcedureInfo(TypedDict):
    """Schema for interventional procedures"""
    procedure_name: str
    procedure_type: str  # diagnostic, therapeutic, emergency
    anatomical_location: str
    indications: List[str]
    contraindications: List[str]
    relative_contraindications: List[str]
    pre_procedure_preparation: List[str]
    equipment_needed: List[str]
    technique_steps: List[str]
    post_procedure_care: List[str]
    complications: List[str]
    success_rate: Optional[str]
    evidence_level: Optional[str]
    alternative_procedures: List[str]
    special_considerations: Optional[str]

class ClinicalGuideline(TypedDict):
    """Schema for clinical guidelines"""
    guideline_title: str
    condition: str
    diagnostic_criteria: List[str]
    severity_classification: Optional[str]
    first_line_treatment: str
    second_line_treatment: Optional[str]
    treatment_algorithm: List[str]
    monitoring_parameters: List[str]
    follow_up_schedule: str
    outcome_measures: List[str]
    quality_indicators: List[str]
    evidence_grade: str
    last_updated: Optional[str]

class BronchoscopyFindings(TypedDict):
    """Schema for bronchoscopy-specific information"""
    bronchoscopy_type: str  # flexible, rigid, navigational
    airway_anatomy: List[str]
    pathological_findings: List[str]
    biopsy_techniques: List[str]
    sample_types: List[str]
    diagnostic_yield: Optional[str]
    sedation_requirements: str
    ventilation_strategy: Optional[str]
    special_equipment: List[str]

class PleuralProcedure(TypedDict):
    """Schema for pleural procedures"""
    procedure_name: str
    pleural_pathology: str
    diagnostic_approach: List[str]
    therapeutic_interventions: List[str]
    drainage_type: Optional[str]
    pleurodesis_agents: List[str]
    imaging_guidance: str
    success_criteria: List[str]
    recurrence_rate: Optional[str]

class EmergencyAirwayManagement(TypedDict):
    """Schema for emergency airway procedures"""
    scenario: str
    urgency_level: str  # emergent, urgent, semi-urgent
    primary_technique: str
    backup_techniques: List[str]
    required_personnel: List[str]
    essential_equipment: List[str]
    decision_points: List[str]
    complications_to_anticipate: List[str]
    post_procedure_monitoring: List[str]

class ResearchStudy(TypedDict):
    """Schema for research articles"""
    study_title: str
    study_type: str  # RCT, cohort, case-control, etc.
    population_size: Optional[int]
    inclusion_criteria: List[str]
    exclusion_criteria: List[str]
    intervention: str
    comparator: Optional[str]
    primary_outcomes: List[str]
    secondary_outcomes: List[str]
    key_findings: List[str]
    statistical_significance: Optional[str]
    clinical_significance: str
    limitations: List[str]
    conclusions: str
    implications_for_practice: List[str]

class MedicalConcepts(TypedDict):
    """Schema for general medical concept extraction"""
    anatomical_sites: List[str]
    procedures: List[str]
    diagnoses: List[str]
    symptoms: List[str]
    medications: List[str]
    equipment: List[str]
    laboratory_tests: List[str]
    imaging_modalities: List[str]
    clinical_findings: List[str]
    risk_factors: List[str]