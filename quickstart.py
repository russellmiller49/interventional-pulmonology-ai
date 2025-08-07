#!/usr/bin/env python3
"""
Quick Start Script for Interventional Pulmonology Chatbot
Runs initial setup and processing automatically
"""

import os
import sys
from pathlib import Path

def check_environment():
    """Check if environment is properly set up"""
    print("🔍 Checking environment setup...")
    
    # Check for .env file
    if not Path('.env').exists():
        print("❌ .env file not found!")
        print("Please create .env file with your API keys")
        return False
    
    # Check for API keys
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv('GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY') == 'your_gemini_api_key_here':
        print("❌ GEMINI_API_KEY not configured in .env file")
        print("Get your key from: https://makersuite.google.com/app/apikey")
        return False
    
    if not os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY') == 'your_openai_api_key_here':
        print("❌ OPENAI_API_KEY not configured in .env file") 
        print("Get your key from: https://platform.openai.com/api-keys")
        return False
    
    print("✅ Environment configured correctly!")
    return True

def check_dependencies():
    """Check if all required packages are installed"""
    print("\n🔍 Checking dependencies...")
    
    required_packages = [
        'streamlit',
        'langextract',
        'chromadb',
        'sentence_transformers',
        'openai',
        'PyPDF2'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies installed!")
    return True

def process_initial_data():
    """Process existing text/JSON data"""
    print("\n📚 Processing existing data...")
    
    from src.knowledge_base.document_processor import DocumentProcessor
    
    processor = DocumentProcessor()
    
    # Check if input_articles path exists
    input_articles_path = Path('./data/input_articles')
    
    if not input_articles_path.exists():
        print(f"⚠️ Input articles directory not found: {input_articles_path}")
        print("Creating input_articles directory...")
        input_articles_path.mkdir(parents=True, exist_ok=True)
        print("✅ Created input_articles directory")
        print("Please add your JSON files to data/input_articles/ and run again")
        return False
    
    # Check if there are any files
    json_files = list(input_articles_path.glob("*.json"))
    if not json_files:
        print(f"⚠️ No JSON files found in {input_articles_path}")
        print("Please add your JSON files to data/input_articles/ and run again")
        return False
    
    # Process the data
    print(f"Processing files from: {input_articles_path}")
    results = processor.process_adobe_extract_files(input_articles_path)
    
    print(f"\n✅ Processed {results['processed']} files successfully!")
    if results['failed'] > 0:
        print(f"⚠️ {results['failed']} files failed to process")
    
    # Show statistics
    stats = processor.knowledge_base.get_statistics()
    print(f"\n📊 Knowledge Base Statistics:")
    print(f"  Total chunks: {stats['total_chunks']}")
    
    return True

def main():
    print("=" * 60)
    print("🫁 Interventional Pulmonology Chatbot - Quick Start")
    print("=" * 60)
    
    # Step 1: Check environment
    if not check_environment():
        print("\n❌ Please fix environment issues and run again")
        sys.exit(1)
    
    # Step 2: Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies and run again")
        sys.exit(1)
    
    # Step 3: Ask about data processing
    print("\n" + "=" * 60)
    response = input("Do you want to process your existing text/JSON files now? (y/n): ")
    
    if response.lower() == 'y':
        if process_initial_data():
            print("\n✅ Initial setup complete!")
        else:
            print("\n⚠️ Data processing skipped")
    else:
        print("⚠️ Skipping data processing - you can do this later")
    
    # Step 4: Launch options
    print("\n" + "=" * 60)
    print("🚀 Setup complete! You can now:")
    print("\n1. Launch web interface:")
    print("   streamlit run app.py")
    print("\n2. Start command-line chat:")
    print("   python main.py chat")
    print("\n3. Process more documents:")
    print("   python main.py process-text <directory>")
    print("\n" + "=" * 60)
    
    response = input("\nLaunch web interface now? (y/n): ")
    if response.lower() == 'y':
        import subprocess
        print("\n🌐 Launching web interface...")
        print("The browser should open automatically. If not, go to http://localhost:8501")
        subprocess.run(["streamlit", "run", "app.py"])

if __name__ == "__main__":
    main()