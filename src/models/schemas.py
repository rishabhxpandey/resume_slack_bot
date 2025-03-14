from typing import Dict, List, TypedDict

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field


class WorkflowState(TypedDict):
    """State management for job analysis workflow"""

    messages: List[BaseMessage]
    job_text: str
    current_step: str
    analysis_results: Dict
    matching_results: Dict
    recommendations: List[str]
    errors: List[str]


class JobPosting(BaseModel):
    """Schema for job posting analysis"""

    job_title: str = Field(description="Job title")
    company_name: str = Field(description="Company name")
    required_skills: List[str] = Field(description="Required skills")
    preferred_skills: List[str] = Field(description="Preferred skills")
    experience_level: str = Field(description="Required experience level")
    location: str = Field(description="Job location")
    key_responsibilities: List[str] = Field(description="Key responsibilities")


class ResumeData(BaseModel):
    """Schema for parsed resume data"""

    user_id: str = Field(description="Slack user ID")
    technical_skills: List[str] = Field(description="Technical skills")
    soft_skills: List[str] = Field(description="Soft skills")
    experience_level: str = Field(description="Experience level")
    education: str = Field(description="Education details")
