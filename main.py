import os
import logging
import telebot
import yt_dlp
import re
import toml
from datetime import datetime
from time import sleep

class VideoLinkBot:
    def __init__(self, bot_token):
        # Configure logging
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
            'tiktok.com', 
            'instagram.com/reel',
            'facebook.com/share'
        ]

        self.settings_dir = 'chat_settings'
        os.makedirs(self.settings_dir, exist_ok=True)
        
        self.settings = self.load_settings()

    def _get_settings_path(self, chat_id):
        return os.path.join(self.settings_dir, f'{chat_id}_settings.toml')

    def save_settings(self, chat_id):
        path = self._get_settings_path(chat_id)
        with open(path, 'w') as f:
            toml.dump(self.settings.get(chat_id, {}), f)

    def load_settings(self):
        settings = {}
        for filename in os.listdir(self.settings_dir):
            if filename.endswith('_settings.toml'):
                chat_id = int(filename.split('_')[0])
                path = os.path.join(self.settings_dir, filename)
                with open(path, 'r') as f:
                    settings[chat_id] = toml.load(f)
        return settings

    def download_video(self, url):
        # Opcje pobierania dla Facebook
        ydl_opts = {
            'format': 'mp4',
            'outtmpl': os.path.join('downloads', 'video_%(id)s.%(ext)s'),
            'nooverwrites': True,
            'no_color': True,
            'ignoreerrors': False,
            'no_warnings': True,
            'verbose': False
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Przekształcenie linku mobilnego na standardowy
                if 'm.facebook.com' in url:
                    url = url.replace('m.facebook.com', 'www.facebook.com')
                
                info = ydl.extract_info(url, download=True)
                return ydl.prepare_filename(info)
        except Exception as e:
            self.log_error(None, url, f"Download failed: {str(e)}")
            raise


    def log_video_process(self, user, url):
        extra = {
            'user': user.id if user else 'Unknown',
            'url': url
        }
        self.logger.info('Video link processed', extra=extra)

    def log_error(self, user, url, error_message):
        extra = {
            'user': user.id if user else 'Unknown',
            'url': url
        }
        self.logger.error(error_message, extra=extra)
    
    def is_file_in_use(self, file_path):
        try:
            os.rename(file_path, file_path)
            return False
        except (IOError, PermissionError):
            return True
        
    def is_admin(self, chat_id, user_id):
        """Sprawdź, czy użytkownik jest administratorem grupy"""
        try:
            chat_member = self.bot.get_chat_member(chat_id, user_id)
            return chat_member.status in ['administrator', 'creator']
        except Exception:
            return False

    def setup_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            chat_id = message.chat.id
            welcome_text = """
    🤖 Witaj! Jestem gotowy do pomocy. Dostępne ustawienia:
    - /set_delete - włącz/wyłącz auto-usuwanie wiadomości
    - /set_caption - dodaj wiadomość z informacją o wysyłającym
    - /set_link - dołącz oryginalny link do wiadomości
    """
            self.bot.send_message(chat_id, welcome_text)

        @self.bot.message_handler(commands=['set_delete'])
        def toggle_delete_message(message):
            chat_id = message.chat.id
            user_id = message.from_user.id

            # Sprawdź uprawnienia
            if not self.is_admin(chat_id, user_id):
                self.bot.reply_to(message, "Przepraszam, tylko administrator może zmienić to ustawienie.")
                return
            
            if chat_id not in self.settings:
                self.settings[chat_id] = {}
            
            current = self.settings[chat_id].get('delete_message', False)
            self.settings[chat_id]['delete_message'] = not current
            self.save_settings(chat_id)
            
            status = "włączone" if not current else "wyłączone"
            self.bot.reply_to(message, f"Auto-usuwanie wiadomości: {status}")

        @self.bot.message_handler(commands=['set_caption'])
        def toggle_sender_caption(message):
            chat_id = message.chat.id
            user_id = message.from_user.id

            # Sprawdź uprawnienia
            if not self.is_admin(chat_id, user_id):
                self.bot.reply_to(message, "Przepraszam, tylko administrator może zmienić to ustawienie.")
                return
            if chat_id not in self.settings:
                self.settings[chat_id] = {}
            
            current = self.settings[chat_id].get('add_sender_caption', False)
            self.settings[chat_id]['add_sender_caption'] = not current
            self.save_settings(chat_id)
            
            status = "włączone" if not current else "wyłączone"
            self.bot.reply_to(message, f"Wiadomość o nadawcy: {status}")

        @self.bot.message_handler(commands=['set_link'])
        def toggle_original_link(message):
            chat_id = message.chat.id
            user_id = message.from_user.id

            # Sprawdź uprawnienia
            if not self.is_admin(chat_id, user_id):
                self.bot.reply_to(message, "Przepraszam, tylko administrator może zmienić to ustawienie.")
                return
            if chat_id not in self.settings:
                self.settings[chat_id] = {}
            
            current = self.settings[chat_id].get('include_original_link', False)
            self.settings[chat_id]['include_original_link'] = not current
            self.save_settings(chat_id)
            
            status = "włączone" if not current else "wyłączone"
            self.bot.reply_to(message, f"Dołącz oryginalny link do: {status}")

        @self.bot.message_handler(func=lambda message: any(platform in message.text for platform in self.supported_platforms))
        def handle_video_link(message):
            try:
                chat_id = message.chat.id
                match = re.search(r'(https?://\S+)', message.text)
                if match:
                    url = match.group(1)
                    
                    # Log video processing attempt
                    self.log_video_process(message.from_user, url)
                    
                    video_path = self.download_video(url)
                    
                    # Prepare caption
                    caption = ""
                    chat_settings = self.settings.get(chat_id, {})
                    if chat_settings.get('add_sender_caption', False):
                        caption += f"Sent by: {message.from_user.first_name}\n"
                    if chat_settings.get('include_original_link', False):
                        caption += f"Original link: {url}"
                    
                    # Send video
                    if caption:
                        self.bot.send_video(message.chat.id, open(video_path, 'rb'), caption=caption.strip())
                    else:
                        self.bot.send_video(message.chat.id, open(video_path, 'rb'))
                    
                    # Optional deletion of original message
                    if chat_settings.get('delete_message', False) and len(message.text.strip().split()) == 1:
                         self.bot.delete_message(chat_id, message.message_id)
                    
                    while self.is_file_in_use(video_path):
                        sleep(0.1)
                    os.remove(video_path)

            except Exception as e:
                self.log_error(message.from_user, url, f"Error processing video: {str(e)}")
                self.bot.reply_to(message, f"Error processing video: {str(e)}")

    def run(self):
        self.setup_handlers()
        self.bot.polling()

def main():
    bot = VideoLinkBot('BOT_TOKEN')
    bot.run()

if __name__ == '__main__':
    main()