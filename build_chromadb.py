#!/usr/bin/env python3
"""
Build ChromaDB from processed chunks
"""

import json
from pathlib import Path
from src.knowledge_base.vector_store import MedicalKnowledgeBase

def build_chromadb_from_chunks():
    """Build ChromaDB from processed chunks"""
    
    print("Building ChromaDB from processed chunks...")
    
    # Initialize knowledge base
    kb = MedicalKnowledgeBase()
    
    # Check if processed_chunks directory exists
    processed_chunks_dir = Path('./data/processed_chunks')
    if not processed_chunks_dir.exists():
        print("❌ No processed_chunks directory found!")
        print("Please run 'python main.py process-existing' first to create chunks.")
        return
    
    # Find all chunk files
    chunk_files = list(processed_chunks_dir.glob("*_chunks.json"))
    print(f"Found {len(chunk_files)} chunk files")
    
    if not chunk_files:
        print("❌ No chunk files found!")
        print("Please run 'python main.py process-existing' first to create chunks.")
        return
    
    # Process each chunk file
    total_chunks = 0
    for chunk_file in chunk_files:
        print(f"Processing {chunk_file.name}...")
        
        try:
            with open(chunk_file, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
            
            # Add chunks to ChromaDB
            for chunk in chunks:
                if isinstance(chunk, dict) and 'text' in chunk and 'metadata' in chunk:
                    # Generate embedding
                    embedding = kb.embedder.encode(chunk['text']).tolist()
                    
                    # Generate unique ID
                    chunk_id = kb.generate_chunk_id(chunk['text'])
                    
                    # Determine collection based on chunk type
                    chunk_type = chunk['metadata'].get('chunk_type', 'general')
                    if chunk_type == 'qa':
                        collection = kb.collections['qa_pairs']
                    elif chunk_type == 'concept':
                        collection = kb.collections['concepts']
                    else:
                        # Default to procedures collection
                        collection = kb.collections['procedures']
                    
                    # Add to collection
                    collection.add(
                        embeddings=[embedding],
                        documents=[chunk['text']],
                        metadatas=[chunk['metadata']],
                        ids=[chunk_id]
                    )
                    
                    total_chunks += 1
            
            print(f"  ✅ Added {len(chunks)} chunks from {chunk_file.name}")
            
        except Exception as e:
            print(f"  ❌ Error processing {chunk_file.name}: {e}")
    
    # Print final statistics
    stats = kb.get_statistics()
    print(f"\n🎉 ChromaDB build complete!")
    print(f"Total chunks: {stats['total_chunks']}")
    for collection, count in stats['collections'].items():
        print(f"  {collection}: {count} chunks")

if __name__ == "__main__":
    build_chromadb_from_chunks()
