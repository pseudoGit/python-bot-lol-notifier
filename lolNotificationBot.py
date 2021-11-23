#! python3
# lolNotificationBot.py
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from dotenv import load_dotenv
import os, discord, datetime, asyncio, bs4

"""
Event - A date and the list of matches on that date 
"""
class Event:
    def __init__(self, date, matches):
        self.date = date
        self.matches = matches
        self.played = False
        
    def appendMatch(self, match):
        self.matches.append(match)

    def printEvent(self):
        print(f"{self.date} - Played Status: {self.played}")
        for match in self.matches:
            match.printMatch()

"""
Match - The match time, team scores and names
"""
class Match:
    def __init__(self, time, t1s, t2s, t1n, t2n):
        self.time = time
        self.t1s = t1s
        self.t2s = t2s
        self.t1n = t1n
        self.t2n = t2n
    
    def matchInfo(self):
        return f"{self.time} - {self.t1n} vs {self.t2n}"

    def printMatch(self):
        print(f"{self.time} - {self.t1n}: {self.t1s} vs {self.t2n}: {self.t2s}")

listOfEvents = []

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

"""
Display when bot successfully connects.
"""
@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break
    print(f"{client.user} is connected to the following guild: "
          f"{guild.name}(id: {guild.id})")

"""
Scrape lol esports website for scheduled big region matches once a month.
"""
@client.event
async def scrape_schedule():
    # Initialize the date since the bot last scraped.
    lastScrapedDate = datetime.datetime.utcfromtimestamp(0) 

    while (True):
        await client.wait_until_ready()
        # Scrape if the bot has not already scraped this month.
        today = datetime.datetime.now()
        print("Waiting for scrape")
        if lastScrapedDate.year < today.year or lastScrapedDate.month < today.month:
            # Update the date since the bot last scraped.
            lastScrapedDate = today

            # Clear the existing list of events
            global listOfEvents 
            listOfEvents = []

            options = Options()
            options.headless = True
            driver = webdriver.Firefox(options=options)
            # Scrape from lolesports website: https://lolesports.com/schedule?leagues=worlds,lcs,lec,lck,lpl,msi
            lolUrl = "https://lolesports.com/schedule?leagues=worlds,lcs,lec,lck,lpl,msi"
            driver.get(lolUrl)
            lolSoup = bs4.BeautifulSoup(driver.page_source, 'html.parser')

            # Get each date and their list of matches.
            for d1 in lolSoup.find('div', class_='Event').children:
                if isinstance(d1, bs4.element.Tag):
                    if d1.get('class')[0] == 'EventDate':
                        for d2 in d1:
                            for d3 in d2:
                                if isinstance(d3, bs4.element.Tag):
                                    if d3.get('class')[0] == 'monthday':
                                        # Store the date into a list of events and make a list of matches per event.
                                        event = Event(d3.string, [])
                                        listOfEvents.append(event)
                    if d1.get('class')[0] == 'EventMatch':
                        for d2 in d1:
                            for d3 in d2:
                                if isinstance(d3, bs4.element.Tag):
                                    if (d3.get('class')[0] == 'EventTime'):
                                        # Store the match time.
                                        time = d3.find('span', class_='hour').string + " " \
                                               + d3.find('span', class_='ampm').string
                                    else:
                                        # Store the match info: T1score | T2score | T1name | T2name.
                                        for d4 in d3:
                                            if isinstance(d4, bs4.element.Tag):
                                                if (d4.get('class')[0] == 'score'):
                                                    t1s = d4.find('span', class_='scoreTeam1').string
                                                    t2s = d4.find('span', class_='scoreTeam2').string
                                                if (len(d4.get('class')) > 1 and d4.get('class')[1] == 'team1'):
                                                    t1n = d4.find('span', class_='tricode').string
                                                if (len(d4.get('class')) > 1 and d4.get('class')[1] == 'team2'):
                                                    t2n = d4.find('span', class_='tricode').string
                                        if d3.get('class')[0] == 'teams':
                                            match = Match(time, t1s, t2s, t1n, t2n)
                                            # Check if any matches have been played and only add unplayed matches.
                                            event.played = (t1s != '0' or t2s != '0')
                                            if not event.played:
                                                event.appendMatch(match)
            driver.quit()
        else:
            # Sleep 1 day before checking again.
            await asyncio.sleep(864000)

"""
Check the list of events and notifies the guild.
"""
@client.event
async def match_reminder():
    while (True):
        await client.wait_until_ready()

        global listOfEvents

        # Check that the list is not empty
        if not listOfEvents:
            await asyncio.sleep(864000)
        else:
            # Get the oldest event listed
            currentEvent = listOfEvents.pop(0)

            eventDate = datetime.datetime.strptime(currentEvent.date, '%B %d')
            today = datetime.datetime.now()

            # Loop until the event is scheduled for today
            while today.month != eventDate.month and today.day != eventDate.day:
                await asyncio.sleep(864000)

            # Loop through every match on the present event date
            for currentMatch in currentEvent.matches:
                    # Loop until the match is being played soon, i.e. within 30 minutes of the start time.
                    startTime = datetime.datetime.strptime(currentMatch.time, '%I %p')
                    notifyTime = startTime - datetime.timedelta(minutes=30)
                    
                    while not (datetime.datetime.now().time() > notifyTime.time() and datetime.datetime.now().time() < startTime.time()):
                        # Sleep for 15 minutes.
                        await asyncio.sleep(900)

                    # Send message on Discord
                    channel = discord.utils.get(client.guilds[0].channels, name='general')
                    announcement = "Match about to begin: " + currentMatch.matchInfo()
                    await channel.send(content=announcement)

client.loop.create_task(scrape_schedule())
client.loop.create_task(match_reminder())

client.run(TOKEN)
