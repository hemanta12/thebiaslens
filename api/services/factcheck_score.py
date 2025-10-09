import re
from datetime import datetime, timedelta
from typing import Dict, Set, Optional
from .textutil import text_util
from .factcheck_filters import passes_gates

def score_item(
    query: str,
    claim_text: str,
    source_domain: Optional[str],
    published_at: Optional[datetime],
    claim_type: str,
    targets: Dict[str, Set[str]],
    reason: str
) -> float:
    if not passes_gates(claim_text, claim_type, targets):
        return -1.0
    
    base_score = _calculate_ngram_overlap(query, claim_text)
    bonus = 0.0
    
    if source_domain and _has_domain_token(claim_text, source_domain):
        bonus += 0.05
    
    if published_at:
        months_ago = (datetime.now() - published_at.replace(tzinfo=None)).days / 30
        if months_ago <= 18:
            bonus += 0.08 * max(0, (18 - months_ago) / 18)
    
    claim_based_reasons = {'core_claim', 'policy_exact', 'statistics_exact', 'causal_exact', 'factoid_exact'}
    if reason in claim_based_reasons:
        bonus += 0.10
    
    type_bonus = _calculate_type_bonus(claim_text, claim_type, targets, query)
    bonus += type_bonus
    
    distractor_penalty = _calculate_distractor_penalty(claim_text, claim_type, targets)
    bonus -= distractor_penalty
    
    return max(0.0, min(1.0, base_score + bonus))


def _calculate_ngram_overlap(query: str, claim_text: str) -> float:
    bigram_score = text_util.ngram_jaccard_similarity(query, claim_text, n=2)
    unigram_score = text_util.jaccard_similarity(query, claim_text)
    
    query_entities = set(ent.lower() for ent in text_util.extract_entities(query))
    claim_entities = set(ent.lower() for ent in text_util.extract_entities(claim_text))
    
    entity_overlap = 0.0
    if query_entities and claim_entities:
        entity_overlap = len(query_entities.intersection(claim_entities)) / len(query_entities.union(claim_entities))
    
    query_tokens = set(text_util.tokenize(query))
    claim_tokens = set(text_util.tokenize(claim_text))
    
    token_overlap = 0.0
    if query_tokens and claim_tokens:
        token_overlap = len(query_tokens.intersection(claim_tokens)) / len(query_tokens.union(claim_tokens))
    
    base_score = (
        0.4 * bigram_score +
        0.3 * unigram_score +
        0.2 * entity_overlap +
        0.1 * token_overlap
    )
    
    if entity_overlap > 0.3 or token_overlap > 0.4:
        base_score = max(base_score, 0.3)
    
    return base_score


def _has_domain_token(claim_text: str, source_domain: str) -> bool:
    if not source_domain:
        return False
    
    # Extract meaningful tokens from domain
    domain_parts = source_domain.replace('.', ' ').replace('-', ' ').split()
    domain_tokens = [part for part in domain_parts if len(part) > 3]
    
    claim_lower = claim_text.lower()
    return any(token.lower() in claim_lower for token in domain_tokens)


def _calculate_type_bonus(claim_text: str, claim_type: str, targets: Dict[str, Set[str]], query: str) -> float:
    bonus = 0.0
    claim_lower = claim_text.lower()
    
    if claim_type == "policy":
        bonus += _policy_bonus(claim_text, targets)
    elif claim_type == "statistics":
        bonus += _statistics_bonus(claim_text, targets)
    elif claim_type == "causal":
        bonus += _causal_bonus(claim_text, targets)
    elif claim_type == "factoid":
        bonus += _factoid_bonus(claim_text, targets, query)
    
    return bonus


def _policy_bonus(claim_text: str, targets: Dict[str, Set[str]]) -> float:
    bonus = 0.0
    claim_lower = claim_text.lower()
    
    # Actor present bonus
    actors = targets.get("actors", set())
    if any(actor.lower() in claim_lower for actor in actors):
        bonus += 0.08
    
    # Action+object proximity bonus
    actions = targets.get("actions", set())
    objects = targets.get("objects", set())
    
    if actions and objects:
        tokens = text_util.tokenize(claim_text)
        action_positions = []
        object_positions = []
        
        for i, token in enumerate(tokens):
            if any(action.lower() in token.lower() for action in actions):
                action_positions.append(i)
            if any(obj.lower() in token.lower() for obj in objects):
                object_positions.append(i)
        
        # Check proximity ≤ 4 tokens
        tight_proximity = False
        for action_pos in action_positions:
            for object_pos in object_positions:
                if abs(action_pos - object_pos) <= 4:
                    tight_proximity = True
                    break
            if tight_proximity:
                break
        
        if tight_proximity:
            bonus += 0.12
    
    return bonus


