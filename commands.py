import lib.utilities as utilities
import urllib.request
import random
from lib.aggregator import Aggregator
import discord
from lib.notifications import Notifications
import config
from lib.cache import Cache, CacheKey
from sqlitedict import SqliteDict
from lib.models import shard_map
from lib import pubg
import subprocess

db = SqliteDict('./database.sqlite', autocommit=True)
cache = Cache(db)

async def register(command, callback, message, param=None, channel=None, delete_otherwise=False):
    if channel != None and message.channel.name != channel:
        return

    if isinstance(command, list):
        for _command in command:
            if _command == message.content[0:len(_command)]:
                rate_limit = utilities.pass_rate_limit(message.author.id, command[0])

                if rate_limit == 1:
                    await callback(message, message.content[len(_command) + 1:], param)
                elif rate_limit != 3:
                    await message.channel.send('fuck off cunt')
                break
            if delete_otherwise:
                await message.author.send(config.USE_HELP_CHANNEL_MSG)
                await message.delete()
    else:
        if command == message.content[0:len(command)]:
            rate_limit = utilities.pass_rate_limit(message.author.id, command)

            if rate_limit == 1:
                await callback(message, message.content[len(command) + 1:], param)
            elif rate_limit != 3:
                await message.channel.send('fuck off cunt')
        elif delete_otherwise:
            await message.author.send(config.USE_HELP_CHANNEL_MSG)
            await message.delete()

async def stat(message, name, param2):
    if len(name) == 0:
        name = utilities.get_member_name(message.author)

    player = Aggregator.get_player_stats(name)

    if player == None:
        print("No player found")
        await message.channel.send('No player found')
    else:
        embed = Notifications.build_stats(player)
        await message.channel.send(embed=embed)

async def insult(message, param, param2):
    contents = urllib.request.urlopen("https://insult.mattbas.org/api/insult").read().decode('utf-8')

    await message.channel.send(contents)

async def random_map(message, param, param2):
    await message.channel.send(random.choice(['Sanhok', 'Miramar', 'Vikendi', 'Erangel']))

async def last_match(message, param, param2):
    await message.channel.send(random.choice(['Sanhok', 'Miramar', 'Vikendi', 'Erangel']))

async def restart(message, param, param2):
    await message.channel.send("Restarting server")
    subprocess.run(["/sbin/reboot", "now"])

async def logs(message, param, param2):
    await message.channel.send("Last server logs")


async def image(message, param, data):
    embed = discord.Embed()
    embed.set_image(url=data['link'])
    embed.set_footer(text=" ".join(["PUBG-BOT -", data["footer"]]))
    await message.channel.send(embed=embed)

async def help(message, param, param2):
    embed = discord.Embed()
    embed.add_field(name="Help list", value=";stat <name> - Game stats lookup\n;map - Randomly generated map choice\n;face - Randomly generated faces\n;insult - Randomly generated insults\n;aim-guide - WackyJacky Scope guide", inline=True)
    embed.set_footer(text="PUBG-BOT")
    await message.channel.send(embed=embed)

async def help_manager(message, param, param2):
    embed = discord.Embed()
    embed.add_field(name="Help list", value=";register <name> <region> - PUBG account link", inline=True)
    embed.set_footer(text="PUBG-BOT")
    await message.channel.send(embed=embed)
    
async def config_set(message, param, param2):
    split_param = param.split(" ")
    key = split_param[0]
    value = param[len(key) + 1:]

    utilities.dlog("Config change request. Key:", key, "Value:", value)

    if key in config.CONFIG_OPTIONS and utilities.valid_config(value):
        cache.write([CacheKey.config_option, str(message.guild.id), key], value)
        await message.channel.send('Configuration has succesfully been stored.')
    else:
        utilities.dlog("Invalid config change request")
        await message.channel.send('Configuration change failed. Key does not exist or value is invalid.')

async def config_get(message, param, param2):
    utilities.dlog("Config read request. Key:", param)

    if param in config.CONFIG_OPTIONS:
        value = utilities.get_guild_config(message.guild.id, param)
        await message.channel.send(" ".join(['Configuration value for key:', param, "is:", value]))
    else:
        utilities.dlog("Invalid config change request")
        await message.channel.send('Configuration read failed. Key does not exist.')

async def get_id(message, param, param2):
    await message.channel.send(message.guild.id)

async def register_pubg(message, param, param2):
    if message.channel.name != "register":
        return

    params = param.split(" ")

    if len(params) != 2:
        utilities.dlog("Incorrect number of parameters")
        await message.channel.send("Incorrect number of parameters. Please include your name and whether you are EU/NA.")
        return

    name = params[0]
    region_param = params[1].lower()

    if region_param not in shard_map:
        utilities.dlog("Invalid region")
        await message.channel.send("Invalid region")
        return

    region = shard_map[region_param]
    season = pubg.Api(name, shard=region).get_season_stats().result

    if season == None:
        utilities.dlog("No season stats found")
        await message.channel.send("No season stats found. Make sure you have typed the name correctly (with capitals).")
        return

    stats = season.squad_fpp
    stats.name = name

    if stats.roundsPlayed < 30:
        utilities.dlog("You must play at least 30 rounds before being registered.")
        await message.channel.send('You must play at least 30 rounds before being registered.')
        return

    if stats.kd >= 2:
        min_kd = 2
    elif stats.kd >= 1:
        min_kd = 1
    else:
        utilities.dlog("Too low rank")
        await message.channel.send('Sorry, your KD is too low to match you with any channels.')
        return

    region_roles = {
        "eu": utilities.get_role(message.guild.roles, "eu"),
        "na": utilities.get_role(message.guild.roles, "na")
    }

    delete_roles = [
        utilities.get_role(message.guild.roles, "kd-1"),
        utilities.get_role(message.guild.roles, "kd-2"),
        region_roles['eu'],
        region_roles['na'],
    ]

    add_role = utilities.get_role(message.guild.roles, "kd-" + str(min_kd))

    try:
        for role in delete_roles:
            await message.author.remove_roles(role)

        utilities.dlog("Adding roles:", add_role, region_roles[region_param])
        await message.author.add_roles(add_role, region_roles[region_param])
    except discord.errors.Forbidden:
        utilities.dlog("Cannot set roles for:", message.author.name, "to role:", role)
    try:
        await message.author.edit(nick=stats.name)
    except discord.errors.Forbidden:
        utilities.dlog("Cannot set nickname for:", message.author.name)

    await message.channel.send('Succesfully linked. You may now join channels up to +' + str(min_kd) + ' KD.')


async def purge(message, param, param2):
    try:
        await message.channel.purge(limit=100)
    except discord.errors.Forbidden:
        await message.channel.send('Permissions required')
