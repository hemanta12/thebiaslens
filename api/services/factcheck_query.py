import re
from typing import Dict, List, Optional
from .claims import claim_miner
from .textutil import text_util

def derive_core_claim(headline: str, summary: Optional[str] = None) -> str:
    core_claims = claim_miner.extract_core_claims(headline, summary, max_claims=1)
    return core_claims[0] if core_claims else headline or ""

def extract_claim_targets(headline: str, summary: Optional[str] = None) -> List[str]:
    entities = set(text_util.extract_entities(headline))
    if summary:
        entities.update(text_util.extract_entities(summary))
    targets = [e for e in entities if len(e) > 2 and e.lower() not in {"news", "report", "update", "analysis"}]
    return targets[:4]

def extract_keyphrases(text: str, max_phrases: int = 6) -> List[str]:
    if not text or not text.strip():
        return []
    
    tokens = text_util.tokenize(text)
    entities = text_util.extract_entities(text)
    keyphrases = []
    
    keyphrases.extend(entities[:3])
    
    token_freq = {}
    for token in tokens:
        token_freq[token] = token_freq.get(token, 0) + 1
    
    scored_tokens = []
    for token, freq in token_freq.items():
        score = min(len(token) - 2, 4)
        if freq == 1:
            score += 1
        elif freq > 3:
            score -= 2
        
        if score > 0:
            scored_tokens.append((token, score))
    
    scored_tokens.sort(key=lambda x: x[1], reverse=True)
    keyphrases.extend([token for token, _ in scored_tokens[:max_phrases-len(keyphrases)]])
    
    seen = set()
    unique_keyphrases = []
    for phrase in keyphrases:
        phrase_lower = phrase.lower()
        if phrase_lower not in seen and len(phrase) > 2:
            seen.add(phrase_lower)
            unique_keyphrases.append(phrase)
    
    return unique_keyphrases[:max_phrases]


def expand_with_aliases(tokens: List[str]) -> List[str]:
    if not tokens:
        return []
    
    expanded = set(tokens)
    
    for token in tokens:
        token_lower = token.lower().strip()
        
        if token_lower.endswith('s') and len(token_lower) > 3:
            expanded.add(token_lower[:-1])
        elif not token_lower.endswith('s'):
            expanded.add(token_lower + 's')
        
        if len(token_lower) > 4:
            words = token_lower.split()
            if len(words) > 1:
                acronym = ''.join(w[0] for w in words if w)
                if len(acronym) > 1:
                    expanded.add(acronym)
    
    filtered = [token for token in expanded if len(token) > 2]
    return list(set(filtered))[:6]


def build_queries(headline: str, source_domain: Optional[str] = None, summary: Optional[str] = None) -> List[Dict[str, str]]:
    
    queries = []
    
    claims = claim_miner.extract_core_claims(headline, summary, max_claims=3)
    for claim in claims:
        claim_type = claim_miner.classify_claim(claim)
        targets = claim_miner.extract_targets(claim, claim_type)
        
        if claim_type == "policy":
            queries.append({"reason": f"policy_exact", "q": f'"{claim[:70]}"'})
            
            if "objects" in targets and targets["objects"]:
                topic_tokens = " ".join(list(targets["objects"])[:2])
                queries.append({"reason": "policy_topic", "q": f"{headline[:30]} {topic_tokens}"})
            
            if "actions" in targets and "objects" in targets:
                actions_list = list(targets["actions"])[:2]
                objects_list = list(targets["objects"])[:2]
                for action in actions_list:
                    for obj in objects_list:
                        queries.append({"reason": "policy_action", "q": f"{action} {obj}"})
        
        elif claim_type == "statistics":
            # Exact quoted claim
            queries.append({"reason": "statistics_exact", "q": f'"{claim[:70]}"'})
            
            # Number + unit + subject triplet
            if "numbers" in targets and "subjects" in targets:
                numbers_list = list(targets["numbers"])[:2]
                subjects_list = list(targets["subjects"])[:2]
                units_list = list(targets.get("units", [""]))
                for number in numbers_list:
                    for subject in subjects_list:
                        unit = units_list[0] if units_list else ""
                        if unit:
                            queries.append({"reason": "statistics_triplet", "q": f"{number} {unit} {subject}"})
                        else:
                            queries.append({"reason": "statistics_number", "q": f"{number} {subject}"})
            
            # Subject + number + unit (unquoted)
            if "subjects" in targets and "numbers" in targets:
                subjects_list = list(targets["subjects"])[:1]
                numbers_list = list(targets["numbers"])[:1]
                for subject in subjects_list:
                    for number in numbers_list:
                        queries.append({"reason": "statistics_subject", "q": f"{subject} {number}"})
        
        elif claim_type == "causal":
            # Exact quoted claim
            queries.append({"reason": "causal_exact", "q": f'"{claim[:70]}"'})
            
            # Cause + effect terms combined
            if "causes" in targets and "effects" in targets:
                causes_list = list(targets["causes"])[:2]
                effects_list = list(targets["effects"])[:2]
                for cause in causes_list:
                    for effect in effects_list:
                        queries.append({"reason": "causal_relation", "q": f"{cause} {effect}"})
        
        else:  # factoid
            # Exact quoted claim
            queries.append({"reason": "factoid_exact", "q": f'"{claim[:70]}"'})
            
            # Speaker/entity + predicate
            if "speakers" in targets and "predicates" in targets:
                speakers_list = list(targets["speakers"])[:2]
                predicates_list = list(targets["predicates"])[:2]
                for speaker in speakers_list:
                    for predicate in predicates_list:
                        queries.append({"reason": "factoid_speaker", "q": f"{speaker} {predicate}"})
    
    if headline:
        queries.append({"reason": "headline_quoted", "q": f'"{headline[:70]}"'})
        headline_keyphrases = extract_keyphrases(headline)
        for phrase in headline_keyphrases[:2]:
            queries.append({"reason": "headline_plain", "q": phrase})
    
    entities = text_util.extract_entities(headline + " " + (summary or ""))
    for entity in entities[:3]:
        aliases = expand_with_aliases([entity])
        for alias in aliases[:2]:
            queries.append({"reason": "entity_expanded", "q": alias})
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
    
    return valid_queries[:10]