import lib.utilities as utilities
import datetime
from dataclasses import dataclass

@dataclass
class CacheKey:
    player_name_ref: str = "player-name-ref"
    pubg_match: str = "pubg-match"
    player_stats: str = "player-stats"
    active_season: str = "active-season"
    config_option: str = "config-option"
    
class Cache():
    def __init__(self, db):
        self.db = db

    def key(self, elements):
        return "_".join(elements)

    def exists(self, key, check_expiry=True):
        if isinstance(key, list):
            key = self.key(key)

        if key in self.db:
            utilities.dlog("Item exists in cache", key)

            if check_expiry == True:
                if self.check_expiry(key, self.db[key]) != False:
                    return True
            else:
                return True

    def exists_or_create(self, key):
        if self.exists(key):
            return True
        else:
            self.write(key, True)
            return False

    def not_exists(self, key):
        return self.exists(key) != True

    def read(self, key, check_exists=True):
        if isinstance(key, list):
            key = self.key(key)

        if (check_exists == True and self.exists(key, check_expiry=False)) or (check_exists == False):
            data = self.db[key]

            return self.check_expiry(key, data)

    def check_expiry(self, key, data):
        if isinstance(data, dict) and 'expiry' in data:
            time_now = utilities.time_now()
            if data['expiry'] < time_now:
                utilities.dlog("Deleting expired cache item", key, "Expiry:", data['expiry'], "Time:", time_now)
                self.delete(key)
                return False
            else:
                return data['value']
        else:
            return data

    def delete(self, key):
        del self.db[key]

    def write(self, key, value=True, expire=0):
        if isinstance(key, list):
            key = self.key(key)

        if expire != 0:
            utilities.dlog("Writing expirable cache item", key)
            self.db[key] = {
                "expiry": utilities.time_days_ahead(expire),
                "value": value
            }
        else:
            self.db[key] = value
