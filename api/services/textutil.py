import re
from typing import List, Set, Dict
from collections import Counter

class TextUtil:
    
    def __init__(self):
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'or', 'but', 'not', 'this', 'they',
            'them', 'their', 'we', 'our', 'us', 'you', 'your', 'have', 'had',
            'do', 'does', 'did', 'can', 'could', 'would', 'should', 'may',
            'might', 'must', 'shall', 'about', 'after', 'all', 'also',
            'any', 'because', 'been', 'before', 'being', 'between', 'both',
            'each', 'few', 'more', 'most', 'other', 'some', 'such', 'than',
            'too', 'very', 'what', 'when', 'where', 'which', 'who', 'why'
        }
    
    def normalize_text(self, text: str) -> str:
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def tokenize(self, text: str, min_length: int = 3) -> List[str]:
        normalized = self.normalize_text(text)
        tokens = normalized.split()
        return [t for t in tokens if len(t) >= min_length and t not in self.stop_words]
    
    def extract_tokens_set(self, text: str, min_length: int = 3) -> Set[str]:
        return set(self.tokenize(text, min_length))
    
    def jaccard_similarity(self, text1: str, text2: str) -> float:
        tokens1 = self.extract_tokens_set(text1)
        tokens2 = self.extract_tokens_set(text2)
        
        if not tokens1 and not tokens2:
            return 1.0
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = len(tokens1.intersection(tokens2))
        union = len(tokens1.union(tokens2))
        
        return intersection / union if union > 0 else 0.0
    
    def ngram_jaccard_similarity(self, text1: str, text2: str, n: int = 2) -> float:
        def get_ngrams(text: str, n: int) -> Set[str]:
            tokens = self.tokenize(text)
            if len(tokens) < n:
                return set(tokens)
            
            ngrams = set()
            for i in range(len(tokens) - n + 1):
                ngram = ' '.join(tokens[i:i+n])
                ngrams.add(ngram)
            return ngrams
        
        ngrams1 = get_ngrams(text1, n)
        ngrams2 = get_ngrams(text2, n)
        
        if not ngrams1 and not ngrams2:
            return 1.0
        if not ngrams1 or not ngrams2:
            return 0.0
        
        intersection = len(ngrams1.intersection(ngrams2))
        union = len(ngrams1.union(ngrams2))
        
        return intersection / union if union > 0 else 0.0
    
    def extract_numbers_with_units(self, text: str) -> List[Dict[str, str]]:
        patterns = [
            r'(\d+(?:\.\d+)?)\s*%',
            r'(\d+(?:\.\d+)?)\s*percent',
            r'\$(\d+(?:[.,]\d+)*)\s*(million|billion|trillion|thousand)?',
            r'(\d+(?:[.,]\d+)*)\s*(million|billion|trillion|thousand|cases|votes|people|dollars|per\s+day|per\s+year)',
            r'\b(19|20)(\d{2})\b',
            r'(\d+(?:[.,]\d+)*)\s+([a-zA-Z]+)',
        ]
        
        results = []
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 2:
                    number = match.group(1)
                    unit = match.group(2) if match.group(2) else ""
                    results.append({"number": number, "unit": unit, "full": match.group(0)})
                else:
                    results.append({"number": match.group(0), "unit": "", "full": match.group(0)})
        
        return results
    
    def extract_entities(self, text: str) -> List[str]:
        """Extract potential entities (capitalized words, organizations, etc.)."""
        # Multi-word capitalized phrases
        multi_word = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', text)
        
        # Single capitalized words (excluding sentence starters)
        words = text.split()
        single_words = []
        for i, word in enumerate(words):
            if (i > 0 and  # Not sentence start
                re.match(r'^[A-Z][a-z]{2,}$', word) and 
                word not in {'This', 'That', 'They', 'There', 'Then', 'When', 'Where', 'What', 'Which'}):
                single_words.append(word)
        
        entities = multi_word + single_words
        
        seen = set()
        unique_entities = []
        for entity in entities:
            if entity.lower() not in seen:
                seen.add(entity.lower())
                unique_entities.append(entity)
        
        return unique_entities[:10]


text_util = TextUtil()