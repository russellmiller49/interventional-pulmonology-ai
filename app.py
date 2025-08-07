import streamlit as st
from pathlib import Path
import json
from src.extractors.langextract_processor import MedicalDocumentProcessor
from src.knowledge_base.vector_store import MedicalKnowledgeBase
from src.knowledge_base.document_processor import DocumentProcessor
from src.chatbot.rag_pipeline import InterventionalPulmonologyBot

# Page config
st.set_page_config(
    page_title="Interventional Pulmonology Assistant",
    page_icon="🫁",
    layout="wide"
)

# Initialize session state
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = InterventionalPulmonologyBot()
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Main UI
st.title("🫁 Interventional Pulmonology Assistant")
st.markdown("AI-powered assistant for bronchoscopy, pleural procedures, and airway management")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Mode selection
    mode = st.selectbox(
        "Select Mode",
        ["Chat Assistant", "Document Processing", "Knowledge Base Management"]
    )
    
    if mode == "Chat Assistant":
        st.markdown("### Chat Settings")
        include_sources = st.checkbox("Show sources", value=True)
        confidence_threshold = st.slider("Confidence threshold", 0.0, 1.0, 0.5)
    
    elif mode == "Document Processing":
        st.markdown("### Process Documents")
        doc_type = st.radio(
            "Document Type",
            ["PDF Files", "Text/JSON Files (Adobe Extract)", "Existing Kotaemon Data"]
        )
        
        if doc_type == "PDF Files":
            uploaded_files = st.file_uploader(
                "Choose PDF files",
                type="pdf",
                accept_multiple_files=True
            )
            
            if st.button("Process PDFs"):
                if uploaded_files:
                    processor = MedicalDocumentProcessor()
                    progress_bar = st.progress(0)
                    
                    for i, file in enumerate(uploaded_files):
                        # Save uploaded file
                        file_path = Path(f"./temp/{file.name}")
                        file_path.parent.mkdir(exist_ok=True, parents=True)
                        with open(file_path, "wb") as f:
                            f.write(file.getbuffer())
                        
                        # Process file
                        st.info(f"Processing {file.name}...")
                        extracted = processor.extract_from_pdf(file_path)
                        
                        if extracted:
                            # Add to knowledge base
                            st.session_state.chatbot.knowledge_base.add_extracted_document(extracted)
                            st.success(f"✓ Processed {file.name}")
                        else:
                            st.error(f"✗ Failed to process {file.name}")
                        
                        progress_bar.progress((i + 1) / len(uploaded_files))
                    
                    st.success("All documents processed!")
        
        elif doc_type == "Text/JSON Files (Adobe Extract)":
            directory_path = st.text_input(
                "Enter directory path containing text/JSON files",
                value="C:\\Users\\russe\\OneDrive\\backup technology\\backup light Kotaemon app data\\ktem_app_data"
            )
            
            if st.button("Process Text/JSON Files"):
                if directory_path:
                    processor = DocumentProcessor()
                    with st.spinner("Processing files..."):
                        results = processor.process_adobe_extract_files(Path(directory_path))
                    st.success(f"Processed {results['processed']} out of {results['total_files']} files")
                    if results['failed'] > 0:
                        st.warning(f"{results['failed']} files failed to process")

# Main content area
if mode == "Chat Assistant":
    # Chat interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Chat")
        
        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask about interventional pulmonology..."):
            # Add user message
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
            
            # Get bot response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = st.session_state.chatbot.answer_question(
                        prompt, 
                        include_sources=include_sources
                    )
                    
                    # Display answer
                    st.write(response['answer'])
                    
                    # Display confidence
                    if response['confidence'] >= confidence_threshold:
                        st.success(f"Confidence: {response['confidence']:.0%}")
                    else:
                        st.warning(f"Confidence: {response['confidence']:.0%}")
                    
                    # Display sources
                    if include_sources and 'sources' in response:
                        with st.expander("📚 Sources"):
                            for source in response['sources']:
                                st.markdown(f"**{source['source']}** (Relevance: {source['relevance_score']:.2f})")
                                st.text(source['text'])
            
            # Add to history
            st.session_state.chat_history.append({
                "role": "assistant", 
                "content": response['answer']
            })
    
    with col2:
        st.header("🔍 Quick Actions")
        
        # Procedure lookup
        st.subheader("Procedure Details")
        procedure_name = st.text_input("Enter procedure name")
        if st.button("Get Details"):
            if procedure_name:
                details = st.session_state.chatbot.get_procedure_details(procedure_name)
                st.json(details)
        
        # Guideline lookup
        st.subheader("Clinical Guidelines")
        condition = st.text_input("Enter condition")
        if st.button("Get Guidelines"):
            if condition:
                guidelines = st.session_state.chatbot.get_guideline_summary(condition)
                st.write(guidelines['summary'])
                st.caption(f"Sources: {', '.join(guidelines['sources'])}")

elif mode == "Knowledge Base Management":
    st.header("📊 Knowledge Base Statistics")
    
    # Get statistics
    stats = st.session_state.chatbot.knowledge_base.get_statistics()
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Documents", stats['total_chunks'])
    with col2:
        st.metric("Procedures", stats['collections'].get('procedures', 0))
    with col3:
        st.metric("Guidelines", stats['collections'].get('guidelines', 0))
    
    # Display collection details
    st.subheader("Collection Details")
    for collection_name, count in stats['collections'].items():
        st.write(f"- **{collection_name}**: {count} chunks")
    
    # Process existing data button
    if st.button("🔄 Process Existing Text/JSON Data"):
        processor = DocumentProcessor()
        with st.spinner("Processing existing data..."):
            input_articles_path = Path('./data/input_articles')
            if input_articles_path.exists():
                results = processor.process_adobe_extract_files(input_articles_path)
                st.success(f"Processed {results['processed']} files from input_articles directory")
            else:
                st.warning("No input_articles directory found. Please add your JSON files to data/input_articles/")
    
    # Clear knowledge base option
    if st.button("🗑️ Clear Knowledge Base", type="secondary"):
        if st.checkbox("Are you sure? This will delete all stored data."):
            # Reset knowledge base
            st.session_state.chatbot.knowledge_base = MedicalKnowledgeBase()
            st.success("Knowledge base cleared!")
            st.rerun()

# Footer
st.markdown("---")
st.caption("⚠️ This tool is for educational and informational purposes only. Always consult qualified healthcare providers for medical decisions.")