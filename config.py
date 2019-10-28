import os

MIN_RANK = 10 # Minimum rank to report
TICK_RATE = 60 # Listener interval in seconds
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
DISCORD_TOKEN_MANAGER = os.environ['DISCORD_TOKEN_MANAGER']
PUBG_KEY = os.environ['PUBG_KEY']
STREAM_TIME_LIMIT = 1 # Number of days ago a stream report can be notified about
MATCH_NOTIFICATION_TIME_LIMIT = 1 # Number of days ago a match report can be notified about
PLAYER_STAT_CACHE_HOURS = 1 # Time in hours to cache player stats
ACTIVE_SEASON_CACHE_DAYS = 1 # Time in days to cache active season ID
PUBG_ENDPOINT = "https://api.pubg.com/shards/" # Pubg API endpoint
PUBG_REPORT_ENDPOINT = "http://api.pubg.report/v1/players/" # Pubg stream reports endpoint
CONFIG_OPTIONS = { # Available config options and the default values
    "notification.channel.highRank": "pubg-report",
    "notification.channel.win": "chicken-dinners",
    "notification.channel.streamReport": "pubg-report",
    "listener.channel.name": "general",
}
DEBUG_SERVER_ID = int(os.environ['DEBUG_SERVER_ID'])
SUPER_USER_ID = int(os.environ['SUPER_USER_ID'])
WELCOME_MSG = 'Welcome to the PUBG Skill matcher server. To get started, join the "register" channel and link your account using the message ";register my_pubg_name eu" without quotes. From there, you can wait in an appropriate voice channel for other people to join and get some of that tasty chicken.'
USE_HELP_CHANNEL_MSG = 'Please only use this channel for its intended use. If you have questions, please ask in the help channel.'
