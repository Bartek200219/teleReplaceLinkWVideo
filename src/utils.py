# utils.py
# Utility functions like logging and file checks

import os
import logging

# Log a message when a video link is processed
def log_video_process(logger, user, url):
    extra = {
        'user': user.id if user else 'Unknown',
        'url': url
    }
    logger.info('Video link processed', extra=extra)

# Log an error message
def log_error(logger, user, url, error_message):
    extra = {
        'user': user.id if user else 'Unknown',
        'url': url
    }
    logger.error(error_message, extra=extra)

# Check if a file is in use
def is_file_in_use(file_path):
    try:
        os.rename(file_path, file_path)
        return False
    except (IOError, PermissionError):
        return True

# Check if a user is an admin in a chat (group or channel)
def is_admin(bot, chat_id, user_id):
    try:
        chat_member = bot.get_chat_member(chat_id, user_id)
        return chat_member.status in ['administrator', 'creator']
    except Exception:
        return False