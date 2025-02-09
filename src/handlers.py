# handlers.py
# Message handlers for the bot

import re
import os
from time import sleep
from utils import log_video_process, log_error, is_file_in_use, is_admin
from settings import save_settings

# Set up message handlers for the bot
def setup_handlers(bot):

    # /start command handler
    @bot.bot.message_handler(commands=['start'])
    def send_welcome(message):
        chat_id = message.chat.id
        welcome_text = """
        🤖 Welcome! I am ready to assist you. Available settings:
        - /set_delete - enable/disable auto-deletion of messages
        - /set_caption - add a message with sender information
        - /set_link - include the original link in the message
        """
        bot.bot.send_message(chat_id, welcome_text)

    # /set_delete command handler
    @bot.bot.message_handler(commands=['set_delete'])
    def toggle_delete_message(message):
        chat_id = message.chat.id
        user_id = message.from_user.id

        if not is_admin(bot.bot, chat_id, user_id):
            bot.bot.reply_to(message, "Sorry, only an administrator can change this setting.")
            return
        
        if chat_id not in bot.settings:
            bot.settings[chat_id] = {}
        
        current = bot.settings[chat_id].get('delete_message', False)
        bot.settings[chat_id]['delete_message'] = not current
        save_settings(bot.settings_dir, chat_id, bot.settings)
        
        status = "enabled" if not current else "disabled"
        bot.bot.reply_to(message, f"Auto-deletion of messages: {status}")

    # /set_caption command handler
    @bot.bot.message_handler(commands=['set_caption'])
    def toggle_sender_caption(message):
        chat_id = message.chat.id
        user_id = message.from_user.id

        if not is_admin(bot.bot, chat_id, user_id):
            bot.bot.reply_to(message, "Sorry, only an administrator can change this setting.")
            return
        if chat_id not in bot.settings:
            bot.settings[chat_id] = {}
        
        current = bot.settings[chat_id].get('add_sender_caption', False)
        bot.settings[chat_id]['add_sender_caption'] = not current
        save_settings(bot.settings_dir, chat_id, bot.settings)
        
        status = "enabled" if not current else "disabled"
        bot.bot.reply_to(message, f"Sender information: {status}")

    # /set_link command handler
    @bot.bot.message_handler(commands=['set_link'])
    def toggle_original_link(message):
        chat_id = message.chat.id
        user_id = message.from_user.id

        if not is_admin(bot.bot, chat_id, user_id):
            bot.bot.reply_to(message, "Sorry, only an administrator can change this setting.")
            return
        if chat_id not in bot.settings:
            bot.settings[chat_id] = {}
        
        current = bot.settings[chat_id].get('include_original_link', False)
        bot.settings[chat_id]['include_original_link'] = not current
        save_settings(bot.settings_dir, chat_id, bot.settings)
        
        status = "enabled" if not current else "disabled"
        bot.bot.reply_to(message, f"Include original link: {status}")

    # Video link handler
    @bot.bot.message_handler(func=lambda message: any(platform in message.text for platform in bot.supported_platforms))
    def handle_video_link(message):
        try:
            chat_id = message.chat.id

            # Find the URL in the message
            match = re.search(r'(https?://\S+)', message.text)

            if match:
                url = match.group(1)
                log_video_process(bot.logger, message.from_user, url)
                video_path = bot.download_video(url)
                caption = ""
                chat_settings = bot.settings.get(chat_id, {})

                # Add optional caption
                if chat_settings.get('add_sender_caption', False):
                    caption += f"Sent by: {message.from_user.first_name}\n"

                # Add optional original link
                if chat_settings.get('include_original_link', False):
                    caption += f"Original link: {url}"
                
                # Send the video with the optional caption
                if caption:
                    bot.bot.send_video(message.chat.id, open(video_path, 'rb'), caption=caption.strip())
                else:
                    bot.bot.send_video(message.chat.id, open(video_path, 'rb'))
                
                # Optional deletion of original message
                if chat_settings.get('delete_message', False) and len(message.text.strip().split()) == 1:
                    bot.bot.delete_message(chat_id, message.message_id)
                
                # Wait until the file is no longer in use and then delete it
                while is_file_in_use(video_path):
                    sleep(0.1)
                os.remove(video_path)

        except Exception as e:
            log_error(bot.logger, message.from_user, url, f"Error processing video: {str(e)}")
            bot.bot.reply_to(message, f"Error processing video: {str(e)}")