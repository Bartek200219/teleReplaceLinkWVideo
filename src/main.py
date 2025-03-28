# main.py
# The main entry point to run the bot

import os
from dotenv import load_dotenv
from bot import VideoLinkBot
import schedule
import time
import subprocess
import threading

def run_cookies_script():
    try:
        result = subprocess.run(["venv/bin/python", "src/get-cookies.py"], check=True, capture_output=True, text=True)
        print(f"{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error running cookies.py: {e}")
        print(f"Error output: {e.stderr}")

def main():
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        raise ValueError("No BOT_TOKEN provided. Please set the BOT_TOKEN environment variable.")
    bot = VideoLinkBot(bot_token)
    
    # Run the bot in a separate thread
    bot_thread = threading.Thread(target=bot.run)
    bot_thread.start()

    run_cookies_script()

    # Schedule the cookies script to run daily
    schedule.every().day.at("00:00").do(run_cookies_script)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    load_dotenv()
    main()