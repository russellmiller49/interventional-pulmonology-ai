# 🫁 Interventional Pulmonology AI Assistant

An AI-powered chatbot for interventional pulmonology that processes medical documents using LangExtract and provides evidence-based responses through a RAG (Retrieval-Augmented Generation) pipeline.

## 🎯 Features

- **Medical Document Processing**: Extract structured information from medical PDFs and JSON files
- **Intelligent Q&A**: Generate evidence-based responses with source citations
- **Vector Search**: Semantic search through medical knowledge base
- **Web Interface**: User-friendly Streamlit interface
- **CLI Tools**: Command-line interface for batch processing
- **XML Metadata**: Enhanced processing with rich article metadata

## 🏗️ Architecture

```
JSON Files → LangExtract → Vector DB → RAG Pipeline → Chatbot UI
```

## 📁 Project Structure

```
interventional-pulmonology-ai/
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
│   ├── input_articles/           # Your JSON files go here
│   ├── raw_pdfs/                 # For PDF files
│   ├── processed_chunks/         # Processed data
│   ├── extracted_data/           # Extracted results
│   └── Combined.xml              # XML metadata (optional)
├── config/
│   └── settings.py               # Configuration and API keys
├── main.py                       # CLI entry point
├── app.py                        # Streamlit web interface
├── quickstart.py                 # Quick setup script
└── requirements.txt
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- API keys for [Gemini](https://makersuite.google.com/app/apikey) and [OpenAI](https://platform.openai.com/api-keys)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/interventional-pulmonology-ai.git
   cd interventional-pulmonology-ai
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

4. **Add your medical documents**
   ```bash
   # Copy your JSON files to data/input_articles/
   cp your_medical_files.json data/input_articles/
   ```

5. **Process your documents**
   ```bash
   # Process all files in input_articles
   python main.py process-existing
   
   # Or process specific directory
   python main.py process-text "data/input_articles"
   ```

6. **Start the web interface**
   ```bash
   streamlit run app.py
   ```

## 📚 Usage

### Command Line Interface

```bash
# Process existing JSON files
python main.py process-existing

# Process specific directory
python main.py process-text "path/to/files"

# Process PDF files
python main.py process-pdf "path/to/pdfs"

# Build ChromaDB from processed chunks
python main.py build-chromadb

# Start interactive chat
python main.py chat
```

### Web Interface

```bash
streamlit run app.py
```

Access the web interface at `http://localhost:8501`

### Python API

```python
from src.chatbot.rag_pipeline import InterventionalPulmonologyBot

# Initialize the bot
bot = InterventionalPulmonologyBot()

# Ask a question
response = bot.answer_question("What are the indications for bronchoscopy?")
print(response['answer'])
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with your API keys:

```env
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
NEW_DOCS_PATH=./data/new_docs
```

### Model Settings

You can customize the models used in `config/settings.py`:

```python
# Model Settings
EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
LLM_MODEL = 'gpt-4-turbo-preview'
EXTRACTION_MODEL = 'gemini-2.5-pro'
```

## 📊 Data Processing

### Supported File Types

- **JSON files**: Adobe Extract output (primary)
- **PDF files**: Medical documents and research papers
- **Text files**: Plain text medical content

### Processing Pipeline

1. **Document Classification**: Automatically classify documents by type
2. **Structured Extraction**: Extract medical entities using LangExtract
3. **Chunk Creation**: Create searchable chunks for vector storage
4. **Metadata Enhancement**: Add XML metadata if available
5. **Vector Storage**: Store in ChromaDB for semantic search

### Chunk Types

- **Overview chunks**: Document summaries and key information
- **Q&A chunks**: Generated question-answer pairs
- **Concept chunks**: Medical concepts and terminology
- **Procedure chunks**: Step-by-step procedures

## 🎯 Medical Focus Areas

- **Bronchoscopy**: Techniques, indications, complications
- **Pleural Procedures**: Thoracentesis, chest tube insertion
- **Airway Management**: Emergency procedures, stenting
- **Diagnostic Techniques**: Biopsy, imaging, testing
- **Guidelines**: Clinical recommendations and protocols

## 🔍 Search Capabilities

- **Semantic Search**: Find relevant content using natural language
- **Source Attribution**: Always cite sources for medical information
- **Confidence Scoring**: Indicate confidence in responses
- **Context Awareness**: Consider document type and context

## 🛠️ Development

### Running Tests

```bash
python -m pytest tests/
```

### Code Style

```bash
# Format code
black src/
isort src/

# Lint code
flake8 src/
```

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for **educational and informational purposes only**. It is not a substitute for professional medical judgment. Always consult qualified healthcare providers for medical decisions.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📞 Support

- Create an issue for bugs or feature requests
- Check the documentation in the `docs/` folder
- Join our community discussions

## 🎉 Acknowledgments

- Built with [LangExtract](https://github.com/jxnl/langextract) for structured extraction
- Powered by [ChromaDB](https://www.trychroma.com/) for vector storage
- Interface built with [Streamlit](https://streamlit.io/)
- Medical knowledge processing with [Gemini](https://ai.google.dev/gemini-api) and [OpenAI](https://openai.com/)