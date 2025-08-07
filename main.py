#!/usr/bin/env python3
"""
Interventional Pulmonology Chatbot - CLI Interface
"""

import argparse
import sys
from pathlib import Path
from src.knowledge_base.document_processor import DocumentProcessor, process_existing_data
from src.extractors.langextract_processor import MedicalDocumentProcessor, batch_process_medical_documents
from src.chatbot.rag_pipeline import InterventionalPulmonologyBot

def process_text_json(directory_path: str):
    """Process text and JSON files from Adobe Extract"""
    processor = DocumentProcessor()
    path = Path(directory_path)
    
    if not path.exists():
        print(f"Error: Directory {directory_path} does not exist")
        return
    
    print(f"Processing text/JSON files from {directory_path}...")
    results = processor.process_adobe_extract_files(path)
    
    print(f"\nResults:")
    print(f"  Total files: {results['total_files']}")
    print(f"  Successfully processed: {results['processed']}")
    print(f"  Failed: {results['failed']}")
    
    # Show knowledge base statistics
    stats = processor.knowledge_base.get_statistics()
    print(f"\nKnowledge Base Statistics:")
    print(f"  Total chunks: {stats['total_chunks']}")
    for collection, count in stats['collections'].items():
        print(f"  {collection}: {count} chunks")

def process_pdfs(directory_path: str):
    """Process PDF files"""
    processor = MedicalDocumentProcessor()
    path = Path(directory_path)
    output_path = Path('./data/extracted_data')
    
    if not path.exists():
        print(f"Error: Directory {directory_path} does not exist")
        return
    
    print(f"Processing PDF files from {directory_path}...")
    processor.process_directory(path, output_path)

def chat_interface():
    """Simple command-line chat interface"""
    bot = InterventionalPulmonologyBot()
    
    print("\n🫁 Interventional Pulmonology Assistant")
    print("=" * 50)
    print("Type 'quit' to exit, 'help' for commands")
    print("=" * 50)
    
    while True:
        try:
            question = input("\nYour question: ").strip()
            
            if question.lower() == 'quit':
                print("Goodbye!")
                break
            elif question.lower() == 'help':
                print("\nAvailable commands:")
                print("  quit - Exit the chatbot")
                print("  help - Show this help message")
                print("  stats - Show knowledge base statistics")
                continue
            elif question.lower() == 'stats':
                stats = bot.knowledge_base.get_statistics()
                print(f"\nKnowledge Base Statistics:")
                print(f"  Total chunks: {stats['total_chunks']}")
                for collection, count in stats['collections'].items():
                    print(f"  {collection}: {count} chunks")
                continue
            
            if question:
                print("\nSearching knowledge base...")
                response = bot.answer_question(question, include_sources=True)
                
                print(f"\n{'=' * 50}")
                print("Answer:")
                print(response['answer'])
                print(f"\nConfidence: {response['confidence']:.0%}")
                
                if 'sources' in response and response['sources']:
                    print(f"\n{'=' * 50}")
                    print("Sources:")
                    for i, source in enumerate(response['sources'][:3], 1):
                        print(f"\n{i}. {source['source']} (Relevance: {source['relevance_score']:.2f})")
                        print(f"   {source['text']}")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

def build_chromadb():
    """Build ChromaDB from processed chunks"""
    from build_chromadb import build_chromadb_from_chunks
    build_chromadb_from_chunks()

def main():
    parser = argparse.ArgumentParser(description='Interventional Pulmonology Chatbot')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Process text/JSON command
    text_parser = subparsers.add_parser('process-text', help='Process text/JSON files from input directory')
    text_parser.add_argument('directory', help='Directory containing text/JSON files')
    
    # Process PDFs command
    pdf_parser = subparsers.add_parser('process-pdf', help='Process PDF files')
    pdf_parser.add_argument('directory', help='Directory containing PDF files')
    
    # Process all existing data
    existing_parser = subparsers.add_parser('process-existing', help='Process all existing data from input_articles directory')
    existing_parser.add_argument('--no-qa', action='store_true', help='Disable Q&A generation (faster processing)')
    
    # Build ChromaDB from chunks
    build_parser = subparsers.add_parser('build-chromadb', help='Build ChromaDB from processed chunks')
    
    # Chat command
    chat_parser = subparsers.add_parser('chat', help='Start interactive chat interface')
    
    args = parser.parse_args()
    
    if args.command == 'process-text':
        process_text_json(args.directory)
    elif args.command == 'process-pdf':
        process_pdfs(args.directory)
    elif args.command == 'process-existing':
        enable_qa = not args.no_qa  # If --no-qa is specified, disable Q&A generation
        process_existing_data(enable_qa=enable_qa)
    elif args.command == 'build-chromadb':
        build_chromadb()
    elif args.command == 'chat':
        chat_interface()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()