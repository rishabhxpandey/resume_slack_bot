import json
import os
from pathlib import Path
from typing import Dict, List

import PyPDF2
import requests
import spacy


class ResumeParser:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.resumes_dir = Path("resumes")
        self.skills_file = self.resumes_dir / "skills_database.json"

        # Initialize skills database if it doesn't exist
        if not self.skills_file.exists():
            self._init_skills_database()

    def _init_skills_database(self):
        """Initialize an empty skills database"""
        self.resumes_dir.mkdir(exist_ok=True)
        initial_data = {}
        with open(self.skills_file, "w") as f:
            json.dump(initial_data, f)

    def save_resume(self, user_id: str, file_url: str) -> None:
        """
        Download and save a resume, then extract and store skills
        """
        # Create user directory if it doesn't exist
        user_dir = self.resumes_dir / user_id
        user_dir.mkdir(exist_ok=True)

        # Download the resume
        headers = {"Authorization": f'Bearer {os.environ["SLACK_BOT_TOKEN"]}'}
        response = requests.get(file_url, headers=headers)

        # Save the PDF
        pdf_path = user_dir / "resume.pdf"
        with open(pdf_path, "wb") as f:
            f.write(response.content)

        # Extract and save skills
        skills = self._extract_skills_from_pdf(pdf_path)
        self._update_skills_database(user_id, skills)

    def _extract_skills_from_pdf(self, pdf_path: Path) -> List[str]:
        """
        Extract skills from a PDF resume using NLP
        """
        text = ""
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()

        # Process text with spaCy
        doc = self.nlp(text)

        # Extract potential skills (this is a simple implementation)
        skills = []
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PRODUCT", "GPE"]:
                skills.append(ent.text)

        # Add common programming languages and tools
        programming_keywords = [
            "Python",
            "Java",
            "JavaScript",
            "C++",
            "SQL",
            "React",
            "Node.js",
        ]
        for keyword in programming_keywords:
            if keyword.lower() in text.lower():
                skills.append(keyword)

        return list(set(skills))

    def _update_skills_database(self, user_id: str, skills: List[str]) -> None:
        """
        Update the skills database with user's skills
        """
        with open(self.skills_file, "r") as f:
            skills_db = json.load(f)

        skills_db[user_id] = {"skills": skills, "last_updated": str(Path.ctime(Path()))}

        with open(self.skills_file, "w") as f:
            json.dump(skills_db, f, indent=2)

    def find_matching_members(self, required_skills: List[str]) -> Dict[str, List[str]]:
        """
        Find members who have the required skills and identify skill gaps
        """
        with open(self.skills_file, "r") as f:
            skills_db = json.load(f)

        matches = {}
        for user_id, user_data in skills_db.items():
            user_skills = set(user_data["skills"])
            matching_skills = user_skills.intersection(required_skills)
            if matching_skills:
                matches[user_id] = list(matching_skills)

        return matches

    def get_user_skills(self, user_id: str) -> List[str]:
        """
        Get skills for a specific user
        """
        with open(self.skills_file, "r") as f:
            skills_db = json.load(f)

        return skills_db.get(user_id, {}).get("skills", [])
