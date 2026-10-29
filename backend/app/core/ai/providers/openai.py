import json
import logging
from typing import Any, Dict, Tuple
from openai import AsyncOpenAI

from app.core.ai.base import BaseAIProvider, ParsedResumeOutput, RESUME_PARSE_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseAIProvider):
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model_name = model_name

    async def parse_resume(self, raw_text: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": RESUME_PARSE_SYSTEM_PROMPT},
                {"role": "user", "content": f"Extract structured candidate data:\n\n{raw_text}"},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )

        content = response.choices[0].message.content or "{}"
        usage = response.usage
        
        input_tokens = usage.prompt_tokens if usage else 0
        output_tokens = usage.completion_tokens if usage else 0

        # Est cost calculation ($0.15 / 1M input, $0.60 / 1M output for mini)
        rate_input = 0.00000015 if "mini" in self.model_name else 0.0000025
        rate_output = 0.00000060 if "mini" in self.model_name else 0.0000100
        cost_usd = (input_tokens * rate_input) + (output_tokens * rate_output)

        try:
            parsed_raw = json.loads(content)
            validated_output = ParsedResumeOutput(**parsed_raw)
            parsed_data = validated_output.model_dump()
        except Exception as exc:
            logger.error("Failed to parse or validate OpenAI output: %s", exc)
            parsed_data = ParsedResumeOutput().model_dump()

        usage_meta = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": round(cost_usd, 6),
        }

        return parsed_data, usage_meta