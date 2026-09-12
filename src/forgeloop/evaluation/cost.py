from .tokenizer import TokenAnalyzer


def estimate_token_cost(transcript_text: str) -> float:
    """Offline local penalty estimate; not an official competition cost."""
    return TokenAnalyzer().calculate_penalty(transcript_text)["cost_penalty"]
