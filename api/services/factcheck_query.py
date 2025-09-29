"""Dynamic query building for fact-check API requests."""

import re
from typing import Dict, List, Optional


def extract_claim_sentences(summary: str, max_claims: int = 3) -> List[str]:
    """Extract top claim sentences from summary text."""
    if not summary or not summary.strip():
        return []
    
    sentences = re.split(r'[.!?]+', summary)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    filtered_sentences = []
    for sentence in sentences:
        word_count = len(sentence.split())
        if 8 <= word_count <= 35:
            filtered_sentences.append(sentence)
    
    scored_sentences = []
    for sentence in filtered_sentences:
        score = 0
        
        word_count = len(sentence.split())
        if 12 <= word_count <= 25:
            score += 2
        elif 8 <= word_count <= 30:
            score += 1
        
        if re.search(r'\b(is|are|was|were|has|have|had|will|would|could|should|says|said|reports|reported|claims|claimed)\b', sentence.lower()):
            score += 1
        
        proper_nouns = re.findall(r'\b[A-Z][a-z]+\b', sentence)
        if len(proper_nouns) > 1:
            score += len(proper_nouns) * 0.5
        
        if re.search(r'\b\d+%|\$\d+|\b\d{4}\b', sentence):
            score += 1
        
        scored_sentences.append((sentence, score))
    
    scored_sentences.sort(key=lambda x: x[1], reverse=True)
    return [sentence for sentence, _ in scored_sentences[:max_claims]]


def extract_keyphrases(text: str, max_phrases: int = 6) -> List[str]:
    """Extract meaningful keyphrases using dynamic TF-IDF-like scoring."""
    if not text or not text.strip():
        return []
    
    stop_words = {
        'the', 'and', 'but', 'for', 'are', 'was', 'were', 'been', 'have', 'has', 
        'this', 'that', 'with', 'from', 'they', 'them', 'will', 'would'
    }
    
    words = [w.lower().strip('.,!?";:()[]') for w in text.split()]
    words = [w for w in words if w and len(w) > 2 and not w.isdigit()]
    
    word_freq = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    word_scores = {}
    for word in word_freq:
        score = 0
        score += min(len(word) - 2, 4)
        if word_freq[word] > 2:
            score -= 1
        if word in stop_words:
            score -= 5
        if any(w.istitle() for w in text.split() if w.lower().strip('.,!?";:()[]') == word):
            score += 3
        
        word_scores[word] = score
    
    phrases = []
    
    for word, score in word_scores.items():
        if score > 0:
            phrases.append((word, score))
    
    for i in range(len(words) - 1):
        if words[i] not in stop_words and words[i+1] not in stop_words:
            phrase = f"{words[i]} {words[i+1]}"
            score = word_scores.get(words[i], 0) + word_scores.get(words[i+1], 0) + 2
            phrases.append((phrase, score))
    
    for i in range(len(words) - 2):
        if all(word not in stop_words for word in words[i:i+3]):
            phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
            score = sum(word_scores.get(w, 0) for w in words[i:i+3]) + 3
            if score > 6:
                phrases.append((phrase, score))
    
    phrases.sort(key=lambda x: x[1], reverse=True)
    return [phrase for phrase, _ in phrases[:max_phrases]]


def extract_entities_cheap(text: str) -> List[str]:
    """Simple entity extraction using capitalization patterns."""
    if not text or not text.strip():
        return []
    
    entities = []
    
    multi_word = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', text)
    entities.extend(multi_word)
    
    words = text.split()
    for i, word in enumerate(words):
        if (i > 0 and 
            re.match(r'^[A-Z][a-z]{2,}$', word) and 
            word not in {'This', 'That', 'They', 'There', 'Then', 'When', 'Where', 'What', 'Which'}):
            entities.append(word)
    
    numbers = re.findall(r'\b\d+(?:[.,]\d+)*\s*(?:%|percent|billion|million|thousand)\b|\$\d+|\b(?:19|20)\d{2}\b', text, re.IGNORECASE)
    entities.extend(numbers)
    
    cleaned = []
    for entity in entities:
        if isinstance(entity, str) and len(entity.strip()) > 1:
            entity_clean = entity.strip()
            if not any(skip in entity_clean.lower() for skip in ['by ', 'published', 'updated']):
                cleaned.append(entity_clean)
    
    return list(dict.fromkeys(cleaned))[:8]


def expand_with_aliases(tokens: List[str]) -> List[str]:
    """Simple expansion with common variations."""
    if not tokens:
        return []
    
    expanded = set(tokens)
    
    for token in tokens:
        token_lower = token.lower().strip()
        
        if token_lower.endswith('eds') and len(token_lower) > 5:
            fixed_word = token_lower[:-1]
            expanded.add(fixed_word)
        elif token_lower.endswith('s') and len(token_lower) > 3:
            expanded.add(token_lower[:-1])
        elif not token_lower.endswith('s') and not token_lower.endswith('ed'):
            expanded.add(token_lower + 's')
        
        if len(token_lower) > 4:
            words = token_lower.split()
            if len(words) > 1:
                acronym = ''.join(w[0] for w in words if w)
                if len(acronym) > 1:
                    expanded.add(acronym)
    
    filtered = [token for token in expanded if len(token) > 2 and 
                token.lower() not in {'the', 'and', 'or', 'but', 'for', 'with'}]
    
    unique_filtered = list(dict.fromkeys(filtered))
    return unique_filtered[:6]


