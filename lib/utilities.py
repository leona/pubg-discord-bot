import discord
import random
import string
import datetime
import re
import config
from sqlitedict import SqliteDict
from lib.cache import Cache, CacheKey
import os

db = SqliteDict('./database.sqlite', autocommit=True)
cache = Cache(db)

def should_skip_guild(id):
    if 'DEBUG' in os.environ and id != config.DEBUG_SERVER_ID:
        return True
    elif 'DEBUG' not in os.environ and id == config.DEBUG_SERVER_ID:
        return True

def random_string(length=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def get_member(members, name):
    for member in members:
        if get_member_name(member) == name:
            return member

def get_map_name(name):
    maps = {
        "Savage_Main": "Sanhok",
        "DihorOtok_Main": "Vikendi",
        "Desert_Main": "Miramar",
        "Erangel_Main": "Erangel"
    }

    return maps[name]

def get_participants_total_kills(participants):
    total_kills = 0

    for participant in participants:
        total_kills = total_kills + participant.stats.kills

    return total_kills

def get_match_telemetry_link(match):
    return "".join(["https://pubg.sh/", match['roster'].participants[0].name, "/steam/", match['match'].id])

def valid_config(value):
    return bool(re.match("^[A-Za-z0-9-]*$", value))

def get_channel(channels, name):
    try:
        return list(filter(lambda x: x.name.lower() == name,  channels))[0]
    except:
        dlog("Failed to find {} channel".format(name))
        return

def get_role(roles, name):
    try:
        return list(filter(lambda x: x.name.lower() == name,  roles))[0]
    except:
        return

def flatten_member_list(members):
    players = []

    for member in members:
        players.append(get_member_name(member))

    return players

def get_guild_config(guild_id, config_key):
    if config_key in config.CONFIG_OPTIONS:
        key = [CacheKey.config_option, str(guild_id), config_key]

        if cache.exists(key):
            return cache.read(key, check_exists=False)
        else:
            return config.CONFIG_OPTIONS[config_key]

def get_member_name(member):
    if member.nick != None:
        return member.nick
    else:
        return member.name

def time_days_ago(num_days):
    return (datetime.datetime.now() - datetime.timedelta(days=num_days)).isoformat()

def time_days_ahead(num_days):
    return (datetime.datetime.now() + datetime.timedelta(days=num_days)).isoformat()

def time_now():
    return datetime.datetime.now().isoformat()

def hours_from_day(hours):
    return (1 / 24) * hours

def dlog(*args):
    args = ("--->",)+args+("",)
    print(*args)

rate_limits = {}

def pass_rate_limit(id, task, exec_limit=5, time_limit=1):
    if task not in rate_limits:
        rate_limits[task] = {}

    if id not in rate_limits[task]:
        rate_limits[task][id] = {
            "counter": 0,
            "end_time": time_days_ahead(((1 / 24) / 60) * time_limit)
        }

        return 1

    if time_now() > rate_limits[task][id]['end_time']:
        del rate_limits[task][id]
        return 1

    rate_limits[task][id]['counter'] += 1

    if rate_limits[task][id]['counter'] == exec_limit:
        return 2
    if rate_limits[task][id]['counter'] > exec_limit:
        return 3


    return 1
