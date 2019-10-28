import discord
import urllib.request
from lib.listener import Listener
import lib.utilities as utilities
import commands
import config
import signal
import sys

class DiscordClient(discord.Client):
    async def on_ready(self):
        utilities.dlog('Logged on as', self.user)

    async def on_member_join(self, member):
        #role = utilities.get_role(member.guild.roles, "unregistered")
        #await member.add_roles()
        await member.send(config.WELCOME_MSG)

    async def on_voice_state_update(self, member, before, after):
        ignore_channels = ['afk']

        if after.channel and after.channel.name not in ignore_channels:
            channel_length = len(after.channel.category.channels)

            if len(after.channel.members) == 1:
                await member.guild.create_voice_channel(name="squad", category=after.channel.category, user_limit=4)

            new_category = after.channel.category

        if before.channel and before.channel.name not in ignore_channels:
            channel_length = len(before.channel.category.channels)

            if len(before.channel.members) == 0 and channel_length > 1:
                await before.channel.delete()

    async def on_guild_join(self, guild):
        utilities.dlog("{} has been added".format(guild.name))

    async def on_guild_remove(self, guild):
        utilities.dlog("{} has been removed".format(guild.name))

    async def on_message(self, message):
        if message.author == self.user:
            return

        utilities.dlog("Message received:", message.content)

        if message.author == message.guild.owner or utilities.get_role(message.author.roles, 'bot-commander'):
            await commands.register(';config-set', commands.config_set, message)
            await commands.register(';config-get', commands.config_get, message)

        if message.author == message.guild.owner:
            await commands.register(';purge', commands.purge, message, self.user)
            await commands.register(';get-id', commands.get_id, message, self.user)

        if utilities.should_skip_guild(message.guild.id):
            utilities.dlog("Skipping command request from:", message.guild.name, "because of debug mode")
            return

        # Admin commands
        #if message.author == message.guild.owner or utilities.get_role(message.author.roles, 'bot-commander'):
            #await commands.register(';config-set', commands.config_set, message)
            #await commands.register(';config-get', commands.config_get, message)
        await commands.register([';help', ';h'], commands.help_manager, message)

        await commands.register(';register', commands.register_pubg, message, param=client, channel="register", delete_otherwise=True)



client = DiscordClient()
client.run(config.DISCORD_TOKEN_MANAGER)
