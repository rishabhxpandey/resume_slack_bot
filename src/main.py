import os
from pathlib import Path

from dotenv import load_dotenv
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_bolt.async_app import AsyncApp as App

from src.parsers.resume_parser import ResumeParser
from src.slack.message_handlers import MessageHandler
from src.slack.resume_handlers import ResumeHandler

# Load environment variables
load_dotenv()

# Initialize the Slack app
app = App(token=os.environ["SLACK_BOT_TOKEN"])

# Initialize components
resume_parser = ResumeParser()
message_handler = MessageHandler(resume_parser)
resume_handler = ResumeHandler(resume_parser)

# Register handlers
app.command("/upload-resume")(resume_handler.handle_upload_command)
app.view("resume_upload_modal")(resume_handler.handle_submission)
app.event("message")(message_handler.handle_message)

if __name__ == "__main__":
    # Create resumes directory if it doesn't exist
    Path("resumes").mkdir(exist_ok=True)

    # Start the app
    handler = AsyncSocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