def build_queries(headline: str, source_domain: Optional[str] = None, summary: Optional[str] = None) -> List[Dict[str, str]]:
    """Build targeted fact-check queries using dynamic, domain-agnostic approach."""
    queries = []
    
    headline_entities = extract_entities_cheap(headline)
    headline_keyphrases = extract_keyphrases(headline)
    
    if not headline_entities:
        words = headline.split()
        for word in words:
            clean_word = word.strip('.,!?";:()[]')
            if (clean_word and clean_word[0].isupper() and len(clean_word) > 2 and
                clean_word not in {'The', 'This', 'That', 'And', 'But', 'For'}):
                headline_entities.append(clean_word)
    
    if headline_entities and headline_keyphrases:
        top_entity = headline_entities[0]
        top_keyphrase = headline_keyphrases[0]
        
        entity_words = set(top_entity.lower().split())
        keyphrase_words = [w for w in top_keyphrase.split() if w.lower() not in entity_words]
        
        if keyphrase_words:
            clean_keyphrase = " ".join(keyphrase_words)
            queries.append({"reason": "headline_entity_keyphrase", "q": f"{top_entity} {clean_keyphrase}"})
    
    queries.append({"reason": "headline_exact", "q": f'"{headline[:70]}"'})
    
    if len(headline_entities) >= 2:
        entity1, entity2 = headline_entities[0], headline_entities[1]
        if entity1.lower() != entity2.lower():
            queries.append({"reason": "top_entities", "q": f"{entity1} {entity2}"})
    
    if len(headline_keyphrases) >= 2:
        queries.append({"reason": "top_keyphrases", "q": f"{headline_keyphrases[0]} {headline_keyphrases[1]}"})
    
    if summary and summary.strip():
        summary_keyphrases = extract_keyphrases(summary)
        if summary_keyphrases:
            all_words = []
            seen_words = set()
            
            for phrase in summary_keyphrases[:4]:
                for word in phrase.split():
                    word_lower = word.lower()
                    if word_lower not in seen_words and len(word) > 3:
                        all_words.append(word)
                        seen_words.add(word_lower)
            
            if len(all_words) >= 2:
                queries.append({"reason": "summary_topics", "q": " ".join(all_words[:3])})
    
    meaningful_words = []
    for word in headline.split():
        word_clean = word.lower().strip('.,!?";:()[]')
        if (len(word_clean) > 3 and 
            word_clean not in {'this', 'that', 'they', 'them', 'with', 'from', 'have', 'been', 'were', 'will', 'said', 'says', 'make', 'made'}):
            meaningful_words.append(word_clean)
    
    if len(meaningful_words) >= 2:
        queries.append({"reason": "headline_core", "q": " ".join(meaningful_words[:3])})
    
    for entity in headline_entities[:2]:
        if len(entity) > 2:
            queries.append({"reason": "single_entity", "q": entity})
    
    headline_words = headline.lower().split()
    important_single_words = [w.strip('.,!?";:()[]') for w in headline_words if len(w) > 5]
    if important_single_words:
        queries.append({"reason": "key_topic", "q": important_single_words[0]})
    
    clean_words = [w.strip('.,!?";:()[]').lower() for w in headline.split() 
                   if len(w) > 3 and w.lower() not in {'this', 'that', 'with', 'from', 'have', 'been'}]
    if len(clean_words) >= 2:
        queries.append({"reason": "word_pair", "q": f"{clean_words[0]} {clean_words[-1]}"})
    
    if headline_entities and summary:
        summary_keyphrases = extract_keyphrases(summary)
        if summary_keyphrases:
            best_topic = None
            best_score = 0
            
            for keyphrase in summary_keyphrases[:3]:
                words = keyphrase.split()
                score = 0
                
                score += len(words)
                score += sum(len(word) for word in words) / len(words)
                
                if not any(word.endswith(('ing', 'ed', 'ly', 's')) for word in words):
                    score += 2
                
                if score > best_score:
                    best_score = score
                    best_topic = keyphrase
            
            if best_topic:
                entity = headline_entities[0]
                
                entity_words = set(entity.lower().split())
                topic_words = [w for w in best_topic.split() if w.lower() not in entity_words]
                
                if topic_words:
                    clean_topic = " ".join(topic_words)
                    queries.append({"reason": "entity_topic", "q": f"{entity} {clean_topic}"})
                
                if len(headline_entities) >= 2:
                    entity1, entity2 = headline_entities[0], headline_entities[1]
                    if entity1.lower() != entity2.lower():
                        queries.append({"reason": "dual_entities", "q": f"{entity1} {entity2}"})
    
    valid_queries = []
    seen_normalized = set()
    
    for query_dict in queries:
        query = query_dict.get("q", "").strip()
        
        if not query or len(query) < 6 or len(query.split()) < 2:
            continue
        
        normalized = query.replace('"', '').lower().strip()
        
        is_duplicate = False
        normalized_words = set(normalized.split())
        
        for seen in seen_normalized:
            seen_words = set(seen.split())
            if len(normalized_words) > 0 and len(seen_words) > 0:
                overlap = len(normalized_words & seen_words)
                similarity = overlap / min(len(normalized_words), len(seen_words))
                if similarity > 0.75:
                    is_duplicate = True
                    break
        
        if not is_duplicate:
            valid_queries.append(query_dict)
            seen_normalized.add(normalized)
    
    return valid_queries[:8]