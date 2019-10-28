import asyncio
import time
import discord
import threading
from lib.aggregator import Aggregator
from lib.notifications import Notifications
from lib import utilities
from sqlitedict import SqliteDict
from lib.sleeper import Sleeper
import config
from lib.models import ConfigOption
import signal
import sys

db = SqliteDict('./database.sqlite', autocommit=True)
loop = asyncio.get_event_loop()

class Listener():
    def __init__(self, config):
        self.config = config
        self.notifications = Notifications(self.config)
        self.stop_request = False

        def signal_handler(sig, frame):
                sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)


    async def run(self, guilds):
        try:
            utilities.dlog("# of active guilds: ", len(guilds))
            loop.create_task(self.loop_guilds(guilds))
            self.sleeper = Sleeper(loop)
            await self.sleeper.sleep(self.config.TICK_RATE)
        except Exception as e:
            print(e)
            print("Error raised in listener.")

        if self.stop_request != True:
            await self.run(guilds)

    async def stop(self):
        self.stop_request = True
        await self.sleeper.cancel_all()
        self.stop_request = False

    async def loop_guilds(self, guilds):
        queue = {}

        for guild in guilds:
            if utilities.should_skip_guild(guild.id):
                utilities.dlog("Skipping server:", guild.name, "because of debug mode")
                continue

            reports = self.get_guild_reports(guild)

            if reports == None:
                continue

            match_notifications = self.notifications.build_match(reports['match'], guild.members)
            stream_notifications = self.notifications.build_stream(reports['stream'], self.config.STREAM_TIME_LIMIT)

            if match_notifications != None:
                await self.send_guild_notifications(guild, match_notifications)

            if stream_notifications != None:
                await self.send_guild_notifications(guild, stream_notifications)

    async def send_guild_notifications(self, guild, queue):
        send_channel = utilities.get_guild_config(guild.id, queue['type'])

        for embed in queue['embeds']:
            utilities.dlog("Sending notification to", guild.name, "in channel", send_channel)
            text_channel = utilities.get_channel(guild.text_channels, send_channel)
            await text_channel.send(embed=embed)

    def get_guild_reports(self, guild):
        members = self.get_active_guild_members(guild)

        if members == None or len(members) == 0:
            return None

        region_roles = {
            "eu": utilities.get_role(guild.roles, "eu"),
            "na": utilities.get_role(guild.roles, "na")
        }

        aggregator = Aggregator(members, region_roles)
        match_reports = aggregator.get_match_reports()
        stream_reports = aggregator.get_stream_reports(self.config.STREAM_TIME_LIMIT)

        return {
            "match": match_reports,
            "stream": stream_reports
        }

    @staticmethod
    def get_active_guild_members(guild):
        utilities.dlog("processing guild:", guild.name)
        voice_channels = guild.voice_channels
        members = []

        listen_channel = utilities.get_guild_config(guild.id, ConfigOption.listener_channel_name)
        utilities.dlog("Getting members from channel:", listen_channel)
        for channel in voice_channels:
            if channel.name.lower() == listen_channel:
                members = members + channel.members

        return members
