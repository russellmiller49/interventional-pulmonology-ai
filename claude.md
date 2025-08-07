# Interventional Pulmonology AI Assistant

## Project Overview
Medical AI chatbot using LangExtract for structured information extraction and RAG for intelligent responses. Processes medical JSON files from Adobe Extract, guidelines, and research papers to provide evidence-based answers.

## Architecture
```
JSON Files → LangExtract → Vector DB → RAG Pipeline → Chatbot UI
```

## Project Structure
```
IP chat/
├── src/
│   ├── extractors/
│   │   ├── custom_schemas.py      # Medical extraction schemas
│   │   ├── langextract_processor.py # LangExtract processing
│   │   └── schemas.py             # Base schemas
│   ├── knowledge_base/
│   │   ├── document_processor.py  # Document processing
│   │   ├── vector_store.py        # ChromaDB management
│   │   └── xml_processor.py       # XML metadata processing
│   └── chatbot/
│       └── rag_pipeline.py        # RAG implementation
├── data/
│   ├── input_articles/           # ✅ Your JSON files go here
│   ├── raw_pdfs/                 # For PDF files
│   ├── processed_chunks/         # Processed data
│   ├── extracted_data/           # Extracted results
│   └── Combined.xml              # ✅ XML metadata (optional)
├── config/
│   └── settings.py               # Configuration and API keys
├── main.py                       # CLI entry point
├── app.py                        # Streamlit web interface
├── quickstart.py                 # Quick setup script
└── requirements.txt
```

## Tech Stack
- **LangExtract**: Structured extraction from medical documents
- **ChromaDB**: Vector database for semantic search
- **Streamlit**: Web interface
- **Google Gemini 2.5 Pro**: Primary LLM for extraction
- **OpenAI**: Embeddings and chat completion
- **Sentence Transformers**: Text embeddings

## Environment Setup
```bash
# Key environment variables (.env)
GEMINI_API_KEY=your_key
OPENAI_API_KEY=your_key
NEW_DOCS_PATH=C:\Users\russe\OneDrive\new_medical_docs
```

## Main Commands
```bash
# Install and setup
pip install -r requirements.txt

# Process existing JSON files from input_articles
python main.py process-existing

# Process specific directory
python main.py process-text "data/input_articles"

# Launch web interface  
streamlit run app.py

# CLI chat
python main.py chat

# Process new PDFs
python main.py process-pdf "path/to/pdfs"
```

## Document Types
- **Procedures**: Bronchoscopy, thoracentesis, chest tube insertion
- **Guidelines**: Society recommendations, protocols
- **Research**: Clinical studies, systematic reviews
- **Reference**: Diagnostic criteria, anatomy guides

## Key Features
- Medical document classification and extraction
- Q&A pair generation for better responses
- Source attribution and confidence scoring
- Real-time chat with medical knowledge base
- Batch processing of medical literature
- XML metadata enhancement (optional)

## Data Flow
1. **Input**: JSON files from Adobe Extract (primary) or PDFs
2. **Processing**: LangExtract schemas extract structured medical content
3. **Enhancement**: XML metadata added if available (281 articles)
4. **Storage**: ChromaDB for semantic search and retrieval
5. **Query**: RAG pipeline retrieves relevant context for user questions
6. **Output**: Evidence-based responses with source citations

## Medical Schemas
- DocumentMetadata: Title, authors, document type
- KeyConcepts: Medical terminology, procedures, conditions
- TechnicalContent: Procedures, contraindications, complications
- ResearchContent: Methodology, findings, clinical significance
- QAPair: Medical Q&A for training and responses

## Fresh Start Setup
This project has been updated for a fresh start without Kotaemon dependencies:

### Directory Structure
```
data/
├── input_articles/          # ✅ Your JSON files go here
├── raw_pdfs/               # ✅ For PDF files
├── processed_chunks/       # ✅ Processed data
├── extracted_data/         # ✅ Extracted results
└── Combined.xml           # ✅ Your XML metadata (optional)
```

### Quick Start
1. **Add your JSON files** to `data/input_articles/`
2. **Process them**: `python main.py process-existing`
3. **Start chatting**: `python main.py chat` or `streamlit run app.py`

## Current Status
- ✅ **Fresh start** - No Kotaemon dependencies
- ✅ **JSON processing** - Optimized for Adobe Extract JSON files
- ✅ **XML metadata** - 281 articles with rich metadata available
- ✅ **Gemini 2.5 Pro** - Latest extraction model
- ✅ **Streamlined workflow** - Focus on input_articles directory
- 🔄 **Building knowledge base** from interventional pulmonology literature
- 🔄 **Optimizing** for medical terminology and clinical context
- 🔄 **Focus** on evidence-based responses with proper attribution

## Important Notes
- Medical information tool - not for clinical decision-making
- Requires API keys for Gemini (extraction) and OpenAI (chat)
- Uses `data/input_articles/` for your JSON files
- XML metadata enhancement available (optional)
- Prioritizes accuracy and source attribution for medical content
- Fresh start - no legacy Kotaemon dependencies