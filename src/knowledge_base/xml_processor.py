"""
XML processor for Combined.xml metadata file
Extracts article metadata and enhances document processing
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

class XMLMetadataProcessor:
    """Process XML metadata for articles"""
    
    def __init__(self):
        self.articles_metadata = {}
        self.section_mapping = {
            'sec1': 'bronchoscopy',
            'sec2': 'pleural_procedures', 
            'sec3': 'guidelines',
            'sec4': 'research_studies',
            'sec5': 'emergency_procedures',
            'sec6': 'diagnostic_techniques',
            'sec7': 'therapeutic_procedures',
            'sec8': 'complications',
            'sec10': 'education_training',
            'sec11': 'case_studies'
        }
    
    def load_xml_metadata(self, xml_path: Path) -> Dict[str, Any]:
        """Load and parse XML metadata file"""
        
        if not xml_path.exists():
            print(f"XML file not found: {xml_path}")
            return {}
        
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            articles = {}
            
            for article in root.findall('.//article'):
                article_id = article.get('id', '')
                article_data = self._extract_article_data(article, article_id)
                
                if article_data:
                    articles[article_id] = article_data
            
            self.articles_metadata = articles
            print(f"Loaded metadata for {len(articles)} articles from {xml_path}")
            return articles
            
        except Exception as e:
            print(f"Error loading XML metadata: {e}")
            return {}
    
    def _extract_article_data(self, article_elem, article_id: str) -> Optional[Dict[str, Any]]:
        """Extract data from individual article element"""
        
        try:
            # Basic metadata
            title = self._get_text(article_elem, 'title')
            authors = self._get_text(article_elem, 'authors')
            citation = self._get_text(article_elem, 'citation')
            doc_type = self._get_text(article_elem, 'type')
            year = self._get_text(article_elem, 'year')
            
            # Keywords
            keywords = []
            keywords_elem = article_elem.find('keywords')
            if keywords_elem is not None:
                for keyword_elem in keywords_elem.findall('keyword'):
                    keywords.append(keyword_elem.text.strip())
            
            # Summary and content
            summary = self._get_text(article_elem, 'summary')
            take_home = self._get_text(article_elem, 'take_home')
            
            # PICO framework
            pico = {}
            pico_elem = article_elem.find('pico')
            if pico_elem is not None:
                pico = {
                    'population': self._get_text(pico_elem, 'population'),
                    'intervention': self._get_text(pico_elem, 'intervention'),
                    'comparison': self._get_text(pico_elem, 'comparison'),
                    'outcome': self._get_text(pico_elem, 'outcome')
                }
            
            # Determine section/category
            section = self._determine_section(article_id)
            
            return {
                'id': article_id,
                'title': title,
                'authors': authors,
                'citation': citation,
                'type': doc_type,
                'year': year,
                'keywords': keywords,
                'summary': summary,
                'take_home': take_home,
                'pico': pico,
                'section': section,
                'category': self.section_mapping.get(section, 'general')
            }
            
        except Exception as e:
            print(f"Error extracting article data for {article_id}: {e}")
            return None
    
    def _get_text(self, parent_elem, tag_name: str) -> str:
        """Safely extract text from XML element"""
        elem = parent_elem.find(tag_name)
        return elem.text.strip() if elem is not None and elem.text else ""
    
    def _determine_section(self, article_id: str) -> str:
        """Determine section from article ID"""
        if '_' in article_id:
            section_part = article_id.split('_')[0]
            return section_part
        return 'general'
    
    def get_article_metadata(self, article_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for specific article"""
        return self.articles_metadata.get(article_id)
    
    def find_articles_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Find articles containing specific keyword"""
        keyword_lower = keyword.lower()
        matches = []
        
        for article_id, metadata in self.articles_metadata.items():
            # Check title, keywords, summary
            if (keyword_lower in metadata.get('title', '').lower() or
                keyword_lower in metadata.get('summary', '').lower() or
                any(keyword_lower in k.lower() for k in metadata.get('keywords', []))):
                matches.append(metadata)
        
        return matches
    
    def find_articles_by_section(self, section: str) -> List[Dict[str, Any]]:
        """Find articles in specific section"""
        section_key = f'sec{section}' if not section.startswith('sec') else section
        return [metadata for metadata in self.articles_metadata.values() 
                if metadata.get('section') == section_key]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about loaded metadata"""
        if not self.articles_metadata:
            return {}
        
        stats = {
            'total_articles': len(self.articles_metadata),
            'sections': {},
            'types': {},
            'years': {},
            'keywords': {}
        }
        
        for metadata in self.articles_metadata.values():
            # Section stats
            section = metadata.get('section', 'unknown')
            stats['sections'][section] = stats['sections'].get(section, 0) + 1
            
            # Type stats
            doc_type = metadata.get('type', 'unknown')
            stats['types'][doc_type] = stats['types'].get(doc_type, 0) + 1
            
            # Year stats
            year = metadata.get('year', 'unknown')
            stats['years'][year] = stats['years'].get(year, 0) + 1
            
            # Keyword stats
            for keyword in metadata.get('keywords', []):
                stats['keywords'][keyword] = stats['keywords'].get(keyword, 0) + 1
        
        return stats
    
    def enhance_document_processing(self, extracted_data: Dict[str, Any], filename: str) -> Dict[str, Any]:
        """Enhance extracted data with XML metadata"""
        
        # Try to find matching article by title or filename
        matching_metadata = self._find_matching_article(extracted_data, filename)
        
        if matching_metadata:
            # Enhance metadata
            if 'metadata' not in extracted_data:
                extracted_data['metadata'] = {}
            
            extracted_data['metadata'].update({
                'xml_metadata': matching_metadata,
                'article_id': matching_metadata.get('id'),
                'publication_year': matching_metadata.get('year'),
                'document_type': matching_metadata.get('type'),
                'authors': matching_metadata.get('authors'),
                'citation': matching_metadata.get('citation'),
                'keywords': matching_metadata.get('keywords', []),
                'section': matching_metadata.get('section'),
                'category': matching_metadata.get('category'),
                'pico_framework': matching_metadata.get('pico', {}),
                'take_home_message': matching_metadata.get('take_home'),
                'summary': matching_metadata.get('summary')
            })
            
            # Add keywords to medical concepts if available
            if 'medical_concepts' not in extracted_data:
                extracted_data['medical_concepts'] = {}
            
            if matching_metadata.get('keywords'):
                if 'keywords' not in extracted_data['medical_concepts']:
                    extracted_data['medical_concepts']['keywords'] = []
                extracted_data['medical_concepts']['keywords'].extend(matching_metadata['keywords'])
        
        return extracted_data
    
    def _find_matching_article(self, extracted_data: Dict[str, Any], filename: str) -> Optional[Dict[str, Any]]:
        """Find matching article metadata by title or filename"""
        
        # Try to match by title first
        if 'metadata' in extracted_data and 'title' in extracted_data['metadata']:
            title = extracted_data['metadata']['title']
            for metadata in self.articles_metadata.values():
                if metadata.get('title', '').lower() in title.lower() or title.lower() in metadata.get('title', '').lower():
                    return metadata
        
        # Try to match by filename
        filename_lower = filename.lower()
        for metadata in self.articles_metadata.values():
            title_lower = metadata.get('title', '').lower()
            # Check if filename contains key words from title
            title_words = [word for word in title_lower.split() if len(word) > 3]
            if any(word in filename_lower for word in title_words):
                return metadata
        
        return None
