# AKPsi Resume Bot

A Slack bot for managing fraternity member resumes and providing insights on job postings.

## Features
- Resume storage and management for fraternity members
- Job posting analysis
- Skills gap identification
- Member recommendations based on required skills

## Setup Instructions

1. Create a `.env` file with your Slack credentials:
```
SLACK_BOT_TOKEN=your-bot-token
SLACK_APP_TOKEN=your-app-token
```

2. Install dependencies:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

3. Create a `resumes` directory in the project root:
```bash
mkdir resumes
```

4. Run the bot:
```bash
python app.py
```

## Usage
- Upload resumes using `/upload-resume` command
- Post job listings in any channel where the bot is present
- The bot will automatically analyze job postings and provide insights

## Security Note
All resumes are stored locally in the `resumes` directory. Ensure proper access controls are in place. 