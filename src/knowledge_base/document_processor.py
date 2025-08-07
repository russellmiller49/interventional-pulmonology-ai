import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib
from ..extractors.langextract_processor import MedicalDocumentProcessor
from .vector_store import MedicalKnowledgeBase
from .xml_processor import XMLMetadataProcessor

class DocumentProcessor:
    """Process existing text and JSON files from Adobe Extract"""
    
    def __init__(self, enable_qa_generation: bool = True):
        self.medical_processor = MedicalDocumentProcessor()
        self.knowledge_base = MedicalKnowledgeBase()
        self.processed_files = set()
        self.xml_processor = XMLMetadataProcessor()
        self.enable_qa_generation = enable_qa_generation
        
        # Load XML metadata if available
        xml_path = Path("data/Combined.xml")
        if xml_path.exists():
            print("Loading XML metadata...")
            self.xml_processor.load_xml_metadata(xml_path)
        else:
            print("No XML metadata file found at data/Combined.xml")
    
    def process_adobe_extract_files(self, directory_path: Path) -> Dict[str, Any]:
        """Process text and JSON files from Adobe Extract"""
        
        results = {
            'total_files': 0,
            'processed': 0,
            'failed': 0,
            'files': []
        }
        
        # Create processed_chunks directory
        processed_chunks_dir = Path('./data/processed_chunks')
        processed_chunks_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all JSON files from Adobe Extract
        json_files = list(directory_path.glob("*.json"))
        txt_files = list(directory_path.glob("*.txt"))
        
        print(f"Found {len(json_files)} JSON files and {len(txt_files)} text files")
        
        # Process JSON files (they likely contain structured data)
        for json_file in json_files:
            try:
                # Check for corresponding text file
                txt_file = json_file.with_suffix('.txt')
                
                if txt_file.exists():
                    print(f"Processing {json_file.stem}...")
                    
                    # Read text content
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        text_content = f.read()
                    
                    # Read JSON metadata
                    with open(json_file, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                    
                    # Process with LangExtract
                    extracted = self.process_with_langextract(
                        text_content, 
                        json_file.stem,
                        json_data
                    )
                    
                    if extracted:
                        # Enhance with XML metadata
                        extracted = self.xml_processor.enhance_document_processing(extracted, json_file.stem)
                        
                        # Save to processed_chunks folder
                        self.save_to_processed_chunks(extracted, json_file.stem, processed_chunks_dir)
                        
                        results['processed'] += 1
                        results['files'].append(json_file.name)
                        safe_stem = json_file.stem.encode('ascii', 'replace').decode('ascii')
                        print(f"  [OK] Processed {safe_stem}")
                    else:
                        results['failed'] += 1
                        print(f"  ✗ Failed to process {json_file.stem}")
                else:
                    # Process JSON only
                    print(f"Processing JSON only: {json_file.stem}")
                    extracted = self.process_json_only(json_file)
                    if extracted:
                        # Enhance with XML metadata
                        extracted = self.xml_processor.enhance_document_processing(extracted, json_file.stem)
                        
                        # Save to processed_chunks folder
                        self.save_to_processed_chunks(extracted, json_file.stem, processed_chunks_dir)
                        
                        results['processed'] += 1
                        safe_stem = json_file.stem.encode('ascii', 'replace').decode('ascii')
                        print(f"  [OK] Processed {safe_stem}")
                
                results['total_files'] += 1
                
            except Exception as e:
                print(f"Error processing {json_file.name}: {e}")
                # Add debugging info
                import traceback
                print("Full traceback:")
                traceback.print_exc()
                results['failed'] += 1
        
        # Process standalone text files (without JSON)
        for txt_file in txt_files:
            json_file = txt_file.with_suffix('.json')
            if not json_file.exists():  # Only process if no corresponding JSON
                try:
                    print(f"Processing text file: {txt_file.stem}")
                    
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        text_content = f.read()
                    
                    extracted = self.process_with_langextract(
                        text_content, 
                        txt_file.stem,
                        {}
                    )
                    
                    if extracted:
                        # Enhance with XML metadata
                        extracted = self.xml_processor.enhance_document_processing(extracted, txt_file.stem)
                        
                        # Save to processed_chunks folder
                        self.save_to_processed_chunks(extracted, txt_file.stem, processed_chunks_dir)
                        
                        results['processed'] += 1
                        results['files'].append(txt_file.name)
                        safe_stem = txt_file.stem.encode('ascii', 'replace').decode('ascii')
                        print(f"  [OK] Processed {safe_stem}")
                    
                    results['total_files'] += 1
                    
                except Exception as e:
                    print(f"Error processing {txt_file.name}: {e}")
                    results['failed'] += 1
        
        return results
    
    def process_with_langextract(self, text: str, filename: str, adobe_metadata: Dict = None) -> Optional[Dict]:
        """Process text with LangExtract, using Adobe metadata if available"""
        
        try:
            # Clean text and filename to avoid Unicode issues on Windows
            clean_text = text.encode('ascii', 'replace').decode('ascii')
            clean_filename = filename.encode('ascii', 'replace').decode('ascii')
            
            # Classify document
            doc_type = self.medical_processor.classify_document(clean_text, clean_filename)
            
            # Extract structured data
            extracted_data = self.medical_processor.extract_by_type(clean_text, doc_type)
            
            # Extract medical concepts (use clean text)
            concepts = self.medical_processor.extract_medical_concepts(clean_text)
            extracted_data['medical_concepts'] = concepts
            
            # Generate Q&A pairs (optional - can be disabled)
            if self.enable_qa_generation:
                try:
                    # Skip Q&A generation for very long documents (>50k chars) to avoid timeouts
                    if len(text) > 50000:
                        print(f"  [SKIP] Skipping Q&A generation for {clean_filename} (document too long: {len(clean_text)} chars)")
                        extracted_data['qa_pairs'] = []
                    else:
                        print(f"  [QA] Generating Q&A pairs for {clean_filename}...")
                        qa_pairs = self.medical_processor.generate_qa_pairs(clean_text, doc_type)
                        extracted_data['qa_pairs'] = qa_pairs
                        print(f"  [OK] Generated {len(qa_pairs) if qa_pairs else 0} Q&A pairs")
                except KeyboardInterrupt:
                    print(f"  [INTERRUPTED] Q&A generation interrupted for {clean_filename}")
                    extracted_data['qa_pairs'] = []
                except Exception as e:
                    error_msg = str(e).encode('ascii', 'replace').decode('ascii')
                    print(f"  [WARNING] Q&A generation failed for {clean_filename}: {error_msg}")
                    extracted_data['qa_pairs'] = []
            else:
                print(f"  [DISABLED] Q&A generation disabled for {clean_filename}")
                extracted_data['qa_pairs'] = []
            
            # Create metadata
            metadata = {
                'source_file': clean_filename,
                'document_type': doc_type,
                'extraction_date': datetime.now().isoformat(),
                'extraction_model': 'gemini-2.5-pro',
                'char_count': len(clean_text),
                'word_count': len(clean_text.split())
            }
            
            # Add Adobe metadata if available
            if adobe_metadata:
                metadata['adobe_extract'] = {
                    'title': adobe_metadata.get('Title', ''),
                    'author': adobe_metadata.get('Author', ''),
                    'pages': adobe_metadata.get('Pages', 0),
                    'creation_date': adobe_metadata.get('CreationDate', ''),
                    'has_tables': 'Tables' in adobe_metadata,
                    'has_images': 'Images' in adobe_metadata
                }
            
            extracted_data['metadata'] = metadata
            extracted_data['raw_text'] = clean_text
            
            return extracted_data
            
        except Exception as e:
            # Handle Unicode errors more specifically
            if "'charmap' codec can't encode" in str(e):
                clean_filename = filename.encode('ascii', 'replace').decode('ascii')
                print(f"Unicode error extracting from {clean_filename}: creating fallback result")
                # Create a minimal fallback result
                return {
                    'document_type': 'general',
                    'extracted_data': {'content': 'Document processed with Unicode limitations'},
                    'medical_concepts': [],
                    'qa_pairs': [],
                    'metadata': {
                        'source_file': clean_filename,
                        'document_type': 'general',
                        'extraction_date': datetime.now().isoformat(),
                        'extraction_model': 'gemini-2.5-pro-fallback',
                        'char_count': len(clean_text) if 'clean_text' in locals() else 0,
                        'word_count': len(clean_text.split()) if 'clean_text' in locals() else 0,
                        'unicode_error': True
                    },
                    'raw_text': clean_text if 'clean_text' in locals() else 'Text unavailable due to encoding issues'
                }
            else:
                error_msg = str(e).encode('ascii', 'replace').decode('ascii')
                clean_filename = filename.encode('ascii', 'replace').decode('ascii')
                print(f"Error extracting from {clean_filename}: {error_msg}")
                return None
    
    def process_json_only(self, json_file: Path) -> Optional[Dict]:
        """Process JSON file when text is embedded in JSON"""
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract text from JSON structure (Adobe Extract format)
            text = ""
            
            # Common Adobe Extract JSON structure
            if 'elements' in data:
                for element in data['elements']:
                    if 'Text' in element:
                        text += element['Text'] + "\n"
                    elif 'text' in element:
                        text += element['text'] + "\n"
            elif 'content' in data:
                text = data['content']
            elif 'text' in data:
                text = data['text']
            
            if text:
                return self.process_with_langextract(text, json_file.stem, data)
            else:
                print(f"  No text found in {json_file.name}")
                return None
                
        except Exception as e:
            print(f"Error processing JSON {json_file.name}: {e}")
            return None
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Chunk text for processing"""
        
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks

    def get_xml_statistics(self) -> Dict[str, Any]:
        """Get statistics about XML metadata"""
        return self.xml_processor.get_statistics()
    
    def find_articles_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Find articles by keyword using XML metadata"""
        return self.xml_processor.find_articles_by_keyword(keyword)
    
    def find_articles_by_section(self, section: str) -> List[Dict[str, Any]]:
        """Find articles by section using XML metadata"""
        return self.xml_processor.find_articles_by_section(section)

    def save_to_processed_chunks(self, extracted_data: Dict[str, Any], filename: str, chunks_dir: Path):
        """Save extracted data to processed_chunks folder"""
        
        try:
            # Create chunks from extracted data
            chunks = self.create_chunks_from_extracted_data(extracted_data, filename)
            
            # Save chunks to file
            chunks_file = chunks_dir / f"{filename}_chunks.json"
            with open(chunks_file, 'w', encoding='utf-8') as f:
                json.dump(chunks, f, indent=2, ensure_ascii=False)
            
            print(f"  [SAVED] Saved {len(chunks)} chunks to {chunks_file}")
            
        except Exception as e:
            error_msg = str(e).encode('ascii', 'replace').decode('ascii')
            safe_filename = filename.encode('ascii', 'replace').decode('ascii')
            print(f"  [ERROR] Error saving chunks for {safe_filename}: {error_msg}")
    
    def create_chunks_from_extracted_data(self, extracted_data: Dict[str, Any], filename: str) -> List[Dict[str, Any]]:
        """Create chunks from extracted data"""
        
        chunks = []
        
        # Handle the nested structure from LangExtract
        if 'extracted_data' in extracted_data:
            doc_type = extracted_data.get('document_type', 'general')
            doc_data = extracted_data.get('extracted_data', {})
            metadata = extracted_data.get('metadata', {})
        else:
            doc_type = extracted_data.get('document_type', 'general')
            doc_data = extracted_data
            metadata = extracted_data.get('metadata', {})
        
        # If doc_data is a list (for example, a list of extraction dictionaries),
        # convert it into a dictionary keyed by extraction class. Each list
        # element becomes a list of `extraction_text` values under its
        # extraction_class key. Non-dict elements are grouped under the `items`
        # key. This conversion ensures that doc_data behaves like a mapping and
        # can be iterated over safely when constructing the main overview chunk.
        if isinstance(doc_data, list):
            processed_dict = {}
            for item in doc_data:
                if isinstance(item, dict):
                    extraction_class = item.get('extraction_class', 'unknown')
                    extraction_text = item.get('extraction_text', '') or str(item)
                    processed_dict.setdefault(extraction_class, []).append(extraction_text)
                else:
                    processed_dict.setdefault('items', []).append(str(item))
            doc_data = processed_dict
        
        # Create main content chunk
        main_chunk = {
            'text': f"Document Type: {doc_type}\nSource: {filename}\n\n",
            'metadata': {
                'type': f'{doc_type}_overview',
                'source': filename,
                'chunk_type': 'overview',
                'document_type': doc_type
            }
        }
        
        # Add extracted fields to main chunk
        if isinstance(doc_data, dict):
            for key, value in doc_data.items():
                try:
                    if isinstance(value, list):
                        # Handle list values safely
                        safe_values = []
                        for v in value[:5]:  # Limit to first 5 items
                            if isinstance(v, dict):
                                safe_values.append(str(v)[:100])  # Truncate dict representations
                            else:
                                safe_values.append(str(v))
                        main_chunk['text'] += f"{key.replace('_', ' ').title()}: {', '.join(safe_values)}\n"
                    elif isinstance(value, dict):
                        main_chunk['text'] += f"{key.replace('_', ' ').title()}: {str(value)[:200]}...\n"
                    else:
                        main_chunk['text'] += f"{key.replace('_', ' ').title()}: {str(value)}\n"
                except Exception as e:
                    # If there's any issue with processing this field, skip it
                    main_chunk['text'] += f"{key.replace('_', ' ').title()}: [Error processing field]\n"
        
        chunks.append(main_chunk)
        
        # Add Q&A pairs as separate chunks
        if 'qa_pairs' in extracted_data:
            qa_pairs = extracted_data['qa_pairs']
            if hasattr(qa_pairs, '__iter__') and not isinstance(qa_pairs, str):
                for i, qa in enumerate(qa_pairs):
                    if isinstance(qa, dict):
                        qa_text = f"Q: {qa.get('question', '')}\nA: {qa.get('answer', '')}"
                        chunks.append({
                            'text': qa_text,
                            'metadata': {
                                'type': 'qa_pair',
                                'source': filename,
                                'chunk_type': 'qa',
                                'qa_index': i,
                                'question_type': qa.get('question_type', 'unknown')
                            }
                        })
        
        # Add medical concepts as separate chunks
        if 'medical_concepts' in extracted_data:
            concepts = extracted_data['medical_concepts']
            if isinstance(concepts, dict):
                for concept_type, concept_list in concepts.items():
                    if concept_list and isinstance(concept_list, list):
                        concept_text = f"{concept_type.replace('_', ' ').title()}: {', '.join(concept_list)}"
                        chunks.append({
                            'text': concept_text,
                            'metadata': {
                                'type': 'medical_concept',
                                'source': filename,
                                'chunk_type': 'concept',
                                'concept_type': concept_type
                            }
                        })
        
        return chunks

# Utility function to process all existing data
def process_existing_data(enable_qa: bool = True):
    """Process all existing text/JSON files from input_articles directory"""
    
    processor = DocumentProcessor(enable_qa_generation=enable_qa)
    
    # Process files from input_articles directory
    input_articles_path = Path('./data/input_articles')
    if input_articles_path.exists():
        print("Processing files from input_articles directory...")
        results = processor.process_adobe_extract_files(input_articles_path)
        print(f"Input Articles: Processed {results['processed']}/{results['total_files']} files")
    else:
        print("No input_articles directory found. Creating it...")
        input_articles_path.mkdir(parents=True, exist_ok=True)
        print("Created input_articles directory. Please add your JSON files there.")
    
    # Get statistics
    stats = processor.knowledge_base.get_statistics()
    print(f"\nKnowledge Base Statistics:")
    print(f"  Total chunks: {stats['total_chunks']}")
    for collection, count in stats['collections'].items():
        print(f"  {collection}: {count} chunks")

if __name__ == "__main__":
    process_existing_data()