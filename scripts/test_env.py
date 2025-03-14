import os
from dotenv import load_dotenv
import openai
from slack_bolt import App

def test_env_variables():
    # Load environment variables
    load_dotenv()
    
    # Required variables
    required_vars = [
        'OPENAI_API_KEY',
        'OPENAI_MODEL',
        'SLACK_BOT_TOKEN',
        'SLACK_APP_TOKEN',
        'SLACK_SIGNING_SECRET'
    ]
    
    # Check each variable
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        return False
    
    # Test OpenAI API key
    try:
        openai.api_key = os.getenv('OPENAI_API_KEY')
        openai.models.list()
        print("✅ OpenAI API key is valid")
    except Exception as e:
        print(f"❌ OpenAI API key error: {str(e)}")
        return False
    
    # Test Slack tokens
    try:
        app = App(token=os.getenv('SLACK_BOT_TOKEN'))
        app.client.auth_test()
        print("✅ Slack Bot Token is valid")
    except Exception as e:
        print(f"❌ Slack Bot Token error: {str(e)}")
        return False
    
    print("\n✅ All environment variables are set and valid!")
    return True

if __name__ == "__main__":
    test_env_variables() 