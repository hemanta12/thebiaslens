import re
from typing import List, Dict, Literal, Set, Optional
from .textutil import text_util

ClaimType = Literal["policy", "statistics", "causal", "factoid"]

class ClaimMiner:
    
    def __init__(self):
        self.policy_verbs = {
            'freeze', 'block', 'halt', 'suspend', 'withhold', 'impound', 'stay', 
            'ban', 'mandate', 'approve', 'enact', 'implement', 'announce', 'sign',
            'veto', 'overturn', 'pass', 'reject', 'authorize', 'prohibit', 'rule',
            'decide', 'order', 'require', 'allow', 'permit', 'enable', 'declare'
        }
        
        self.policy_nouns = {
            'order', 'ruling', 'bill', 'law', 'policy', 'regulation', 'directive',
            'executive', 'legislation', 'amendment', 'act', 'statute', 'decree'
        }
        
        self.causal_indicators = {
            'cause', 'causes', 'caused', 'link', 'linked', 'links', 'increase', 
            'increases', 'reduce', 'reduces', 'lead', 'leads', 'result', 'results',
            'associate', 'associated', 'connection', 'impact', 'effect', 'affects',
            'influence', 'contribute', 'due', 'because', 'trigger', 'triggers'
        }
        
        self.causal_phrases = [
            'linked to', 'leads to', 'results in', 'associated with', 'due to',
            'because of', 'caused by', 'resulting from', 'stems from', 'attributed to'
        ]
    
    def extract_core_claims(self, headline: str, summary: Optional[str] = None, max_claims: int = 3) -> List[str]:
        claims = []
        
        if headline and headline.strip():
            claims.append(headline.strip())
        
        if summary and summary.strip():
            summary_claims = self._extract_claims_from_text(summary)
            headline_tokens = text_util.extract_tokens_set(headline) if headline else set()
            
            filtered_claims = []
            for claim in summary_claims:
                word_count = len(claim.split())
                if 8 <= word_count <= 35:
                    claim_tokens = text_util.extract_tokens_set(claim)
                    overlap = len(headline_tokens.intersection(claim_tokens)) if headline_tokens else 0
                    score = overlap + (1 if 12 <= word_count <= 25 else 0)
                    filtered_claims.append((claim, score))
            
            filtered_claims.sort(key=lambda x: x[1], reverse=True)
            claims.extend([claim for claim, _ in filtered_claims[:max_claims-1]])
        
        return claims[:max_claims]
    
    def _extract_claims_from_text(self, text: str) -> List[str]:
        if not text or not text.strip():
            return []
        
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        claim_candidates = []
        for sentence in sentences:
            word_count = len(sentence.split())
            if 8 <= word_count <= 35:
                claim_candidates.append(sentence)
        
        return claim_candidates
    
    def classify_claim(self, claim: str) -> ClaimType:
        """Classify claim into policy, statistics, causal, or factoid."""
        if not claim:
            return "factoid"
        
        claim_lower = claim.lower()
        claim_tokens = text_util.tokenize(claim_lower)
        claim_tokens_set = set(claim_tokens)
        
        # Check for statistics (numbers + units/entities)
        numbers = text_util.extract_numbers_with_units(claim)
        if numbers:
            # Look for statistical indicators
            stats_indicators = {'percent', '%', 'million', 'billion', 'thousand', 'cases', 'votes', 'dollars', 'rate'}
            if any(indicator in claim_lower for indicator in stats_indicators):
                return "statistics"
        
        # Check for policy (specific verbs or nouns, including partial matches)
        policy_verb_match = bool(claim_tokens_set.intersection(self.policy_verbs))
        policy_noun_match = bool(claim_tokens_set.intersection(self.policy_nouns))
        
        # Also check for policy verbs in the full text (handles word forms)
        policy_verb_text_match = any(verb in claim_lower for verb in self.policy_verbs)
        policy_noun_text_match = any(noun in claim_lower for noun in self.policy_nouns)
        
        if policy_verb_match or policy_noun_match or policy_verb_text_match or policy_noun_text_match:
            return "policy"
        
        # Check for causal relationships
        causal_token_match = bool(claim_tokens_set.intersection(self.causal_indicators))
        causal_phrase_match = any(phrase in claim_lower for phrase in self.causal_phrases)
        
        if causal_token_match or causal_phrase_match:
            return "causal"
        
        # Default to factoid (quotes, claims about people/organizations)
        return "factoid"
    
    def extract_targets(self, claim: str, claim_type: ClaimType) -> Dict[str, Set[str]]:
        """Extract token sets for different claim types to use in gating."""
        targets = {}
        
        if claim_type == "policy":
            targets.update(self._extract_policy_targets(claim))
        elif claim_type == "statistics":
            targets.update(self._extract_statistics_targets(claim))
        elif claim_type == "causal":
            targets.update(self._extract_causal_targets(claim))
        else:  # factoid
            targets.update(self._extract_factoid_targets(claim))
        
        # Normalize all token sets
        normalized_targets = {}
        for key, token_set in targets.items():
            normalized_targets[key] = {
                token.lower() for token in token_set 
                if len(token) >= 3 and token.lower() not in text_util.stop_words
            }
        
        return normalized_targets
    
    def _extract_policy_targets(self, claim: str) -> Dict[str, Set[str]]:
        """Extract policy-specific targets: actions, objects, actors."""
        actions = set()
        objects = set()
        actors = set()
        
        claim_tokens = text_util.tokenize(claim)
        entities = text_util.extract_entities(claim)
        claim_lower = claim.lower()
        
        # Actions: policy verbs found in claim (exact and partial matches)
        for token in claim_tokens:
            if token.lower() in self.policy_verbs:
                actions.add(token)
        
        # Also check for verb forms in the claim text
        for verb in self.policy_verbs:
            if verb in claim_lower:
                actions.add(verb)
        
        # Add semantic equivalents and common policy actions
        policy_action_map = {
            'approve': ['authorized', 'permits', 'allows', 'enables'],
            'mandate': ['requires', 'orders', 'commands'],
            'ban': ['prohibits', 'forbids', 'blocks'],
            'announce': ['declares', 'states', 'reveals'],
            'rule': ['decides', 'determines', 'judges']
        }
        
        for base_action, variants in policy_action_map.items():
            if base_action in claim_lower or any(variant in claim_lower for variant in variants):
                actions.add(base_action)
        
        # Objects: policy nouns, key entities, and domain-specific objects
        for token in claim_tokens:
            if token.lower() in self.policy_nouns:
                objects.add(token)
        
        # Add domain-specific objects (mining, power, etc.)
        domain_objects = ['mining', 'crypto', 'cryptocurrency', 'power', 'plants', 'facilities', 'operations']
        for obj in domain_objects:
            if obj in claim_lower:
                objects.add(obj)
        
        # Add entities as potential objects
        objects.update(entities)
        
        # Actors: government entities and officials
        government_indicators = {'president', 'congress', 'senate', 'house', 'court', 'administration', 'government', 'biden'}
        
        # Check for government actors in entities
        for entity in entities:
            entity_lower = entity.lower()
            if any(indicator in entity_lower for indicator in government_indicators):
                actors.add(entity)
        
        # Check for government actors in claim text
        for indicator in government_indicators:
            if indicator in claim_lower:
                actors.add(indicator)
        
        return {
            "actions": actions,
            "objects": objects,
            "actors": actors
        }
    
    def _extract_statistics_targets(self, claim: str) -> Dict[str, Set[str]]:
        """Extract statistics-specific targets: numbers, units, subjects, locales."""
        numbers = set()
        units = set()
        subjects = set()
        locales = set()
        
        # Extract numbers with units
        number_data = text_util.extract_numbers_with_units(claim)
        for item in number_data:
            numbers.add(item["number"])
            if item["unit"]:
                units.add(item["unit"])
        
        # Subject tokens (entities and key nouns)
        entities = text_util.extract_entities(claim)
        subjects.update(entities)
        
        # Locale tokens (countries, regions, states)
        locale_patterns = [
            r'\b[A-Z][a-z]+\s+(State|County|City|Province)\b',
            r'\b(United States|America|US|USA|China|Russia|Europe|Asia|Africa)\b',
            r'\b[A-Z][a-z]+(?:land|stan|burg|shire)\b'  # Country/region suffixes
        ]
        
        for pattern in locale_patterns:
            matches = re.finditer(pattern, claim, re.IGNORECASE)
            for match in matches:
                locales.add(match.group(0))
        
        return {
            "numbers": numbers,
            "units": units,
            "subjects": subjects,
            "locales": locales
        }
    
    def _extract_causal_targets(self, claim: str) -> Dict[str, Set[str]]:
        """Extract causal-specific targets: causes, effects, metrics."""
        causes = set()
        effects = set()
        metrics = set()
        
        entities = text_util.extract_entities(claim)
        claim_tokens = text_util.tokenize(claim)
        claim_lower = claim.lower()
        
        # Look for causal structure with expanded phrases
        causal_split = None
        extended_phrases = self.causal_phrases + ['leads to', 'results in', 'causes', 'due to']
        
        for phrase in extended_phrases:
            if phrase in claim_lower:
                parts = claim_lower.split(phrase, 1)
                if len(parts) == 2:
                    causal_split = (parts[0].strip(), parts[1].strip())
                    break
        
        if causal_split:
            # Before causal phrase = cause, after = effect
            cause_tokens = text_util.tokenize(causal_split[0])
            effect_tokens = text_util.tokenize(causal_split[1])
            
            causes.update(cause_tokens[:5])  # Limit to key tokens
            effects.update(effect_tokens[:5])
        else:
            # Enhanced fallback: look for domain-specific terms
            cause_indicators = ['climate', 'change', 'warming', 'temperature', 'emissions', 'pollution']
            effect_indicators = ['flooding', 'drought', 'storms', 'damage', 'loss', 'increase', 'decrease']
            
            # Check for cause indicators
            for indicator in cause_indicators:
                if indicator in claim_lower:
                    causes.add(indicator)
            
            # Check for effect indicators  
            for indicator in effect_indicators:
                if indicator in claim_lower:
                    effects.add(indicator)
            
            # Fallback to entities if no specific indicators found
            if not causes and not effects:
                causes.update(entities[:3])
                effects.update(entities[3:6] if len(entities) > 3 else entities)
        
        # Metrics: numbers and measurement-related terms
        number_data = text_util.extract_numbers_with_units(claim)
        for item in number_data:
            metrics.add(item["full"])
        
        metric_terms = {'rate', 'level', 'amount', 'degree', 'percentage', 'count', 'number', 'increased', 'decreased'}
        for token in claim_tokens:
            if token.lower() in metric_terms:
                metrics.add(token)
        
        return {
            "causes": causes,
            "effects": effects,
            "metrics": metrics
        }
    
    def _extract_factoid_targets(self, claim: str) -> Dict[str, Set[str]]:
        """Extract factoid-specific targets: speakers, predicates."""
        speakers = set()
        predicates = set()
        
        entities = text_util.extract_entities(claim)
        claim_tokens = text_util.tokenize(claim)
        claim_lower = claim.lower()
        
        # Speakers: entities, people names, organizations
        speakers.update(entities)
        
        # Add common political figures
        political_figures = ['biden', 'trump', 'harris', 'obama', 'clinton']
        for figure in political_figures:
            if figure in claim_lower:
                speakers.add(figure)
        
        # Add organizational entities
        org_indicators = ['administration', 'government', 'congress', 'senate', 'house', 'court', 'bureau', 'department']
        for org in org_indicators:
            if org in claim_lower:
                speakers.add(org)
        
        # Predicates: speech verbs, action verbs, and key terms
        speech_verbs = {'said', 'claimed', 'stated', 'announced', 'declared', 'reported', 'told', 'mentioned'}
        action_verbs = {'did', 'made', 'took', 'gave', 'signed', 'visited', 'met', 'attended'}
        
        # Check for speech/action verbs in tokens
        for token in claim_tokens:
            if token.lower() in speech_verbs.union(action_verbs):
                predicates.add(token)
        
        # Check for speech verbs in text (handles word forms)
        for verb in speech_verbs.union(action_verbs):
            if verb in claim_lower:
                predicates.add(verb)
        
        # Add key descriptive terms as predicates
        descriptive_terms = [token for token in claim_tokens if len(token) > 4 and token not in text_util.stop_words]
        predicates.update(descriptive_terms[:5])
        
        return {
            "speakers": speakers,
            "predicates": predicates
        }


# Global instance
claim_miner = ClaimMiner()