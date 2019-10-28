from sqlitedict import SqliteDict
import requests
import config
import datetime
import lib.utilities as utilities
from lib.cache import Cache
from lib import pubg
import random
from lib.models import shard_map
import json

db = SqliteDict('database.sqlite', autocommit=True)
cache = Cache(db)

class Aggregator():
    def __init__(self, players, region_roles):
        self.region_roles = region_roles
        self.members = players
        self.players = utilities.flatten_member_list(players)
        self.players_key = "|".join(self.players)
        self.region = self.get_region()
        utilities.dlog("Using shard for region:", self.region)
        self.shard = shard_map[self.region]
        self.players_pubg = pubg.Api(self.players, shard=self.shard).get_players().result

    def get_region(self):
        eu = 0
        na = 0

        for member in self.members:
            if self.region_roles['na'] in member.roles:
                na += 1
            elif self.region_roles['eu'] in member.roles:
                eu += 1

        if eu == na:
            return random.choice(['eu', 'na'])
        elif eu > na:
            return "eu"
        elif eu < na:
            return "na"

    def has_reported_roster(roster_id, match_id):
        key = ["pubg_roster_match_report", match_id, roster_id]

        if cache.exists(key):
            return True
        else:
            cache.write(key, True)
            return False

    def get_match_reports(self):
        latest_match = 0
        searched_maches = {}
        latest_match = None

        for player_result in self.players_pubg:
            match_id = player_result.matches[0]['id']

            if latest_match != None and latest_match.id == match_id:
                continue

            match = pubg.Api(match_id, shard=self.shard).get_match().result

            if (latest_match == None or
                match.createdAt > latest_match.createdAt and
                match.createdAt > utilities.time_days_ago(config.MATCH_NOTIFICATION_TIME_LIMIT)
                ):
                latest_match = match

        if latest_match != None:
            roster = self.get_group_roster(latest_match, self.players)
            cache_key = ["pubg_roster_match_report", roster.id, latest_match.id]

            if roster != None and not cache.exists_or_create(cache_key):
                utilities.dlog("Found unreported latest match for a roster")
                roster.total_kills = utilities.get_participants_total_kills(roster.participants)

                return {
                    "match": latest_match,
                    "roster": roster
                }

    @staticmethod
    def get_player_stats(name):
        season = pubg.Api(name, shard=shard_map["eu"]).get_season_stats().result

        if season == None:
            return

        stats = season.squad_fpp
        stats.name = name
        return stats


    def get_group_roster(self, match, players):
        for key, roster in match.rosters.items():
            for participant in roster.participants:
                if participant.name in players:
                    return roster


    def get_stream_reports(self, time_limit):
        time_limit = utilities.time_days_ago(time_limit)
        player_reports = {}

        for player in self.players_pubg:
            endpoint = "".join(['http://api.pubg.report/v1/players/', str(player.id)])

            results = requests.get(url=endpoint)

            try:
                results = results.json()
            except json.decoder.JSONDecodeError:
                print("ERROR DECODING", results.content)
                continue

            reports = []

            for key, report in results.items():
                reports.append(report)

            sorted_reports = sorted(reports, key=lambda x: x[0]['TimeEvent'], reverse=True)

            player_reports[player.id] = {
                "reports": self.filter_twitch_reports(sorted_reports, time_limit),
                "name": player.name,
                "id": player.id,
                "knocks": 0,
                "downs": 0
            }

            for report in player_reports[player.id]['reports']:
                if report['Killer'] == player.name:
                    player_reports[player.id]['knocks'] = player_reports[player.id]['knocks'] + 1
                else:
                    player_reports[player.id]['downs'] = player_reports[player.id]['downs'] + 1

        return player_reports


    def filter_twitch_reports(self, reports, time_limit):
        notifiable_reports = []

        for report in reports:
            report = report[0]

            if report['TimeEvent'] < time_limit:
                continue

            if cache.exists_or_create(["pubg_stream_report", str(report['AttackID'])]):
                continue

            notifiable_reports.append(report)

        return notifiable_reports
