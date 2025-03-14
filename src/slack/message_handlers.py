from typing import Dict

from typing_extensions import Awaitable

from src.parsers.resume_parser import ResumeParser
from src.slack.formatters import format_error_message, format_job_matches
from src.workflows.job_workflow import analyze_job_posting


class MessageHandler:
    def __init__(self, resume_parser: ResumeParser):
        self.resume_parser = resume_parser

    async def handle_message(self, event: Dict, say) -> None:
        """Handle incoming Slack messages"""
        try:
            text = event.get("text", "")
            analysis_results = analyze_job_posting(text)

            if analysis_results["success"]:
                if analysis_results["recommendations"]:
                    await say(analysis_results["recommendations"][0])

                if "details" in analysis_results["results"]:
                    required_skills = analysis_results["results"]["details"][
                        "required_skills"
                    ]
                    matching_members = self.resume_parser.find_matching_members(
                        required_skills
                    )

                    if matching_members:
                        response = format_job_matches(matching_members)
                        await say(response)
            else:
                print(f"Error analyzing job posting: {analysis_results['error']}")

        except Exception as e:
            print(f"Error in message handler: {str(e)}")
