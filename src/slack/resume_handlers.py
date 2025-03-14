from typing import Dict

from slack_bolt.app.async_app import AsyncApp
from typing_extensions import Awaitable

from src.parsers.resume_parser import ResumeParser
from src.slack.formatters import format_error_message


class ResumeHandler:
    def __init__(self, resume_parser: ResumeParser):
        self.resume_parser = resume_parser

    async def handle_upload_command(self, ack, body, client) -> None:
        """Handle /upload-resume command"""
        await ack()
        try:
            await client.views_open(
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
            await client.chat_postEphemeral(
                channel=body["channel_id"],
                user=body["user_id"],
                text=format_error_message(str(e)),
            )

    async def handle_submission(self, ack, body, client, view) -> None:
        """Handle resume upload submission"""
        await ack()
        try:
            user_id = body["user"]["id"]
            file_id = view["state"]["values"]["resume_block"]["resume_file"]["files"][0]

            result = await client.files_info(file=file_id)
            file_url = result["file"]["url_private"]

            await self.resume_parser.save_resume(user_id, file_url)

            await client.chat_postMessage(
                channel=user_id,
                text="✅ Your resume has been successfully uploaded and processed!",
            )
        except Exception as e:
            await client.chat_postMessage(
                channel=user_id, text=format_error_message(str(e))
            )
