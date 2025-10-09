import re
from typing import List, Dict, Any

def summarize_lead3(text: str, max_sentences: int = 3, max_chars: int = 600) -> Dict[str, Any]:
    if not text or not text.strip():
        return {"sentences": [], "joined": "", "charCount": 0, "wordCount": 0}

    normalized_text = ' '.join(text.split())

    sentences = re.split(r'(?<=[.?!])\s+', normalized_text)
    
    lead_sentences: List[str] = []
    for s in sentences:
        if len(lead_sentences) >= max_sentences:
            break
        s_stripped = s.strip()
        if s_stripped:
            lead_sentences.append(s_stripped)

    joined_text = " ".join(lead_sentences)
    
    if len(joined_text) > max_chars:
        trimmed_text = joined_text[:max_chars]
        last_space = trimmed_text.rfind(' ')
        if last_space != -1:
            joined_text = trimmed_text[:last_space].rstrip('.,') + "..."
        else:
            joined_text = trimmed_text + "..."

    char_count = len(joined_text)
    word_count = len(joined_text.split())

    return {
        "sentences": lead_sentences,
        "joined": joined_text,
        "charCount": char_count,
        "wordCount": word_count,
    }
