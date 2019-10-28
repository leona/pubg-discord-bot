import requests
from lib.models import Shard, Query, Player, Season, SeasonStats, Match
from sqlitedict import SqliteDict
from lib.cache import Cache, CacheKey
import lib.utilities as utilities
import config
from dataclasses import dataclass
import json

db = SqliteDict('database.sqlite', autocommit=True)
cache = Cache(db)

@dataclass
class ApiError:
    not_found: str = "Not Found"
    rate_limit: str = "Rate Limit"

class Api():
    result: str = None
    headers: dict = {
      "Authorization": " ".join(["Bearer", config.PUBG_KEY]),
      "Accept": "application/vnd.api+json"
    }

    def __init__(self, param, shard=Shard.pc_eu):
        self.param = param
        self.shard = shard

    def close(self):
        db.close()

    def build_endpoint(self, query):
        return "".join([config.PUBG_ENDPOINT, self.shard, "/", query])

    def get(self, query, build_query=True):
        utilities.dlog("GET:", query)

        if build_query == True:
            query = self.build_endpoint(query)

        try:
            self.result = requests.get(url=query, headers=self.headers).json()
        except json.decoder.JSONDecodeError:
            self.result = {
                "errors": [{"title": "Rate Limit"}]
            }
            return self

        self.log_errors()

        return self

    def log_errors(self):
        if self.has_errors():
            if self.has_error(ApiError.not_found):
                utilities.dlog("PUBG API request returned 404")
            else:
                utilities.dlog("PUBG API unknown error", self.result['errors'])

    def unpack_data(self, Type, cacher=None):
        list = []

        if 'data' not in self.result:
            return self

        for raw_data in self.result['data']:
            item = Type().unpack(raw_data)
            list.append(item)

            if cacher != None:
                cacher(item)

        if len(list) > 0:
            self.result = list
        else:
            self.result = None

        return self

    def get_seasons(self):
        query = Query.seasons
        self.get(query)
        self.unpack_data(Season)
        return self

    def get_match(self):
        key = [CacheKey.pubg_match, self.param]

        if cache.exists(key):
            self.result = cache.read(key, check_exists=False)
        else:
            query = Query.match(self.param)
            self.get(query)
            self.result = Match(self.result)
            cache.write(key, self.result, expire=2)

        return self

    def get_telemetry(self):
        self.get(self.param, build_query=False)
        return self

    def get_active_season(self):
        key = [CacheKey.active_season]

        if cache.exists(key):
            return cache.read(key, check_exists=False)
        else:
            utilities.dlog("Updating active season ID")
            active_season = self.get_seasons().result[-1]
            cache.write(key, active_season, expire=utilities.hours_from_day(config.ACTIVE_SEASON_CACHE_DAYS))
            return active_season

    def get_season_stats(self):
        key = [CacheKey.player_stats, self.param.lower()]

        if cache.exists(key):
            self.result = cache.read(key, check_exists=False)
        else:
            self.get_player_id()

            if self.result == None:
                return self

            query = Query.seasonStats(self.result, self.get_active_season().id)
            self.get(query)
            self.result = SeasonStats(self.result)
            cache.write(key, self.result, expire=utilities.hours_from_day(config.PLAYER_STAT_CACHE_HOURS))

        return self

    def get_player_id(self, name=None):
        if name == None:
            name = self.param

        key = [CacheKey.player_name_ref, name.lower()]

        if cache.exists(key):
            self.result = cache.read(key, check_exists=False)
        elif not self.get_players().has_errors():
            self.result = self.result.id
        else:
            self.result = None

        return self

    def has_errors(self):
        if isinstance(self.result, dict) and 'errors' in self.result:
            return True

    def has_error(self, error):
        if self.has_errors():
            for _error in self.result['errors']:
                if _error['title'] == error:
                    return True

    def get_players(self):
        if not isinstance(self.param, list):
            singular = True
        else:
            singular = False

        if singular:
            query = Query.playersByName(self.param)
        else:
            query = Query.playersByName(",".join(self.param))

        self.get(query)

        if self.has_error(ApiError.not_found):
            return self

        def cacher(item):
            key = [CacheKey.player_name_ref, item.name.lower()]

            if cache.not_exists(key):
                cache.write(key, item.id)

        self.unpack_data(Player, cacher=cacher)

        if singular and self.result:
            self.result = self.result[0]

        return self
