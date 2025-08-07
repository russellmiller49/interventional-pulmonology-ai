import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import hashlib
from datetime import datetime
import numpy as np

class MedicalKnowledgeBase:
    """Vector store for medical knowledge with hybrid search capabilities"""
    
    def __init__(self, persist_directory: str = "./data/chroma_db"):
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding model (medical-specific if available)
        self.embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        # Create collections for different content types
        self.collections = {
            'procedures': self.get_or_create_collection('procedures'),
            'guidelines': self.get_or_create_collection('guidelines'),
            'research': self.get_or_create_collection('research'),
            'qa_pairs': self.get_or_create_collection('qa_pairs'),
            'concepts': self.get_or_create_collection('concepts')
        }
    
    def get_or_create_collection(self, name: str):
        """Get or create a ChromaDB collection"""
        try:
            return self.client.get_collection(name)
        except:
            return self.client.create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}
            )
    
    def add_extracted_document(self, extracted_data: Dict[str, Any]):
        """Add an extracted document to the knowledge base"""
        
        # Handle the nested structure from LangExtract
        if 'extracted_data' in extracted_data:
            # This is the structure returned by extract_by_type
            doc_type = extracted_data.get('document_type', 'general')
            doc_data = extracted_data.get('extracted_data', {})
            metadata = extracted_data.get('metadata', {})
        else:
            # Direct structure (fallback)
            doc_type = extracted_data.get('document_type', 'general')
            doc_data = extracted_data
            metadata = extracted_data.get('metadata', {})
        
        # Create searchable text based on document type
        searchable_chunks = self.create_searchable_chunks(doc_type, doc_data, metadata)
        
        # Add to appropriate collection
        collection = self.collections.get(doc_type, self.collections['procedures'])
        
        for chunk in searchable_chunks:
            # Generate unique ID
            chunk_id = self.generate_chunk_id(chunk['text'])
            
            # Generate embedding
            embedding = self.embedder.encode(chunk['text']).tolist()
            
            # Add to collection
            collection.add(
                embeddings=[embedding],
                documents=[chunk['text']],
                metadatas=[chunk['metadata']],
                ids=[chunk_id]
            )
        
        # Add Q&A pairs if available
        if 'qa_pairs' in extracted_data:
            self.add_qa_pairs(extracted_data['qa_pairs'], metadata)
        
        # Add medical concepts
        if 'medical_concepts' in extracted_data:
            self.add_medical_concepts(extracted_data['medical_concepts'], metadata)
    
    def create_searchable_chunks(self, doc_type: str, doc_data: Dict, metadata: Dict) -> List[Dict]:
        """Create searchable chunks from extracted data"""
        
        chunks = []
        source_file = metadata.get('source_file', 'unknown')
        
        # Handle LangExtract output structure
        if isinstance(doc_data, dict):
            # Create a general chunk from all extracted data
            chunk_text = f"Document Type: {doc_type}\nSource: {source_file}\n\n"
            
            # Add all extracted fields
            for key, value in doc_data.items():
                if isinstance(value, list):
                    chunk_text += f"{key.replace('_', ' ').title()}: {', '.join(str(v) for v in value[:5])}\n"
                elif isinstance(value, dict):
                    chunk_text += f"{key.replace('_', ' ').title()}: {str(value)[:200]}...\n"
                else:
                    chunk_text += f"{key.replace('_', ' ').title()}: {str(value)}\n"
            
            chunks.append({
                'text': chunk_text,
                'metadata': {
                    'type': f'{doc_type}_overview',
                    'source': source_file,
                    'chunk_type': 'overview',
                    'document_type': doc_type
                }
            })
            
            # Create specific chunks for different data types
            if doc_type == 'procedure':
                # Procedure-specific chunks
                if 'procedure_name' in doc_data:
                    procedure_chunk = f"""
                    Procedure: {doc_data.get('procedure_name', 'Unknown')}
                    Type: {doc_data.get('procedure_type', 'Unknown')}
                    Location: {doc_data.get('anatomical_location', 'Unknown')}
                    Indications: {', '.join(doc_data.get('indications', []))}
                    Contraindications: {', '.join(doc_data.get('contraindications', []))}
                    """
                    chunks.append({
                        'text': procedure_chunk,
                        'metadata': {
                            'type': 'procedure_details',
                            'procedure_name': doc_data.get('procedure_name'),
                            'source': source_file,
                            'chunk_type': 'procedure'
                        }
                    })
            
            elif doc_type == 'guideline':
                # Guideline-specific chunks
                if 'guideline_title' in doc_data or 'condition' in doc_data:
                    guideline_chunk = f"""
                    Guideline: {doc_data.get('guideline_title', 'Unknown')}
                    Condition: {doc_data.get('condition', 'Unknown')}
                    First-line treatment: {doc_data.get('first_line_treatment', 'Unknown')}
                    Evidence Grade: {doc_data.get('evidence_grade', 'Unknown')}
                    """
                    chunks.append({
                        'text': guideline_chunk,
                        'metadata': {
                            'type': 'guideline_summary',
                            'condition': doc_data.get('condition'),
                            'source': source_file,
                            'chunk_type': 'guideline'
                        }
                    })
            
            elif doc_type == 'research':
                # Research-specific chunks
                if 'study_design' in doc_data or 'findings' in doc_data:
                    research_chunk = f"""
                    Study Design: {doc_data.get('study_design', 'Unknown')}
                    Population: {doc_data.get('patient_population', 'Unknown')}
                    Findings: {', '.join(doc_data.get('findings', []))}
                    Conclusions: {doc_data.get('conclusions', 'Unknown')}
                    """
                    chunks.append({
                        'text': research_chunk,
                        'metadata': {
                            'type': 'research_summary',
                            'study_design': doc_data.get('study_design'),
                            'source': source_file,
                            'chunk_type': 'research'
                        }
                    })
        
        # If no chunks were created, create a basic chunk
        if not chunks:
            basic_chunk = f"""
            Document Type: {doc_type}
            Source: {source_file}
            Content: {str(doc_data)[:500]}...
            """
            chunks.append({
                'text': basic_chunk,
                'metadata': {
                    'type': 'general_content',
                    'source': source_file,
                    'chunk_type': 'general',
                    'document_type': doc_type
                }
            })
        
        return chunks
    
    def add_qa_pairs(self, qa_pairs: List[Dict], metadata: Dict):
        """Add Q&A pairs to the knowledge base"""
        
        collection = self.collections['qa_pairs']
        
        for qa in qa_pairs:
            # Create searchable text
            qa_text = f"""
            Question: {qa.get('question', '')}
            Answer: {qa.get('answer', '')}
            Context: {qa.get('clinical_context', '')}
            Evidence Quality: {qa.get('evidence_quality', '')}
            """
            
            # Generate embedding
            embedding = self.embedder.encode(qa_text).tolist()
            
            # Generate ID
            qa_id = self.generate_chunk_id(qa_text)
            
            # Add to collection
            collection.add(
                embeddings=[embedding],
                documents=[qa_text],
                metadatas=[{
                    'question': qa.get('question'),
                    'answer': qa.get('answer'),
                    'question_type': qa.get('question_type'),
                    'difficulty': qa.get('difficulty_level'),
                    'source': metadata.get('source_file')
                }],
                ids=[qa_id]
            )
    
    def add_medical_concepts(self, concepts: Dict[str, List[str]], metadata: Dict):
        """Add medical concepts for enhanced searchability"""
        
        collection = self.collections['concepts']
        
        # Create concept chunks
        for concept_type, concept_list in concepts.items():
            if concept_list:
                concept_text = f"{concept_type}: {', '.join(concept_list)}"
                
                # Generate embedding
                embedding = self.embedder.encode(concept_text).tolist()
                
                # Generate ID
                concept_id = self.generate_chunk_id(concept_text)
                
                # Add to collection
                collection.add(
                    embeddings=[embedding],
                    documents=[concept_text],
                    metadatas=[{
                        'concept_type': concept_type,
                        'concepts': concept_list,
                        'source': metadata.get('source_file')
                    }],
                    ids=[concept_id]
                )
    
    def search(self, query: str, collection_name: str = None, n_results: int = 5) -> List[Dict]:
        """Search the knowledge base"""
        
        # Generate query embedding
        query_embedding = self.embedder.encode(query).tolist()
        
        # Search in specified collection or all collections
        if collection_name:
            collections_to_search = [self.collections.get(collection_name)]
        else:
            collections_to_search = self.collections.values()
        
        all_results = []
        
        for collection in collections_to_search:
            if collection:
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results
                )
                
                # Format results
                for i in range(len(results['ids'][0])):
                    all_results.append({
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i]
                    })
        
        # Sort by distance (lower is better)
        all_results.sort(key=lambda x: x['distance'])
        
        return all_results[:n_results]
    
    def generate_chunk_id(self, text: str) -> str:
        """Generate a unique ID for a chunk"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def load_extracted_data(self, extracted_data_dir: Path):
        """Load all extracted data into the knowledge base"""
        
        json_files = list(extracted_data_dir.glob("*_extracted.json"))
        
        for json_file in json_files:
            print(f"Loading {json_file.name}")
            
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            if data:
                self.add_extracted_document(data)
        
        print(f"Loaded {len(json_files)} documents into knowledge base")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        
        stats = {
            'collections': {},
            'total_chunks': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        for name, collection in self.collections.items():
            count = collection.count()
            stats['collections'][name] = count
            stats['total_chunks'] += count
        
        return stats