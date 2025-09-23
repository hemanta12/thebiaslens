import re
from typing import List, Dict, Any

def summarize_lead3(text: str, max_sentences: int = 3, max_chars: int = 600) -> Dict[str, Any]:
    """
    Generates a simple lead-based summary from the given text.

    Steps:
    1. Normalize whitespace.
    2. Sentence split with a lightweight regex on .?! followed by space/newline.
    3. Take the first max_sentences non-empty sentences.
    4. Join them, then hard-cap to max_chars (trim at a word boundary, add ellipsis if trimmed).
    
    Returns:
        A dictionary with sentences, joined text, char count, and word count.
    """
    if not text or not text.strip():
        return {"sentences": [], "joined": "", "charCount": 0, "wordCount": 0}

    # 1. Normalize whitespace
    normalized_text = ' '.join(text.split())

    # 2. Sentence split with a lightweight regex
    # Splits on '.', '?', '!' followed by a space or end of string.
    # Using a lookbehind to keep the delimiter.
    sentences = re.split(r'(?<=[.?!])\s+', normalized_text)
    
    # 3. Take the first max_sentences non-empty sentences
    lead_sentences: List[str] = []
    for s in sentences:
        if len(lead_sentences) >= max_sentences:
            break
        s_stripped = s.strip()
        if s_stripped:
            lead_sentences.append(s_stripped)

    # 4. Join and cap to max_chars
    joined_text = " ".join(lead_sentences)
    
    if len(joined_text) > max_chars:
        # Trim at a word boundary
        trimmed_text = joined_text[:max_chars]
        last_space = trimmed_text.rfind(' ')
        if last_space != -1:
            joined_text = trimmed_text[:last_space].rstrip('.,') + "..."
        else:
            # No space found, just hard truncate
            joined_text = trimmed_text + "..."

    char_count = len(joined_text)
    word_count = len(joined_text.split())

    return {
        "sentences": lead_sentences,
        "joined": joined_text,
        "charCount": char_count,
        "wordCount": word_count,
    }
