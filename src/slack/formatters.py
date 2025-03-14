from typing import Dict, List


def format_job_matches(matching_members: Dict[str, List[str]]) -> str:
    """Format matching members for Slack output"""
    matches_text = "*Matching Members:*\n"
    for user_id, skills in matching_members.items():
        matches_text += f"• <@{user_id}> - Matching skills: {', '.join(skills)}\n"
    return matches_text


def format_error_message(error: str) -> str:
    """Format error messages for Slack"""
    return f"⚠️ Error: {error}"


def format_job_analysis(analysis_results: Dict) -> str:
    """Format job analysis results for Slack"""
    return "\n".join(
        [
            "*Job Analysis Results* 📋",
            f"*Position:* {analysis_results['job_title']}",
            f"*Required Skills:* {', '.join(analysis_results['required_skills'])}",
            f"*Experience Level:* {analysis_results['experience_level']}",
        ]
    )
