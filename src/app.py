import os
import re
from pathlib import Path

import spacy
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from job_analyzer import JobAnalyzer
from src.resume_parser import ResumeParser

# Load environment variables
load_dotenv()

# Initialize the Slack app
app = App(token=os.environ["SLACK_BOT_TOKEN"])

# Initialize NLP model
nlp = spacy.load("en_core_web_sm")

# Initialize our custom classes
resume_parser = ResumeParser()
job_analyzer = JobAnalyzer()


@app.command("/upload-resume")
def handle_resume_upload(ack, body, client):
    """Handle the /upload-resume command"""
    ack()
    try:
        # Open a modal for resume upload
        client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "resume_upload_modal",
                "title": {"type": "plain_text", "text": "Upload Resume"},
                "submit": {"type": "plain_text", "text": "Upload"},
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "resume_block",
                        "label": {
                            "type": "plain_text",
                            "text": "Upload your resume (PDF)",
                        },
                        "element": {
                            "type": "file_input",
                            "action_id": "resume_file",
                            "filetypes": ["pdf"],
                        },
                    }
                ],
            },
        )
    except Exception as e:
        client.chat_postEphemeral(
            channel=body["channel_id"], user=body["user_id"], text=f"Error: {str(e)}"
        )


@app.view("resume_upload_modal")
def handle_resume_submission(ack, body, client, view):
    """Handle the resume upload submission"""
    ack()
    try:
        user_id = body["user"]["id"]
        file_id = view["state"]["values"]["resume_block"]["resume_file"]["files"][0]

        # Download and save the resume
        result = client.files_info(file=file_id)
        file_url = result["file"]["url_private"]

        # Save and process resume
        resume_parser.save_resume(user_id, file_url)

        # Notify user
        client.chat_postMessage(
            channel=user_id,
            text="✅ Your resume has been successfully uploaded and processed!",
        )
    except Exception as e:
        client.chat_postMessage(
            channel=user_id, text=f"Error processing resume: {str(e)}"
        )


@app.event("message")
def handle_message(event, say):
    """Handle messages that might contain job postings"""
    try:
        text = event.get("text", "")

        # Check if the message looks like a job posting
        if job_analyzer.is_job_posting(text):
            # Extract required skills from the job posting
            required_skills = job_analyzer.extract_skills(text)

            # Find members with matching skills and identify skill gaps
            analysis = job_analyzer.analyze_job_posting(text)
            matching_members = resume_parser.find_matching_members(required_skills)

            # Prepare response message
            response = job_analyzer.prepare_response(analysis, matching_members)

            say(response)
    except Exception as e:
        say(f"Error analyzing job posting: {str(e)}")


if __name__ == "__main__":
    # Create resumes directory if it doesn't exist
    Path("resumes").mkdir(exist_ok=True)

    # Start the app
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
