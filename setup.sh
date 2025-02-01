#!/bin/bash

# Aktualizacja systemu
sudo apt-get update
sudo apt-get upgrade -y

# Instalacja niezbędnych narzędzi
sudo apt-get install -y python3-pip python3-venv screen

# Dodanie użytkownika telebot
BOT_USER="telebot"
if id "$BOT_USER" &>/dev/null; then
    echo "Użytkownik $BOT_USER już istnieje"
else
    sudo adduser --disabled-password --gecos "" $BOT_USER
    echo "$BOT_USER ALL=(ALL) NOPASSWD: /usr/bin/screen" | sudo tee -a /etc/sudoers.d/$BOT_USER
fi

# Tworzenie katalogu projektu
PROJECT_DIR="/home/$BOT_USER/teleReplaceLinkWVideo"
sudo mkdir -p "$PROJECT_DIR"
sudo chown -R $BOT_USER:$BOT_USER "$PROJECT_DIR"

# Przełączenie na użytkownika telebot i konfiguracja środowiska
sudo -u $BOT_USER bash << EOL
# Tworzenie katalogu projektu (na wypadek gdyby go brakowało)
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Tworzenie wirtualnego środowiska
python3 -m venv venv

# Aktywacja wirtualnego środowiska
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate

    # Instalacja bibliotek
    pip install telebot yt-dlp toml

    # Dezaktywacja środowiska wirtualnego
    deactivate
else
    echo "Nie udało się utworzyć wirtualnego środowiska!"
    exit 1
fi
EOL

echo "Środowisko projektu zostało utworzone pomyślnie!"

# Uprawnienia wykonawcze
chmod +x setup.sh
chmod +x start.sh
