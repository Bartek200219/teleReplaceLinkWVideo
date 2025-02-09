# teleReplaceLinkWVideo
 
## Requirements

- Python 3.7 or later

## Setup

1. Go to the repository's root directory:

   ```bash
    cd path/to/teleReplaceLinkWVideo
    ```
  
2. Create a virtual environment and install required packages:

   ```bash
    make setup
    ```

3. Get the bot API token from the [@BotFather](https://t.me/BotFather) and put it in the `.env` file:

   ```bash
   echo "BOT_TOKEN=your_bot_api_token" > .env
   ```
   By default, **Group Privacy** is enabled for bots. To use bot in groups, this setting has to be turned off:<br/>
   *[@BotFather](https://t.me/BotFather) -> /mybots -> @your-bot -> Bot Settings -> Group Privacy -> Turn off*

4. Optionally, if you want your bot to be able to view restricted content, add your Instagram & TikTok usernames and passwords to the `.env`. You can use the [template file](example.env) as a reference. 

   Unfortunately, to log in to TikTok, you need to bypass a captcha which requires an API key from [sadcaptcha.com](https://sadcaptcha.com/), a paid service.

5. Run the bot in the current terminal:

   ```bash
    make run
    ```

   Or run in detached mode:

   ```bash
    make run-d
    ```

   All available commands can be found by running:

   ```bash
    make help
    ```
