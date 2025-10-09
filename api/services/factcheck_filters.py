import re
from typing import Dict, Set, List
from .textutil import text_util

def gate_policy(text: str, targets: Dict[str, Set[str]]) -> bool:
    if not text or not targets:
        return False
    
    actions = targets.get("actions", set())
    objects = targets.get("objects", set())
    
    if not actions or not objects:
        return False
    
    text_lower = text.lower()
    
    action_synonyms = {
        'ban': ['prohibit', 'forbid', 'block', 'halt', 'stop'],
        'approve': ['authorize', 'permit', 'allow', 'enable'],
        'mandate': ['require', 'order', 'command'],
        'suspend': ['pause', 'halt', 'freeze'],
        'announce': ['declare', 'state', 'reveal']
    }
    
    action_positions = []
    tokens = text_util.tokenize(text)
    
    for i, token in enumerate(tokens):
        # Direct action match
        if any(action.lower() in token.lower() for action in actions):
            action_positions.append(i)
            continue
        
        # Synonym matching
        for action in actions:
            synonyms = action_synonyms.get(action.lower(), [])
            if any(syn in token.lower() for syn in synonyms):
                action_positions.append(i)
                break
        
        # Also check for policy-specific verbs in text
        policy_verbs = ['prohibit', 'forbid', 'authorize', 'require', 'order', 'declare']
        if any(verb in token.lower() for verb in policy_verbs):
            action_positions.append(i)
    
    # Find object positions
    object_positions = []
    for i, token in enumerate(tokens):
        if any(obj.lower() in token.lower() for obj in objects):
            object_positions.append(i)
    
    # Also look for semantic object matches
    if not object_positions:
        # Check for partial matches in the text
        for obj in objects:
            if obj.lower() in text_lower:
                # Find approximate position
                words_before = text_lower[:text_lower.find(obj.lower())].split()
                object_positions.append(len(words_before))
    
    if not action_positions or not object_positions:
        return False
    
    # Check proximity: any action within 8 tokens of any object
    for action_pos in action_positions:
        for object_pos in object_positions:
            if abs(action_pos - object_pos) <= 8:
                return True
    
    return False


def gate_statistics(text: str, targets: Dict[str, Set[str]]) -> bool:
    if not text or not targets:
        return False
    
    subjects = targets.get("subjects", set())
    locales = targets.get("locales", set())
    
    extracted_numbers = text_util.extract_numbers_with_units(text)
    if not extracted_numbers:
        return False
    
    has_number_unit = any(item["unit"] for item in extracted_numbers)
    
    text_lower = text.lower()
    has_subject = any(subj.lower() in text_lower for subj in subjects)
    has_locale = any(locale.lower() in text_lower for locale in locales)
    
    return has_number_unit or (extracted_numbers and (has_subject or has_locale))


def gate_causal(text: str, targets: Dict[str, Set[str]]) -> bool:
    if not text or not targets:
        return False
    
    causes = targets.get("causes", set())
    effects = targets.get("effects", set())
    metrics = targets.get("metrics", set())
    
    if not causes or not (effects or metrics):
        return False
    
    text_lower = text.lower()
    
    # Check for cause tokens
    has_cause = any(cause.lower() in text_lower for cause in causes)
    
    # Check for effect or metric tokens
    has_effect = any(effect.lower() in text_lower for effect in effects)
    has_metric = any(metric.lower() in text_lower for metric in metrics)
    
    if not has_cause or not (has_effect or has_metric):
        return False
    
    # Prefer patterns with causal indicators
    causal_patterns = [
        r'\b(cause|causes|caused|causing)\b',
        r'\b(lead|leads|led|leading)\s+to\b',
        r'\b(result|results|resulted|resulting)\s+in\b',
        r'\b(due\s+to|because\s+of)\b',
        r'\b(increase|increases|decreased|reduce|reduces)\b',
        r'\b(associated\s+with|linked\s+to)\b'
    ]
    
    # Bonus for explicit causal patterns
    has_causal_pattern = any(re.search(pattern, text_lower) for pattern in causal_patterns)
    
    return has_causal_pattern or (has_cause and (has_effect or has_metric))


def gate_factoid(text: str, targets: Dict[str, Set[str]]) -> bool:
    if not text or not targets:
        return False
    
    speakers = targets.get("speakers", set())
    predicates = targets.get("predicates", set())
    
    if not speakers or not predicates:
        return False
    
    text_lower = text.lower()
    
    # Check for speaker/entity mentions
    has_speaker = any(speaker.lower() in text_lower for speaker in speakers)
    
    # Check for predicates (actions, speech verbs, etc.)
    has_predicate = any(pred.lower() in text_lower for pred in predicates)
    
    if not has_speaker or not has_predicate:
        return False
    
    # Additional checks for factoid patterns
    # Look for quote patterns or reported speech
    quote_patterns = [
        r'"[^"]*"',  # Direct quotes
        r'\b(said|claimed|stated|announced|declared|reported|told|mentioned)\b',
        r'\b(according\s+to|reported\s+by)\b'
    ]
    
    has_quote_pattern = any(re.search(pattern, text_lower) for pattern in quote_patterns)
    
    # Gate passes if we have speaker + predicate, with bonus for quote patterns
    return has_speaker and has_predicate and (has_quote_pattern or len(speakers.intersection({s.lower() for s in text.split()})) > 0)


def passes_gates(text: str, claim_type: str, targets: Dict[str, Set[str]]) -> bool:
    """Master gate function: check if text passes type-specific gates."""
    if not text or not claim_type or not targets:
        return False
    
    if claim_type == "policy":
        return gate_policy(text, targets)
    elif claim_type == "statistics":
        return gate_statistics(text, targets)
    elif claim_type == "causal":
        return gate_causal(text, targets)
    elif claim_type == "factoid":
        return gate_factoid(text, targets)
    else:
        # Unknown claim type - use basic heuristic
        return len(text.split()) >= 5  # At least 5 words