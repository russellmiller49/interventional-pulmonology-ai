import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
from datetime import datetime
import hashlib
from langextract import extract
from langextract.data import ExampleData, Document, Extraction
import PyPDF2
from dotenv import load_dotenv
from .schemas import *

load_dotenv()

class MedicalDocumentProcessor:
    """Process medical PDFs using LangExtract for structured extraction"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model_id = "gemini-2.5-pro"
        self.processed_docs = []
        self.extraction_log = []
        
    def create_medical_examples(self, doc_type: str) -> List[ExampleData]:
        """Create example data for LangExtract based on document type"""
        
        if doc_type == 'bronchoscopy':
            return [
                ExampleData(
                    text="Flexible bronchoscopy was performed showing normal right upper lobe bronchus. Endobronchial biopsy was obtained using forceps biopsy technique. No complications were observed.",
                    extractions=[
                        Extraction(
                            extraction_class="bronchoscopy_type",
                            extraction_text="flexible"
                        ),
                        Extraction(
                            extraction_class="anatomical_finding",
                            extraction_text="normal right upper lobe bronchus"
                        ),
                        Extraction(
                            extraction_class="biopsy_technique",
                            extraction_text="forceps biopsy"
                        ),
                        Extraction(
                            extraction_class="complications",
                            extraction_text="none"
                        )
                    ]
                )
            ]
        elif doc_type == 'pleural':
            return [
                ExampleData(
                    text="Thoracentesis was performed with ultrasound guidance. 1200ml of pleural fluid was removed. Analysis revealed exudative effusion with elevated LDH.",
                    extractions=[
                        Extraction(
                            extraction_class="procedure_type",
                            extraction_text="thoracentesis"
                        ),
                        Extraction(
                            extraction_class="guidance_method",
                            extraction_text="ultrasound"
                        ),
                        Extraction(
                            extraction_class="volume_removed",
                            extraction_text="1200ml"
                        ),
                        Extraction(
                            extraction_class="fluid_analysis",
                            extraction_text="exudative effusion with elevated LDH"
                        )
                    ]
                )
            ]
        elif doc_type == 'guideline':
            return [
                ExampleData(
                    text="Grade A recommendation: All patients with suspected lung cancer should undergo tissue sampling via bronchoscopy when feasible. Evidence level: High quality.",
                    extractions=[
                        Extraction(
                            extraction_class="recommendation_grade",
                            extraction_text="A"
                        ),
                        Extraction(
                            extraction_class="clinical_recommendation",
                            extraction_text="tissue sampling via bronchoscopy for suspected lung cancer"
                        ),
                        Extraction(
                            extraction_class="evidence_level",
                            extraction_text="high quality"
                        ),
                        Extraction(
                            extraction_class="patient_population",
                            extraction_text="suspected lung cancer"
                        )
                    ]
                )
            ]
        else:
            # Default examples for other types
            return [
                ExampleData(
                    text="The procedure involves insertion of a flexible bronchoscope through the oral route. Topical anesthesia is applied to the airways.",
                    extractions=[
                        Extraction(
                            extraction_class="procedure_name",
                            extraction_text="flexible bronchoscopy"
                        ),
                        Extraction(
                            extraction_class="access_route",
                            extraction_text="oral"
                        ),
                        Extraction(
                            extraction_class="anesthesia",
                            extraction_text="topical"
                        )
                    ]
                )
            ]
    
    def create_qa_examples(self, doc_type: str) -> List[ExampleData]:
        """Create Q&A example data for LangExtract"""
        return [
            ExampleData(
                text="Flexible bronchoscopy shows airway inflammation and narrowing. Biopsy samples were obtained for analysis.",
                extractions=[
                    Extraction(
                        extraction_class="question",
                        extraction_text="What procedure was performed?"
                    ),
                    Extraction(
                        extraction_class="answer",
                        extraction_text="Flexible bronchoscopy was performed to assess airway inflammation and narrowing, with biopsy samples obtained for analysis."
                    ),
                    Extraction(
                        extraction_class="question_type",
                        extraction_text="factual"
                    ),
                    Extraction(
                        extraction_class="difficulty_level",
                        extraction_text="basic"
                    ),
                    Extraction(
                        extraction_class="evidence_quality",
                        extraction_text="high"
                    ),
                    Extraction(
                        extraction_class="clinical_context",
                        extraction_text="diagnostic bronchoscopy"
                    )
                ]
            )
        ]
    
    def classify_document(self, text: str, filename: str) -> str:
        """Classify document type based on content"""
        text_lower = text.lower()
        filename_lower = filename.lower()
        
        # Classification rules
        if any(term in text_lower for term in ['bronchoscopy', 'bronchoscopic', 'endobronchial']):
            return 'bronchoscopy'
        elif any(term in text_lower for term in ['pleural', 'thoracentesis', 'chest tube']):
            return 'pleural'
        elif any(term in text_lower for term in ['guideline', 'recommendation', 'consensus']):
            return 'guideline'
        elif any(term in text_lower for term in ['emergency', 'urgent', 'critical']):
            return 'emergency'
        elif any(term in text_lower for term in ['randomized', 'trial', 'study', 'cohort']):
            return 'research'
        elif any(term in text_lower for term in ['procedure', 'technique', 'method']):
            return 'procedure'
        else:
            return 'general'
    
    def extract_from_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract structured information from a PDF"""
        try:
            # Read PDF content
            text = self.read_pdf(pdf_path)
            
            # Classify document
            doc_type = self.classify_document(text, pdf_path.name)
            
            # Extract based on document type
            extracted_data = self.extract_by_type(text, doc_type)
            
            # Add metadata
            extracted_data['metadata'] = {
                'source_file': pdf_path.name,
                'file_path': str(pdf_path),
                'document_type': doc_type,
                'extraction_date': datetime.now().isoformat(),
                'file_hash': self.calculate_file_hash(pdf_path),
                'extraction_model': 'gemini-2.5-pro',
                'char_count': len(text),
                'word_count': len(text.split())
            }
            
            # Extract general medical concepts
            concepts = self.extract_medical_concepts(text)
            extracted_data['medical_concepts'] = concepts
            
            # Generate Q&A pairs
            qa_pairs = self.generate_qa_pairs(text, doc_type)
            extracted_data['qa_pairs'] = qa_pairs
            
            # Log successful extraction
            self.extraction_log.append({
                'file': pdf_path.name,
                'status': 'success',
                'timestamp': datetime.now().isoformat()
            })
            
            return extracted_data
            
        except Exception as e:
            # Log error
            self.extraction_log.append({
                'file': pdf_path.name,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            return None
    
    def extract_by_type(self, text: str, doc_type: str) -> Dict[str, Any]:
        """Extract information based on document type"""
        
        extraction_configs = {
            'bronchoscopy': {
                'schema': BronchoscopyFindings,
                'instructions': """
                Extract detailed bronchoscopy information including:
                - Type of bronchoscopy (flexible, rigid, navigational, robotic)
                - Anatomical findings and variations
                - Pathological findings
                - Biopsy techniques (forceps, brush, needle, cryo)
                - Diagnostic yield percentages
                - Complications and their rates
                Focus on procedural details and clinical outcomes.
                """
            },
            'pleural': {
                'schema': PleuralProcedure,
                'instructions': """
                Extract pleural procedure information:
                - Procedure type (thoracentesis, chest tube, pleuroscopy)
                - Indications for procedure
                - Fluid analysis results
                - Drainage techniques
                - Pleurodesis methods and agents
                - Success rates and recurrence data
                """
            },
            'guideline': {
                'schema': ClinicalGuideline,
                'instructions': """
                Extract clinical guideline information:
                - Diagnostic criteria with specific thresholds
                - Treatment algorithms with decision points
                - Evidence grades (A, B, C, Expert Opinion)
                - Monitoring parameters with frequencies
                - Quality indicators and outcome measures
                """
            },
            'emergency': {
                'schema': EmergencyAirwayManagement,
                'instructions': """
                Extract emergency airway management information:
                - Clinical scenarios requiring intervention
                - Step-by-step management algorithms
                - Equipment and personnel requirements
                - Decision points for escalation
                - Complication management strategies
                """
            },
            'research': {
                'schema': ResearchStudy,
                'instructions': """
                Extract research study information:
                - Study design and methodology
                - Patient population characteristics
                - Intervention details
                - Statistical results with p-values
                - Clinical implications
                - Study limitations
                Focus on outcomes relevant to clinical practice.
                """
            },
            'procedure': {
                'schema': ProcedureInfo,
                'instructions': """
                Extract comprehensive procedural information:
                - Step-by-step technique descriptions
                - Equipment specifications and settings
                - Patient preparation requirements
                - Anatomical landmarks
                - Troubleshooting common problems
                - Post-procedure protocols
                Include specific measurements, doses, and timings where mentioned.
                """
            }
        }
        
        # Get appropriate schema and instructions
        config = extraction_configs.get(doc_type, extraction_configs['procedure'])
        
        # Create example data for extraction
        examples = self.create_medical_examples(doc_type)
        
        # Extract structured data using functional API
        extracted = extract(
            text_or_documents=text,
            prompt_description=config['instructions'],
            examples=examples,
            model_id=self.model_id,
            api_key=self.api_key
        )
        
        return {
            'document_type': doc_type,
            'extracted_data': extracted
        }
    
    def extract_medical_concepts(self, text: str, custom_focus: str = None) -> Dict[str, List[str]]:
        """Extract medical concepts for better searchability
        
        Args:
            text: Document text
            custom_focus: Optional focus area ('comprehensive', 'clinical_practice', 
                         'research_focused', 'guideline_focused', 'safety_focused')
        """
        
        if custom_focus:
            # Use custom extraction schema
            from .custom_schemas import get_custom_extraction_config
            config = get_custom_extraction_config(custom_focus)
            concepts = extract(
                text_or_documents=text,
                prompt_description=config['instructions'],
                examples=self.create_medical_examples('general'),
                model_id=self.model_id,
                api_key=self.api_key
            )
        else:
            # Use default extraction
            concepts = extract(
                text_or_documents=text,
                prompt_description="""
                Extract all medical concepts related to interventional pulmonology:
                - Focus on bronchoscopy, pleural procedures, airway management
                - Include specific equipment models and manufacturers
                - Extract medication names with dosages
                - Identify all diagnostic tests and imaging modalities
                - Note anatomical landmarks and variations
                Ensure all medical terminology is accurate and complete.
                """,
                examples=self.create_medical_examples('general'),
                model_id=self.model_id,
                api_key=self.api_key
            )
        
        return concepts
    
    def generate_qa_pairs(self, text: str, doc_type: str, max_length: int = 10000) -> List[Dict[str, str]]:
        """Generate Q&A pairs for chatbot training"""
        
        # Truncate text if too long to prevent timeouts
        if len(text) > max_length:
            text = text[:max_length] + "... [truncated]"
        
        class QAPair(TypedDict):
            question: str
            answer: str
            question_type: str  # factual, procedural, clinical-reasoning
            difficulty_level: str  # basic, intermediate, advanced
            evidence_quality: str  # high, moderate, low
            clinical_context: str
        
        qa_instructions = f"""
        Create clinical question-answer pairs for {doc_type} content.
        Generate questions that:
        1. Test procedural knowledge
        2. Address common clinical scenarios
        3. Cover complications and management
        4. Include differential diagnoses
        5. Address evidence-based practice
        
        Ensure answers are:
        - Accurate and evidence-based
        - Practical and actionable
        - Include specific details (doses, measurements, timings)
        - Reference guidelines where applicable
        
        Generate 3-5 high-quality Q&A pairs.
        """
        
        qa_pairs = extract(
            text_or_documents=text,
            prompt_description=qa_instructions,
            examples=self.create_qa_examples(doc_type),
            model_id=self.model_id,
            api_key=self.api_key
        )
        
        return qa_pairs
    
    def read_pdf(self, pdf_path: Path) -> str:
        """Read and extract text from PDF"""
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                # Add page markers for reference
                text += f"\n[Page {page_num + 1}]\n{page_text}"
        return text
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file for deduplication"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def process_directory(self, directory_path: Path, output_dir: Path) -> None:
        """Process all PDFs in a directory"""
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get all PDF files
        pdf_files = list(directory_path.glob("*.pdf"))
        print(f"Found {len(pdf_files)} PDF files to process")
        
        # Process each PDF
        for idx, pdf_file in enumerate(pdf_files, 1):
            print(f"Processing {idx}/{len(pdf_files)}: {pdf_file.name}")
            
            # Check if already processed
            output_file = output_dir / f"{pdf_file.stem}_extracted.json"
            if output_file.exists():
                print(f"  Already processed, skipping...")
                continue
            
            # Extract data
            extracted_data = self.extract_from_pdf(pdf_file)
            
            if extracted_data:
                # Save extracted data
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(extracted_data, f, indent=2, ensure_ascii=False)
                print(f"  [OK] Extracted and saved to {output_file.name}")
            else:
                print(f"  [FAILED] Extraction failed")
        
        # Save extraction log
        log_file = output_dir / "extraction_log.json"
        with open(log_file, 'w') as f:
            json.dump(self.extraction_log, f, indent=2)
        
        print(f"\nProcessing complete. Log saved to {log_file}")
    
    def validate_extraction(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and score extraction quality"""
        
        validation_results = {
            'is_valid': True,
            'completeness_score': 0,
            'missing_fields': [],
            'warnings': []
        }
        
        # Check for critical fields based on document type
        doc_type = extracted_data.get('document_type')
        extracted = extracted_data.get('extracted_data', {})
        
        critical_fields = {
            'procedure': ['procedure_name', 'indications', 'contraindications', 'technique_steps'],
            'bronchoscopy': ['bronchoscopy_type', 'pathological_findings', 'biopsy_techniques'],
            'guideline': ['condition', 'diagnostic_criteria', 'first_line_treatment'],
            'research': ['study_type', 'intervention', 'key_findings', 'conclusions']
        }
        
        # Check critical fields
        required = critical_fields.get(doc_type, [])
        for field in required:
            if field not in extracted or not extracted.get(field):
                validation_results['missing_fields'].append(field)
                validation_results['is_valid'] = False
        
        # Calculate completeness score
        total_fields = len(extracted.keys())
        filled_fields = sum(1 for v in extracted.values() if v)
        validation_results['completeness_score'] = (filled_fields / total_fields * 100) if total_fields > 0 else 0
        
        # Add warnings for low completeness
        if validation_results['completeness_score'] < 50:
            validation_results['warnings'].append("Less than 50% of fields extracted")
        
        return validation_results

# Utility function for batch processing
def batch_process_medical_documents():
    """Main function to process all medical documents"""
    
    processor = MedicalDocumentProcessor()
    
    # Define paths
    new_docs_path = Path(os.getenv('NEW_DOCS_PATH'))
    output_path = Path('./data/extracted_data')
    
    # Process documents
    processor.process_directory(new_docs_path, output_path)
    
    # Generate summary report
    generate_extraction_report(output_path)

def generate_extraction_report(output_dir: Path):
    """Generate a summary report of all extractions"""
    
    report = {
        'total_documents': 0,
        'successful_extractions': 0,
        'failed_extractions': 0,
        'document_types': {},
        'extraction_quality': [],
        'timestamp': datetime.now().isoformat()
    }
    
    # Analyze all extracted files
    for json_file in output_dir.glob("*_extracted.json"):
        report['total_documents'] += 1
        
        with open(json_file, 'r') as f:
            data = json.load(f)
            
        if data:
            report['successful_extractions'] += 1
            doc_type = data.get('document_type', 'unknown')
            report['document_types'][doc_type] = report['document_types'].get(doc_type, 0) + 1
            
            # Validate extraction
            processor = MedicalDocumentProcessor()
            validation = processor.validate_extraction(data)
            report['extraction_quality'].append({
                'file': json_file.name,
                'completeness': validation['completeness_score'],
                'is_valid': validation['is_valid']
            })
        else:
            report['failed_extractions'] += 1
    
    # Calculate average quality
    if report['extraction_quality']:
        avg_completeness = sum(item['completeness'] for item in report['extraction_quality']) / len(report['extraction_quality'])
        report['average_completeness'] = avg_completeness
    
    # Save report
    report_file = output_dir / "extraction_summary_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Report saved to {report_file}")
    return report

if __name__ == "__main__":
    batch_process_medical_documents()