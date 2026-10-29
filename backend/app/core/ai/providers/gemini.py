import json
import logging
from typing import Any, Dict, Tuple
from google import genai

from app.core.ai.base import BaseAIProvider, ParsedResumeOutput, RESUME_PARSE_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class GeminiProvider(BaseAIProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        genai.Client(api_key=api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=RESUME_PARSE_SYSTEM_PROMPT,
            generation_config={"response_mime_type": "application/json"},
        )

    async def parse_resume(self, raw_text: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        prompt = f"Extract structured candidate data from this resume text:\n\n{raw_text}"

        response = await self.model.generate_content_async(prompt)
        
        # Calculate token counts
        input_tokens = response.usage_metadata.prompt_token_count if response.usage_metadata else 0
        output_tokens = response.usage_metadata.candidates_token_count if response.usage_metadata else 0
        
        # Est cost calculation ($0.075 / 1M input, $0.30 / 1M output for Flash)
        rate_input = 0.000000075 if "flash" in self.model_name else 0.00000125
        rate_output = 0.00000030 if "flash" in self.model_name else 0.00000500
        cost_usd = (input_tokens * rate_input) + (output_tokens * rate_output)

        try:
            parsed_raw = json.loads(response.text)
            validated_output = ParsedResumeOutput(**parsed_raw)
            parsed_data = validated_output.model_dump()
        except Exception as exc:
            logger.error("Failed to parse or validate Gemini output: %s", exc)
            parsed_data = ParsedResumeOutput().model_dump()

        usage_meta = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": round(cost_usd, 6),
        }

        return parsed_data, usage_meta