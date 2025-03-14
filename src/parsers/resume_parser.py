import json
import os
from pathlib import Path
from typing import Dict, List

import aiohttp  # For async HTTP requests
import PyPDF2
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from src.models.schemas import ResumeData
from src.utils.file_helpers import read_pdf_content, save_file
