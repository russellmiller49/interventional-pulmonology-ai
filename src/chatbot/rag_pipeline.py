import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import openai
from dotenv import load_dotenv
from ..knowledge_base.vector_store import MedicalKnowledgeBase

load_dotenv()

class InterventionalPulmonologyBot:
    """RAG-based chatbot for interventional pulmonology"""
    
    def __init__(self):
        self.knowledge_base = MedicalKnowledgeBase()
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.conversation_history = []
        
    def answer_question(self, question: str, include_sources: bool = True) -> Dict[str, Any]:
        """Answer a medical question using RAG"""
        
        # Search knowledge base
        search_results = self.knowledge_base.search(question, n_results=5)
        
        # Build context from search results
        context = self.build_context(search_results)
        
        # Generate response
        response = self.generate_response(question, context)
        
        # Add to conversation history
        self.conversation_history.append({
            'question': question,
            'answer': response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Format final response
        result = {
            'answer': response,
            'confidence': self.calculate_confidence(search_results),
            'timestamp': datetime.now().isoformat()
        }
        
        if include_sources:
            result['sources'] = [
                {
                    'text': r['text'][:200] + '...',
                    'source': r['metadata'].get('source', 'Unknown'),
                    'relevance_score': 1 - r['distance']
                }
                for r in search_results[:3]
            ]
        
        return result
    
    def build_context(self, search_results: List[Dict]) -> str:
        """Build context from search results"""
        
        context_parts = []
        
        for result in search_results:
            source = result['metadata'].get('source', 'Unknown')
            text = result['text']
            context_parts.append(f"[Source: {source}]\n{text}\n")
        
        return "\n---\n".join(context_parts)
    
    def generate_response(self, question: str, context: str) -> str:
        """Generate response using OpenAI"""
        
        system_prompt = """You are an expert interventional pulmonologist assistant. 
        You provide accurate, evidence-based information about bronchoscopy, pleural procedures, 
        airway management, and related interventional pulmonology topics.
        
        Guidelines:
        1. Base your answers on the provided context
        2. Be specific with procedural details, measurements, and dosages
        3. Mention contraindications and complications when relevant
        4. Use medical terminology appropriately
        5. If information is not in the context, state that clearly
        6. Always emphasize that this is for educational purposes and not medical advice
        
        Important: This is for educational and informational purposes only. 
        Always consult with qualified healthcare providers for medical decisions."""
        
        user_prompt = f"""Context:\n{context}\n\nQuestion: {question}\n\n
        Please provide a comprehensive answer based on the context provided."""
        
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    
    def calculate_confidence(self, search_results: List[Dict]) -> float:
        """Calculate confidence score based on search results"""
        
        if not search_results:
            return 0.0
        
        # Calculate based on distances (lower is better)
        distances = [r['distance'] for r in search_results]
        avg_distance = sum(distances) / len(distances)
        
        # Convert to confidence (0-1 scale)
        confidence = max(0, 1 - avg_distance)
        
        return round(confidence, 2)
    
    def get_procedure_details(self, procedure_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific procedure"""
        
        # Search specifically in procedures collection
        results = self.knowledge_base.search(
            procedure_name, 
            collection_name='procedures',
            n_results=10
        )
        
        # Compile procedure information
        procedure_info = {
            'name': procedure_name,
            'details': {},
            'sources': []
        }
        
        for result in results:
            metadata = result['metadata']
            chunk_type = metadata.get('chunk_type')
            
            if chunk_type == 'overview':
                procedure_info['details']['overview'] = result['text']
            elif chunk_type == 'technique':
                procedure_info['details']['technique'] = result['text']
            elif chunk_type == 'complications':
                procedure_info['details']['complications'] = result['text']
            
            procedure_info['sources'].append(metadata.get('source'))
        
        return procedure_info
    
    def get_guideline_summary(self, condition: str) -> Dict[str, Any]:
        """Get guideline summary for a condition"""
        
        # Search in guidelines collection
        results = self.knowledge_base.search(
            condition,
            collection_name='guidelines',
            n_results=5
        )
        
        if results:
            context = self.build_context(results)
            summary = self.generate_response(
                f"Provide a clinical guideline summary for {condition}",
                context
            )
            
            return {
                'condition': condition,
                'summary': summary,
                'sources': [r['metadata'].get('source') for r in results]
            }
        
        return {
            'condition': condition,
            'summary': "No guidelines found for this condition",
            'sources': []
        }