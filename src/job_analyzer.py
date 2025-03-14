import re
from typing import Dict, List, Tuple

import spacy


class JobAnalyzer:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

        # Common job posting indicators
        self.job_indicators = [
            "job description",
            "responsibilities",
            "requirements",
            "qualifications",
            "looking for",
            "hiring",
            "position",
            "role",
            "opportunity",
        ]

        # Initialize common skills patterns
        self.skill_patterns = [
            # Programming Languages
            r"python|java|javascript|typescript|c\+\+|ruby|php|swift|kotlin|go|rust",
            # Web Technologies
            r"html|css|react|angular|vue|node\.js|express|django|flask|spring",
            # Data & Analytics
            r"sql|mysql|postgresql|mongodb|data analysis|machine learning|ai|tensorflow",
            # Cloud & DevOps
            r"aws|azure|gcp|docker|kubernetes|jenkins|ci/cd",
            # Soft Skills
            r"leadership|communication|teamwork|problem.solving|analytical|project management",
        ]

    def is_job_posting(self, text: str) -> bool:
        """
        Determine if a message is likely a job posting
        """
        text_lower = text.lower()

        # Check for job indicators
        indicator_count = sum(
            1 for indicator in self.job_indicators if indicator in text_lower
        )

        # Check for common job posting patterns
        has_position = bool(re.search(r"position|role|job", text_lower))
        has_requirements = bool(re.search(r"requirements?|qualifications?", text_lower))

        # Consider it a job posting if it has multiple indicators or specific patterns
        return indicator_count >= 2 or (has_position and has_requirements)

    def extract_skills(self, text: str) -> List[str]:
        """
        Extract required skills from job posting text
        """
        text_lower = text.lower()
        skills = set()

        # Extract skills using patterns
        for pattern in self.skill_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                skills.add(match.group().title())

        # Use NLP to extract additional potential skills
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PRODUCT"]:
                skills.add(ent.text)

        return list(skills)

    def analyze_job_posting(self, text: str) -> Dict[str, any]:
        """
        Analyze a job posting and extract relevant information
        """
        required_skills = self.extract_skills(text)

        # Extract experience level
        experience_level = self._extract_experience_level(text)

        # Extract job title
        job_title = self._extract_job_title(text)

        return {
            "job_title": job_title,
            "required_skills": required_skills,
            "experience_level": experience_level,
        }

    def _extract_experience_level(self, text: str) -> str:
        """
        Extract the required experience level from the job posting
        """
        text_lower = text.lower()

        # Look for experience patterns
        entry_patterns = r"entry.level|junior|fresh graduate"
        mid_patterns = r"mid.level|intermediate|\b[2-5].years"
        senior_patterns = r"senior|lead|\b[5-9\+].years"

        if re.search(senior_patterns, text_lower):
            return "Senior"
        elif re.search(mid_patterns, text_lower):
            return "Mid-level"
        elif re.search(entry_patterns, text_lower):
            return "Entry-level"
        else:
            return "Not specified"

    def _extract_job_title(self, text: str) -> str:
        """
        Extract the job title from the posting
        """
        # Common job title patterns
        title_patterns = [
            r"(?i)looking for (?:a|an) ([^.]*)",
            r"(?i)hiring (?:a|an) ([^.]*)",
            r"(?i)position: ([^.]*)",
            r"(?i)role: ([^.]*)",
        ]

        for pattern in title_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()

        return "Position not specified"

    def prepare_response(
        self, analysis: Dict[str, any], matching_members: Dict[str, List[str]]
    ) -> str:
        """
        Prepare a response message for the job posting
        """
        job_title = analysis["job_title"]
        required_skills = analysis["required_skills"]
        experience_level = analysis["experience_level"]

        response = [
            f"*Job Analysis*",
            f"Position: {job_title}",
            f"Experience Level: {experience_level}",
            f"\n*Required Skills:*",
            ", ".join(required_skills),
            "\n*Matching Members:*",
        ]

        if matching_members:
            for user_id, skills in matching_members.items():
                response.append(
                    f"• <@{user_id}> - Matching skills: {', '.join(skills)}"
                )
        else:
            response.append(
                "No direct matches found. Consider reaching out to brothers to develop these skills!"
            )

        return "\n".join(response)
