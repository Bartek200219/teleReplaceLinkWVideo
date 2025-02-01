#!/bin/bash

# Nazwa użytkownika, pod którym będzie uruchamiany bot
BOT_USER="telebot"

# Katalog projektu dla użytkownika telebot
PROJECT_DIR="/home/$BOT_USER/teleReplaceLinkWVideo"

# Przełączenie na użytkownika telebot i uruchomienie skryptu
sudo -u $BOT_USER bash -c "
cd $PROJECT_DIR
source venv/bin/activate
screen -dmS bot_session python3 main.py
"

echo "Bot został uruchomiony w tle w sesji screen!"