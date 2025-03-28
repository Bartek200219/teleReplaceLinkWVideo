# bot.py
# Main bot class and its methods

import os
import logging
import telebot
import yt_dlp
from datetime import datetime
from time import sleep
from settings import load_settings, save_settings
from utils import log_video_process, log_error, is_file_in_use, is_admin

class VideoLinkBot:
    def __init__(self, bot_token):
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)
        log_filename = os.path.join(log_dir, f'video_bot_{datetime.now().strftime("%Y%m%d")}.log')
        
        logging.basicConfig(
            filename=log_filename, 
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s - User: %(user)s - URL: %(url)s - %(message)s'
        )
        
        self.logger = logging.getLogger()
        self.bot = telebot.TeleBot(bot_token)
        
        self.delete_original_message = False
        self.add_sender_caption = False
        self.include_original_link = False
        self.supported_platforms = [
            'youtube.com/shorts', 
            'facebook.com/reel', 
            'facebook.com/share',
            'tiktok.com', 
            'instagram.com/reel'
        ]

        self.settings_dir = 'chat_settings'
        os.makedirs(self.settings_dir, exist_ok=True)
        
        self.settings = load_settings(self.settings_dir)

    def download_video(self, url):

        # Set download options
        ydl_opts = {
            'format': 'mp4',
            'outtmpl': os.path.join('downloads', 'video_%(id)s.%(ext)s'),
            'nooverwrites': True,
            'no_color': True,
            'ignoreerrors': False,
            'no_warnings': True,
            'verbose': False
        }

        # Get the platform name from the URL
        platform = url.replace('http://', '').replace('https://', '').replace('www.', '').split('.')[0]

        # Add cookies to the request of a supported platform
        if platform in ['instagram', 'tiktok']:
            ydl_opts['cookiefile'] = os.path.join('cookies', platform + '.txt')

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:

                # Use desktop version of Facebook URL
                if 'm.facebook.com' in url:
                    url = url.replace('m.facebook.com', 'www.facebook.com')
                
                # Download the video
                info = ydl.extract_info(url, download=True)
                
                # Return the path to the downloaded video
                return ydl.prepare_filename(info) 
        except Exception as e:
            log_error(self.logger, None, url, f"Download failed: {str(e)}")
            raise

    def setup_handlers(self):
        from handlers import setup_handlers
        setup_handlers(self)

    def run(self):
        self.setup_handlers()
        self.bot.polling()