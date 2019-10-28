import discord
import urllib.request
from lib.listener import Listener
import lib.utilities as utilities
import commands
import config

class DiscordClient(discord.Client):
    async def on_ready(self):
        utilities.dlog('Logged on as', self.user)

        self.listener = Listener(config)
        await self.listener.run(self.guilds)

    async def on_guild_join(self, guild):
        utilities.dlog("{} has been added".format(guild.name))

        general = utilities.get_channel(guild.text_channels, "general")

        if general and general.permissions_for(guild.me).send_messages:
            await general.send('Hello {}!'.format(guild.name))

        await self.restart_listener()

    async def on_guild_remove(self, guild):
        utilities.dlog("{} has been removed".format(guild.name))
        await self.restart_listener()

    async def restart_listener(self):
        await self.listener.stop()
        await self.listener.run(self.guilds)

    async def on_message(self, message):
        if message.author == self.user:
            return

        utilities.dlog("Message received:", message.content)

        if message.author.id == config.SUPER_USER_ID:
            await commands.register(';restart', commands.restart, message)
            await commands.register(';logs', commands.logs, message)

        if utilities.should_skip_guild(message.guild.id):
            utilities.dlog("Skipping command request from:", message.guild.name, "because of debug mode")
            return

        # Admin commands
        if message.author == message.guild.owner or utilities.get_role(message.author.roles, 'bot-commander'):
            await commands.register(';config-set', commands.config_set, message)
            await commands.register(';config-get', commands.config_get, message)

        # User commands
        await commands.register([';help', ';h'], commands.help, message)
        await commands.register([';stat', ';s'], commands.stat, message)
        await commands.register([';insult', ';i'], commands.insult, message)
        await commands.register([';map', ';m'], commands.random_map, message)
        await commands.register([';face', ';f'], commands.image, message, {
            "footer":"AI Generated face - http://thispersondoesnotexist.com",
            "link": "https://thispersondoesnotexist.com/image?" + utilities.random_string()
        })
        await commands.register(';aim-guide', commands.image, message, {
            "footer": "WackyJacky Scope Guide",
            "link": "https://camo.githubusercontent.com/f76705b005b838f19aa459d25e4a8ddb2e06daa6/68747470733a2f2f692e696d6775722e636f6d2f577034364956372e706e67"
        })

client = DiscordClient()
client.run(config.DISCORD_TOKEN)
