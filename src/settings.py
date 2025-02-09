# settings.py
# Functions for saving and loading settings for chats

import os
import toml

# Get the path to the settings file for a chat
def _get_settings_path(settings_dir, chat_id):
    return os.path.join(settings_dir, f'{chat_id}_settings.toml')

# Save settings for a chat
def save_settings(settings_dir, chat_id, settings):
    path = _get_settings_path(settings_dir, chat_id)
    with open(path, 'w') as f:
        toml.dump(settings.get(chat_id, {}), f)

# Load settings for all chats
def load_settings(settings_dir):
    settings = {}
    for filename in os.listdir(settings_dir):
        if filename.endswith('_settings.toml'):
            chat_id = int(filename.split('_')[0])
            path = os.path.join(settings_dir, filename)
            with open(path, 'r') as f:
                settings[chat_id] = toml.load(f)
    return settings