def _statistics_bonus(claim_text: str, targets: Dict[str, Set[str]]) -> float:
    bonus = 0.0
    
    numbers = targets.get("numbers", set())
    units = targets.get("units", set())
    subjects = targets.get("subjects", set())
    
    claim_lower = claim_text.lower()
    
    # All three present bonus
    has_number = any(num in claim_text for num in numbers)
    has_unit = any(unit.lower() in claim_lower for unit in units)
    has_subject = any(subj.lower() in claim_lower for subj in subjects)
    
    if has_number and has_unit and has_subject:
        bonus += 0.15
    
    # Exact number match bonus
    extracted_numbers = text_util.extract_numbers_with_units(claim_text)
    extracted_nums = {item["number"] for item in extracted_numbers}
    
    if numbers.intersection(extracted_nums):
        bonus += 0.10
    
    return bonus


def _causal_bonus(claim_text: str, targets: Dict[str, Set[str]]) -> float:
    bonus = 0.0
    claim_lower = claim_text.lower()
    
    # Explicit causal verbs
    causal_verbs = ['cause', 'causes', 'caused', 'lead', 'leads', 'led', 'result', 'results', 'resulted']
    if any(verb in claim_lower for verb in causal_verbs):
        bonus += 0.10
    
    # Causal phrases
    causal_phrases = ['leads to', 'results in', 'due to', 'because of', 'associated with', 'linked to']
    if any(phrase in claim_lower for phrase in causal_phrases):
        bonus += 0.12
    
    # Cause→effect order bonus
    causes = targets.get("causes", set())
    effects = targets.get("effects", set())
    
    if causes and effects:
        tokens = text_util.tokenize(claim_text)
        cause_positions = []
        effect_positions = []
        
        for i, token in enumerate(tokens):
            if any(cause.lower() in token.lower() for cause in causes):
                cause_positions.append(i)
            if any(effect.lower() in token.lower() for effect in effects):
                effect_positions.append(i)
        
        # Check if any cause appears before any effect
        if cause_positions and effect_positions:
            min_cause = min(cause_positions)
            min_effect = min(effect_positions)
            if min_cause < min_effect:
                bonus += 0.08
    
    return bonus


def _factoid_bonus(claim_text: str, targets: Dict[str, Set[str]], query: str) -> float:
    bonus = 0.0
    claim_lower = claim_text.lower()
    
    # Speaker name bonus
    speakers = targets.get("speakers", set())
    if any(speaker.lower() in claim_lower for speaker in speakers):
        bonus += 0.10
    
    # Quoted content bonus
    if '"' in claim_text or "'" in claim_text:
        bonus += 0.08
    
    # Reported speech patterns
    speech_patterns = [
        r'\b(said|stated|claimed|announced|declared|reported|told|mentioned)\b',
        r'\b(according\s+to|reported\s+by)\b'
    ]
    
    if any(re.search(pattern, claim_lower) for pattern in speech_patterns):
        bonus += 0.06
    
    return bonus


def _calculate_distractor_penalty(claim_text: str, claim_type: str, targets: Dict[str, Set[str]]) -> float:
    penalty = 0.0
    
    entities = text_util.extract_entities(claim_text)
    
    if not entities:
        return penalty
    
    # Get relevant target entities for this claim type
    relevant_entities = set()
    if claim_type == "policy":
        relevant_entities.update(targets.get("actors", set()))
        relevant_entities.update(targets.get("objects", set()))
    elif claim_type == "statistics":
        relevant_entities.update(targets.get("subjects", set()))
    elif claim_type == "causal":
        relevant_entities.update(targets.get("causes", set()))
        relevant_entities.update(targets.get("effects", set()))
    elif claim_type == "factoid":
        relevant_entities.update(targets.get("speakers", set()))
    
    # Count entities not in relevant targets
    distractor_count = 0
    for entity in entities:
        entity_lower = entity.lower()
        if not any(target.lower() in entity_lower or entity_lower in target.lower() for target in relevant_entities):
            distractor_count += 1
    
    # Apply penalty for distractors
    if distractor_count > 0:
        penalty = min(0.05 * distractor_count, 0.15)  # Cap at 0.15
    
    return penalty
