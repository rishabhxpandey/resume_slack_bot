from typing import Dict, List

from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from src.models.schemas import JobPosting, WorkflowState
from src.parsers.job_analyzer import JobAnalyzer
