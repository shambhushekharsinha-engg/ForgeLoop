import re


class TranscriptScrubber:
    """Preserve transcripts by default; optionally create a redacted review copy.

    JSON/XML may contain human instructions or AI decisions, so code fences alone
    are never grounds for deletion. This does not guarantee competition eligibility.
    Keep the original transcript as submission evidence.
    """

    tool_output_pattern = re.compile(
        r"<!-- forgeloop:tool-output -->.*?<!-- /forgeloop:tool-output -->",
        re.DOTALL,
    )

    def scrub(self, raw_transcript: str, *, redact_tool_outputs: bool = False) -> str:
        if not redact_tool_outputs:
            return raw_transcript
        return self.tool_output_pattern.sub(
            "[TOOL_OUTPUT_REDACTED_IN_REVIEW_COPY]", raw_transcript
        )
