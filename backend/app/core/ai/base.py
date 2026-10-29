from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple
from pydantic import BaseModel, Field


class ParsedWorkExperience(BaseModel):
    company: str | None = None
    role: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None


class ParsedEducation(BaseModel):
    institution: str | None = None
    degree: str | None = None
    field_of_study: str | None = None
    graduation_year: int | None = None


class ParsedResumeOutput(BaseModel):
    full_name: str | None = Field(default=None, description="Candidate's full name")
    email: str | None = Field(default=None, description="Email address")
    phone: str | None = Field(default=None, description="Phone number")
    headline: str | None = Field(default=None, description="Short professional headline/title")
    summary: str | None = Field(default=None, description="Brief candidate background summary")
    experience_years: float | None = Field(default=None, description="Total years of work experience")
    location: str | None = Field(default=None, description="City, State, or Country")
    skills: List[str] = Field(default_factory=list, description="List of technical and soft skills")
    work_history: List[ParsedWorkExperience] = Field(default_factory=list)
    education: List[ParsedEducation] = Field(default_factory=list)


RESUME_PARSE_SYSTEM_PROMPT = """
You are an expert HR AI assistant and resume parser.
Extract structured professional details from the raw resume text provided.
Return ONLY valid JSON strictly matching the target schema.
Do not invent information. If a field is missing or ambiguous, set it to null or an empty list.
"""


class BaseAIProvider(ABC):
    """Abstract interface for multi-LLM provider adapters."""

    @abstractmethod
    async def parse_resume(self, raw_text: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Parses raw resume text into structured JSON.
        
        Returns:
            Tuple[Dict[str, Any], Dict[str, Any]]: 
                - parsed_data: Dictionary conforming to ParsedResumeOutput
                - usage_meta: Token usage and estimated cost dict (input_tokens, output_tokens, cost_usd)
        """
        pass