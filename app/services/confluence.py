from atlassian import Confluence
from loguru import logger
from typing import List, Dict, Any
import asyncio
from bs4 import BeautifulSoup

from app.core.config import Settings

class ConfluenceService:
    """Service for interacting with Confluence"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = Confluence(
            url=settings.CONFLUENCE_BASE_URL,
            token=settings.CONFLUENCE_TOKEN
        )
        
    async def crawl(self) -> List[Dict[Any, Any]]:
        """Crawl Confluence space and return processed documents"""
        try:
            space_key = self.settings.CONFLUENCE_SPACE_KEY
            pages = []
            
            if space_key:
                pages.extend(self._get_space_content(space_key))
            else:
                spaces = self.client.get_all_spaces()
                for space in spaces:
                    pages.extend(self._get_space_content(space['key']))
            
            return self._process_pages(pages)
            
        except Exception as e:
            logger.error(f"Error crawling Confluence: {str(e)}")
            raise
            
    def _get_space_content(self, space_key: str) -> List[Dict[Any, Any]]:
        """Get all content from a Confluence space"""
        try:
            pages = self.client.get_all_pages_from_space(space_key, start=0, limit=self.settings.MAX_PAGES)
            
            if self.settings.INCLUDE_ATTACHMENTS:
                for page in pages:
                    attachments = self.client.get_attachments_from_content(page['id'])
                    page['attachments'] = attachments
                    
            if self.settings.INCLUDE_COMMENTS:
                for page in pages:
                    comments = self.client.get_page_comments(page['id'])
                    page['comments'] = comments
                    
            return pages
        except Exception as e:
            logger.error(f"Error getting space content: {str(e)}")
            raise
    
    def _process_pages(self, pages: List[Dict[Any, Any]]) -> List[Dict[Any, Any]]:
        """Process Confluence pages into documents for vectorization"""
        try:
            documents = []
            
            for page in pages:
                # Get page content
                content = self.client.get_page_by_id(page['id'])
                
                # Extract text from HTML content
                html_content = content.get('body', {}).get('storage', {}).get('value', '')
                clean_text = self._clean_html(html_content)
                
                # Create document
                doc = {
                    'id': page['id'],
                    'title': page['title'],
                    'content': clean_text,
                    'space_key': page['space']['key'],
                    'url': f"{self.settings.CONFLUENCE_BASE_URL}{page['_links']['webui']}",
                    'author': page['history']['createdBy']['displayName'],
                    'last_modified': page['history']['lastUpdated']['when'],
                    'labels': [label['name'] for label in content.get('metadata', {}).get('labels', {}).get('results', [])],
                    'type': 'page'
                }
                
                # Add comments if included
                if self.settings.INCLUDE_COMMENTS and page.get('comments'):
                    comment_texts = []
                    for comment in page['comments']:
                        comment_html = comment.get('body', {}).get('storage', {}).get('value', '')
                        clean_comment = self._clean_html(comment_html)
                        comment_texts.append(clean_comment)
                    
                    doc['comments'] = comment_texts
                
                # Add attachments if included
                if self.settings.INCLUDE_ATTACHMENTS and page.get('attachments'):
                    doc['attachments'] = [{
                        'id': att['id'],
                        'title': att['title'],
                        'url': f"{self.settings.CONFLUENCE_BASE_URL}/download/attachments/{page['id']}/{att['title']}"
                    } for att in page['attachments']]
                
                documents.append(doc)
                
            return documents
            
        except Exception as e:
            logger.error(f"Error processing pages: {str(e)}")
            raise
            
    def _clean_html(self, html_content: str) -> str:
        """Clean HTML content and extract text"""
        try:
            if not html_content:
                return ""
                
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            logger.error(f"Error cleaning HTML: {str(e)}")
            raise
            
    async def get_page_content(self, page_id: str) -> Dict[Any, Any]:
        """Get content of a specific page"""
        try:
            content = self.client.get_page_by_id(page_id)
            
            if not content:
                return None
                
            # Extract text from HTML content
            html_content = content.get('body', {}).get('storage', {}).get('value', '')
            clean_text = self._clean_html(html_content)
            
            return {
                'id': content['id'],
                'title': content['title'],
                'content': clean_text,
                'space_key': content['space']['key'],
                'url': f"{self.settings.CONFLUENCE_BASE_URL}{content['_links']['webui']}",
                'author': content['history']['createdBy']['displayName'],
                'last_modified': content['history']['lastUpdated']['when']
            }
            
        except Exception as e:
            logger.error(f"Error getting page content: {str(e)}")
            raise
