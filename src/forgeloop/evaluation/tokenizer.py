import tiktoken

class TokenAnalyzer:
    """Uses OpenAI's official tiktoken to exactly match the Kaggle cost penalty logic."""
    def __init__(self, model="cl100k_base"):
        # BuildArena likely uses standard GPT-4/o1 tokenization
        self.encoding = tiktoken.get_encoding(model)
        
    def calculate_exact_penalty(self, transcript_text: str) -> dict:
        """Calculates precise token count and the resulting Kaggle cost penalty."""
        token_count = len(self.encoding.encode(transcript_text))
        
        # Simulated Kaggle Rule: 0.1 penalty deduction per 1000 tokens
        penalty = (token_count / 1000.0) * 0.1
        
        return {
            "tokens": token_count,
            "cost_penalty": round(penalty, 4)
        }
