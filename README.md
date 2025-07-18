# Bot for Weekly News Summaries

This bot summarizes the weekly news of the Guild of Physics by parsing the raw contents of current news and feeding them to designated telegram groups on a schedule.
The bot also features the following commands:

- Viewing the weekly news at any time in either Finnish or English
- Creating the next week's news (for admins)
- Previewing the next week's news (only for admins)

## Example

![Example output](https://user-images.githubusercontent.com/7860886/129439552-33341bc9-7403-4da5-89c2-40a85424ce04.png)

## Running the bot

You can run the bot by building a Python environment and running it there or by running the preconfigured docker-compose service.
Common steps:

1. Obtain a bot token from the [Bot Father](https://t.me/botfather)

### Using Python

1. Running this bot requires python3 and virtualenv packages. You can install virtualenv with
   ```commandline
   python3 -m pip install --user virtualenv
   ```
   or you can install it globally without --user flag.
2. Create a virtual environment and prepare it by activating and installing dependencies with the following commands:
   ```commandline
   python3 -m venv env
   source env/bin/activate
   pip install -r requirements.txt
   ```
3. Start the bot in the environment that was created by running
   ```commandline
   python3 bot.py
   ```

### Using docker-compose

(pre) If you have created these configurations before and have made changes to the bot files, you should rebuild the image by running
`  docker compose -f docker-compose.yml build
 `

1. Set the environment variables in a `bot.env`.
   Example contents of the `bot.env`-file:
   `commandline
TIEDOTE_BOT_TOKEN=gmU8lKWwuxIIKju
TIEDOTE_BOT_ADMINS=username1,username2
COMMUNICATIONS_OFFICER=name
FINNISH_CHANNELS="channelId1,channelId2"
ENGLISH_CHANNELS="channelId3,channelId4"
`
2. (optional) Set a symlink from wordpress viikkotiedote folder to mails in root. This way generated weekly news are directly added to Wordpress.
3. Start the bot by running
   ```commandline
   docker compose -f docker-compose.yml up -d
   ```
4. Stop the bot and clean the environment by running
   ```commandline
   docker compose -f docker-compose.yml down
   ```
