"""
Semantic search functionality for email content using local embeddings.
Uses sentence-transformers with all-MiniLM-L6-v2 model for local processing.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import warnings
import re
import html

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

class SemanticSearchEngine:
    def __init__(self, model_name='all-mpnet-base-v2', similarity_threshold=0.1):
        """
        Initialize the semantic search engine with a local embedding model.
        
        Args:
            model_name (str): Name of the sentence-transformers model to use
            similarity_threshold (float): Minimum similarity score to include in results
        """
        try:
            self.model = SentenceTransformer(model_name)
            self.model_name = model_name
        except Exception:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.model_name = 'all-MiniLM-L6-v2'
        self.similarity_threshold = similarity_threshold
    
    def clean_email_body(self, body):
        """
        Clean email body content for better embedding quality.
        
        Args:
            body (str): Raw email body content
            
        Returns:
            str: Cleaned email body
        """
        if not body:
            return ""
        
        # Convert to string if not already
        text = str(body)
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ' ', text)
        
        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', ' ', text)
        
        # Remove excessive whitespace and line breaks
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common email footers and signatures
        text = re.sub(r'(unsubscribe|privacy policy|terms of service|\bsent from\b|\bbest regards\b|\bsincerely\b).*', '', text, flags=re.IGNORECASE)
        
        # Remove quoted text (lines starting with >)
        lines = text.split('\n')
        cleaned_lines = [line for line in lines if not line.strip().startswith('>')]
        text = ' '.join(cleaned_lines)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:\-\'"()]', ' ', text)
        
        # Final cleanup: remove extra spaces and trim
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Limit length to avoid very long embeddings (keep first 500 characters)
        if len(text) > 500:
            text = text[:500] + "..."
        
        return text
    
    def create_email_embedding(self, email_data):
        """
        Create an embedding for an email by combining subject and body.
        
        Args:
            email_data (dict): Email data with 'subject' and 'body' keys
            
        Returns:
            np.ndarray: Normalized embedding vector
        """
        # Get and clean subject and body
        subject = email_data.get('subject', '').strip()
        # Use full_body if available, otherwise fall back to body
        body = email_data.get('full_body', email_data.get('body', ''))
        
        # Clean the email body
        cleaned_body = self.clean_email_body(body)
        
        # Create combined text with weighted subject
        combined_text = f"{subject} {subject} {cleaned_body}"
        
        # Handle empty content
        if not combined_text.strip():
            combined_text = "empty email"
        
        # Generate embedding
        embedding = self.model.encode(combined_text, convert_to_tensor=False)
        return embedding / np.linalg.norm(embedding)  # Return normalized embedding
    
    def create_query_embedding(self, query):
        """
        Create an embedding for a search query.
        
        Args:
            query (str): Search query text
            
        Returns:
            np.ndarray: Normalized embedding vector
        """
        embedding = self.model.encode(query, convert_to_tensor=False)
        return embedding / np.linalg.norm(embedding)  # Return normalized embedding
    
    def compute_similarity(self, query_embedding, email_embeddings):
        """
        Compute cosine similarity between query and email embeddings.
        
        Args:
            query_embedding (np.ndarray): Query embedding vector
            email_embeddings (list): List of email embedding vectors
            
        Returns:
            np.ndarray: Similarity scores
        """
        if not email_embeddings:
            return np.array([])
        
        # Stack email embeddings into matrix
        email_matrix = np.vstack(email_embeddings)
        
        # Compute cosine similarity (both embeddings are already normalized)
        similarities = np.dot(email_matrix, query_embedding)
        
        return similarities
    
    def semantic_search(self, query, emails, top_k=5, min_threshold=None):
        """
        Perform semantic search on a list of emails.
        
        Args:
            query (str): Search query
            emails (list): List of email dictionaries
            top_k (int): Number of top results to return
            min_threshold (float): Override default similarity threshold
            
        Returns:
            list: List of tuples (email, similarity_score) sorted by relevance
        """
        if not emails:
            return []
        
        # Use provided threshold or default
        threshold = min_threshold if min_threshold is not None else self.similarity_threshold
        
        # Create query embedding
        query_embedding = self.create_query_embedding(query)
        
        # Create embeddings for all emails
        email_embeddings = [self.create_email_embedding(email) for email in emails]
        
        # Compute similarities
        similarities = self.compute_similarity(query_embedding, email_embeddings)
        
        # Combine emails with their similarity scores
        email_scores = list(zip(emails, similarities))
        
        # Filter by similarity threshold
        filtered_scores = [(email, score) for email, score in email_scores if score >= threshold]
        
        if not filtered_scores:
            # Return top result anyway if no matches above threshold
            email_scores.sort(key=lambda x: x[1], reverse=True)
            return email_scores[:1] if email_scores else []
        
        # Sort by similarity score (descending)
        filtered_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top-k results
        return filtered_scores[:top_k]
    
    def search_with_threshold(self, query, emails, threshold=0.3, top_k=10):
        """
        Perform semantic search with a similarity threshold.
        
        Args:
            query (str): Search query
            emails (list): List of email dictionaries
            threshold (float): Minimum similarity threshold (0-1)
            top_k (int): Maximum number of results to return
            
        Returns:
            list: List of tuples (email, similarity_score) above threshold
        """
        results = self.semantic_search(query, emails, top_k=len(emails))
        
        # Filter by threshold
        filtered_results = [(email, score) for email, score in results if score >= threshold]
        
        # Return top-k results
        return filtered_results[:top_k]


# Global instance to avoid reloading model
_semantic_engine = None

def get_semantic_engine():
    """
    Get or create the global semantic search engine instance.
    
    Returns:
        SemanticSearchEngine: The semantic search engine instance
    """
    global _semantic_engine
    if _semantic_engine is None:
        _semantic_engine = SemanticSearchEngine()
    return _semantic_engine


def semantic_search_emails(imap_host, email_user, email_pass, query, folder="INBOX", top_k=5, min_threshold=None):
    """
    Convenience function to perform semantic search on emails from IMAP.
    
    Args:
        imap_host (str): IMAP server host
        email_user (str): Email username
        email_pass (str): Email password
        query (str): Search query
        folder (str): Email folder to search in
        top_k (int): Number of top results to return
        min_threshold (float): Minimum similarity threshold
        
    Returns:
        list: List of email dictionaries ranked by semantic similarity
    """
    from imap_client import fetch_all_emails
    
    # Fetch all emails
    emails = fetch_all_emails(imap_host, email_user, email_pass, folder)
    
    if not emails:
        return []
    
    # Get semantic search engine
    engine = get_semantic_engine()
    
    # Perform semantic search
    results = engine.semantic_search(query, emails, top_k=top_k, min_threshold=min_threshold)
    
    # Return just the emails (without similarity scores for now)
    return [email for email, score in results]


def semantic_search_with_scores(imap_host, email_user, email_pass, query, folder="INBOX", top_k=5, min_threshold=None):
    """
    Convenience function to perform semantic search and return results with similarity scores.
    
    Args:
        imap_host (str): IMAP server host
        email_user (str): Email username
        email_pass (str): Email password
        query (str): Search query
        folder (str): Email folder to search in
        top_k (int): Number of top results to return
        min_threshold (float): Minimum similarity threshold
        
    Returns:
        list: List of tuples (email, similarity_score) ranked by semantic similarity
    """
    from imap_client import fetch_all_emails
    
    # Fetch all emails
    emails = fetch_all_emails(imap_host, email_user, email_pass, folder)
    
    if not emails:
        return []
    
    # Get semantic search engine
    engine = get_semantic_engine()
    
    # Perform semantic search
    return engine.semantic_search(query, emails, top_k=top_k, min_threshold=min_threshold)
