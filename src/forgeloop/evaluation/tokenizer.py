import math


class TokenAnalyzer:
    """Offline token estimate with an optional locally cached tiktoken encoder.

    The penalty rate is a configurable local assumption, not a Kaggle rule.
    The default avoids downloads and estimates one token per four UTF-8 bytes.
    """

    def __init__(self, model=None, penalty_per_1000_tokens=0.1):
        if not math.isfinite(penalty_per_1000_tokens) or penalty_per_1000_tokens < 0:
            raise ValueError("penalty_per_1000_tokens must be finite and nonnegative")
        self.rate = penalty_per_1000_tokens
        self.encoding = None
        if model is not None:
            try:
                import tiktoken
            except ImportError as exc:
                raise RuntimeError(
                    "Install tiktoken to request an explicit encoding"
                ) from exc
            self.encoding = tiktoken.get_encoding(model)

    def calculate_penalty(self, transcript_text: str) -> dict:
        if self.encoding is None:
            token_count = math.ceil(len(transcript_text.encode("utf-8")) / 4)
            method = "utf8_bytes_divided_by_4_estimate"
        else:
            token_count = len(
                self.encoding.encode(transcript_text, disallowed_special=())
            )
            method = "tiktoken"
        return {
            "tokens": token_count,
            "cost_penalty": token_count / 1000.0 * self.rate,
            "method": method,
            "is_estimate": self.encoding is None,
            "official_scoring": False,
        }

    def calculate_exact_penalty(self, transcript_text: str) -> dict:
        """Compatibility alias; returned metadata identifies estimation precisely."""
        return self.calculate_penalty(transcript_text)
