.PHONY: help

# global variables
BIN_PATH = venv/bin
YELLOW_COLOR = \033[1;33m
NO_COLOR = \033[0m

help:
	@echo "Available commands:"
	@echo "  $(YELLOW_COLOR)help$(NO_COLOR)          - Show this help"
	@echo "  $(YELLOW_COLOR)setup$(NO_COLOR)         - Set up the environment and install dependencies"
	@echo "  $(YELLOW_COLOR)run$(NO_COLOR)           - Run the bot"
	@echo "  $(YELLOW_COLOR)run-d$(NO_COLOR)         - Run the bot in a detached screen session"
	@echo "  $(YELLOW_COLOR)attach$(NO_COLOR)        - Attach to the detached screen session"
	@echo "  $(YELLOW_COLOR)kill$(NO_COLOR)          - Kill the detached screen session"

setup:
	@echo "Setting up the environment..."
	@python3 -m venv venv
	@echo "Installing dependencies..."
	$(BIN_PATH)/pip install -r requirements.txt	

run:
	@$(BIN_PATH)/python src/main.py

run-d:
	@if screen -list | grep -q "teleReplaceLinkWVideo_bot_session"; then \
		echo "The bot is already running in a detached screen session."; \
		exit 1; \
	else \
		screen -dmS teleReplaceLinkWVideo_bot_session $(BIN_PATH)/python src/main.py; \
		echo "The bot is running in detached screen session.\n\
  > To attach to the session, run $(YELLOW_COLOR)make attach$(NO_COLOR).\n\
  > To detach from the session, press $(YELLOW_COLOR)Ctrl + A, D$(NO_COLOR).\n\
  > To kill the session, run $(YELLOW_COLOR)make kill$(NO_COLOR)."; \
	fi

attach:
	@screen -r teleReplaceLinkWVideo_bot_session

kill:
	@screen -S teleReplaceLinkWVideo_bot_session -X quit
	@echo "The detached screen session has been killed."

# Default rule to show help if an unknown rule is used
.DEFAULT:
	@echo "Unknown command: '$@'"
	@$(MAKE) -s help