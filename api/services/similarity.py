"""
Text similarity calculation service for fact-check matching.
Uses multiple algorithms to compute accurate similarity scores.
"""

import re
import math
from typing import List, Dict, Set, Tuple
from collections import Counter
import unicodedata


class SimilarityCalculator:
    """Calculates text similarity using multiple algorithms."""
    
    def __init__(self):
        # Common stop words to filter out
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'or', 'but', 'not', 'this', 'they',
            'them', 'their', 'we', 'our', 'us', 'you', 'your', 'have', 'had',
            'do', 'does', 'did', 'can', 'could', 'would', 'should', 'may',
            'might', 'must', 'shall', 'will', 'about', 'after', 'all', 'also',
            'any', 'because', 'been', 'before', 'being', 'between', 'both',
            'each', 'few', 'more', 'most', 'other', 'some', 'such', 'than',
            'too', 'very', 'what', 'when', 'where', 'which', 'who', 'why'
        }
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove accents and diacritics
        text = unicodedata.normalize('NFD', text)
        text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
        
        # Remove punctuation and extra whitespace
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_keywords(self, text: str) -> Set[str]:
        """Extract meaningful keywords from text."""
        normalized = self.normalize_text(text)
        words = normalized.split()
        
        # Filter out stop words and very short words
        keywords = {
            word for word in words 
            if len(word) > 2 and word not in self.stop_words
        }
        
        return keywords
    
    def jaccard_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity between two texts."""
        words1 = self.extract_keywords(text1)
        words2 = self.extract_keywords(text2)
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def cosine_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts."""
        words1 = self.normalize_text(text1).split()
        words2 = self.normalize_text(text2).split()
        
        if not words1 or not words2:
            return 0.0
        
        # Create word frequency vectors
        all_words = set(words1 + words2)
        vector1 = [words1.count(word) for word in all_words]
        vector2 = [words2.count(word) for word in all_words]
        
        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(vector1, vector2))
        
        # Calculate magnitudes
        magnitude1 = math.sqrt(sum(a * a for a in vector1))
        magnitude2 = math.sqrt(sum(a * a for a in vector2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def levenshtein_similarity(self, text1: str, text2: str) -> float:
        """Calculate normalized Levenshtein (edit distance) similarity."""
        s1 = self.normalize_text(text1)
        s2 = self.normalize_text(text2)
        
        if s1 == s2:
            return 1.0
        
        len1, len2 = len(s1), len(s2)
        if len1 == 0 or len2 == 0:
            return 0.0
        
        # Dynamic programming matrix for edit distance
        matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        
        # Initialize first row and column
        for i in range(len1 + 1):
            matrix[i][0] = i
        for j in range(len2 + 1):
            matrix[0][j] = j
        
        # Fill the matrix
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                cost = 0 if s1[i-1] == s2[j-1] else 1
                matrix[i][j] = min(
                    matrix[i-1][j] + 1,      # deletion
                    matrix[i][j-1] + 1,      # insertion
                    matrix[i-1][j-1] + cost  # substitution
                )
        
        edit_distance = matrix[len1][len2]
        max_len = max(len1, len2)
        
        return 1.0 - (edit_distance / max_len) if max_len > 0 else 0.0
    
    def semantic_overlap(self, text1: str, text2: str) -> float:
        """Calculate semantic overlap based on important entities and concepts."""
        # Extract potential entities (capitalized words, numbers, dates)
        entities1 = self.extract_entities(text1)
        entities2 = self.extract_entities(text2)
        
        if not entities1 and not entities2:
            return 0.0
        if not entities1 or not entities2:
            return 0.0
        
        # Calculate overlap of entities
        common_entities = len(entities1.intersection(entities2))
        total_entities = len(entities1.union(entities2))
        
        return common_entities / total_entities if total_entities > 0 else 0.0
    
    def extract_entities(self, text: str) -> Set[str]:
        """Extract potential entities from text (names, places, organizations, etc.)."""
        normalized = self.normalize_text(text)
        
        # Find capitalized words, numbers, and potential entities
        entities = set()
        
        # Capitalized words (potential proper nouns)
        cap_words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        entities.update(word.lower() for word in cap_words)
        
        # Numbers and dates
        numbers = re.findall(r'\b\d+(?:[.,]\d+)*\b', text)
        entities.update(numbers)
        
        # Years
        years = re.findall(r'\b(?:19|20)\d{2}\b', text)
        entities.update(years)
        
        return entities
    
    def calculate_similarity(self, headline: str, summary: str, claim: str) -> Dict[str, float]:
        """
        Calculate comprehensive similarity between article content and fact-check claim.
        
        Args:
            headline: Article headline
            summary: Article summary (optional)
            claim: Fact-check claim
            
        Returns:
            Dict with similarity scores and overall score
        """
        # Combine headline and summary for comparison
        article_text = headline
        if summary:
            article_text += " " + summary
        
        # Calculate multiple similarity metrics
        jaccard_score = self.jaccard_similarity(article_text, claim)
        cosine_score = self.cosine_similarity(article_text, claim)
        levenshtein_score = self.levenshtein_similarity(article_text, claim)
        semantic_score = self.semantic_overlap(article_text, claim)
        
        # Also check headline-only similarity for highly relevant matches
        headline_jaccard = self.jaccard_similarity(headline, claim)
        headline_cosine = self.cosine_similarity(headline, claim)
        
        # Weighted combination of scores
        # Higher weight for semantic overlap and headline matches
        overall_score = (
            jaccard_score * 0.25 +
            cosine_score * 0.25 +
            levenshtein_score * 0.15 +
            semantic_score * 0.20 +
            headline_jaccard * 0.10 +
            headline_cosine * 0.05
        )
        
        # Convert to percentage
        overall_percentage = min(99, max(1, int(overall_score * 100)))
        
        return {
            "overall_score": overall_percentage,
            "jaccard_similarity": round(jaccard_score, 3),
            "cosine_similarity": round(cosine_score, 3),
            "levenshtein_similarity": round(levenshtein_score, 3),
            "semantic_overlap": round(semantic_score, 3),
            "headline_match": round(max(headline_jaccard, headline_cosine), 3)
        }


# Global instance
similarity_calculator = SimilarityCalculator()