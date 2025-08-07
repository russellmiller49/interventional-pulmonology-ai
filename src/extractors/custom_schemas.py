from typing import TypedDict, List, Optional, Dict

# --- XML-level Article Metadata ---

class ArticleInfo(TypedDict, total=False):
    article_id: str
    title: str
    authors: List[str]
    article_type: str               # e.g. "Review", "Original Study", etc.
    journal_citation: str
    publication_year: int
    keywords: List[str]

class AbstractSections(TypedDict, total=False):
    summary: str
    take_home: str

class PICOData(TypedDict, total=False):
    population: str
    intervention: str
    comparison: str
    outcome: str

# --- Study & Clinical Entities ---

class StudyMetadata(TypedDict, total=False):
    study_design: str               # e.g. "prospective", "RCT"
    sample_size: int
    country: List[str]
    lesion_location: List[str]
    procedure_type: str             # e.g. "RAB", "EBUS-TBNA"
    registration_id: Optional[str]

class OutcomeMetrics(TypedDict, total=False):
    diagnostic_yield_pct: Optional[float]
    overall_success_rate_pct: Optional[float]
    complication_name: List[str]
    complication_rate_pct: List[float]
    overall_complication_rate_pct: Optional[float]
    biopsy_yield_pct: Optional[float]

class ResearchGapData(TypedDict, total=False):
    limitations: List[str]
    future_research: List[str]
    unanswered_questions: List[str]

class ProcedureTechnique(TypedDict, total=False):
    instrument_names: List[str]
    energy_source: Optional[str]
    debulking_method: Optional[str]

# --- Standard Medical Extraction Fields ---

class CustomMedicalEntities(TypedDict, total=False):
    # XML-level
    article_info: ArticleInfo
    abstract: AbstractSections
    pico: PICOData

    # Study-level
    study_meta: StudyMetadata
    outcomes: OutcomeMetrics
    research_gaps: ResearchGapData
    technique_details: ProcedureTechnique

    # Additional fields for drugs, procedures, complications
    drug_names: List[str]
    drug_dosages: List[str]
    drug_interactions: List[str]
    administration_routes: List[str]
    procedure_duration: Optional[str]
    anesthesia_type: Optional[str]
    patient_positioning: Optional[str]
    success_rates: List[str]
    immediate_complications: List[str]
    delayed_complications: List[str]
    complication_rates: Dict[str, str]
    management_strategies: List[str]
    inclusion_criteria: List[str]
    exclusion_criteria: List[str]
    risk_stratification: List[str]
    primary_endpoints: List[str]
    secondary_endpoints: List[str]
    quality_of_life_measures: List[str]
    mortality_data: Optional[str]
    recommendation_grade: Optional[str]
    evidence_level: Optional[str]
    society_guidelines: List[str]
    bronchoscope_type: Optional[str]
    sedation_protocol: Optional[str]
    ventilation_strategy: Optional[str]
    biopsy_yield: Optional[str]
    number_of_passes: Optional[str]
    specimen_adequacy: Optional[str]

# --- Extraction instructions (as before) ---

EXTRACTION_INSTRUCTIONS = {
    'comprehensive': """
Extract ALL medical information including:
- Every medication with doses
- All procedures & techniques
- Full complications with rates
- Complete patient selection criteria
- Detailed outcomes and endpoints
Be exhaustive.
""",
    'clinical_practice': """
Focus on clinically actionable info:
- Step-by-step procedural techniques
- Drug doses & administration
- Complication management
- Patient selection criteria
- Practical tips & pearls
Also capture debulking technique (instrument, energy).
""",
    'research_focused': """
Extract research methods & results:
- Study design & methods
- Statistical analyses
- Primary & secondary outcomes
- P-values and confidence intervals
- Limitations, biases, future research suggestions
""",
    'guideline_focused': """
Extract guideline recommendations:
- Recommendation text & grade
- Evidence levels
- Diagnostic algorithms & pathways
Focus on actionable clinical guidance.
""",
    'safety_focused': """
Extract safety info:
- Contraindications
- Drug interactions
- Complications with rates
- Risk factors
- Safety monitoring & emergency protocols
Prioritize patient safety.
"""
}

def get_custom_extraction_config(focus: str = 'comprehensive'):
    return {
        'schema': CustomMedicalEntities,
        'instructions': EXTRACTION_INSTRUCTIONS.get(focus, EXTRACTION_INSTRUCTIONS['comprehensive'])
    }
