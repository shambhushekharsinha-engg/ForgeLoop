import re

class TranscriptScrubber:
    """
    The competition rules state: 'Tool feedback, tool return payloads, generated JSON blocks... 
    may be removed before counting so that participants are not heavily penalized'.
    
    This module automatically scrubs our chat_transcript.md to mathematically minimize 
    our Cost Penalty before final submission.
    """
    def __init__(self):
        # Matches ```json ... ``` and ```xml ... ``` blocks
        self.code_block_pattern = re.compile(r'```(?:json|xml).*?```', re.DOTALL | re.IGNORECASE)
        
    def scrub(self, raw_transcript: str) -> str:
        # Remove verbose payloads
        scrubbed = re.sub(self.code_block_pattern, '[PAYLOAD_REMOVED_FOR_SUBMISSION]', raw_transcript)
        # Strip excessive whitespace
        scrubbed = " ".join(scrubbed.split())
        return scrubbed
