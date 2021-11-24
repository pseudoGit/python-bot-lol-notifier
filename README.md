# python-bot-lol-notifier
Python bot on Discord for League of Legends Esports notifications

Description:
    The program runs as a bot on a Discord server. The bot will scrape the lol esports website monthly for the schedule of pro matches and sends a message to the general channel when a match is about to begin.

    The program is written completely in Python because of its simplicity and the availability of the Discord API. Personally, the program will be hosted on a free cloud hosting service.

Challenges:
    The data is scraped from a website, so its organization is determined by the website. This causes certain issues specific to the website. Events should be identified by their date, but dates are not unique, i.e. they are only identified by month and day. This requires the solution to delete the existing list of events before appending any new events to prevent duplicates. The matches on each event are not nested under their respective dates. This requires the solution to loop through every single item and prevents aggregating data by date, preventing the ability to skip if the matches have already been played. Lastly, asynchronous operations rely on the list of events to not have events that have already been played or scheduled on a date antecedent to the current date the program is using.

Installation:
    1. Clone the repository.
    2. Install requirements(see below) and setup a Discord bot.
    3. Create a .env file with your Discord tokens.
    4. Run - python3 lolNotificationBot.py


Usage:
    python3 lolNotificationBot.py

Requirements:
    python3
    pip3 install selenium
    pip3 install python-dotenv
    pip3 install discord.py
    pip3 install beautifulsoup4

Resources:
    https://github.com/mozilla/geckodriver/releases
    https://discord.com/login?redirect_to=%2Fdevelopers%2Fapplications