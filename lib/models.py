from dataclasses import dataclass

@dataclass
class Shard:
    pc_na: str = "pc-na"
    pc_eu: str = "pc-eu"
    pc_jp: str = "pc-jp"
    pc_kakao: str = "pc-kakao"
    pc_krjp: str = "pc-krjp"
    pc_oc: str = "pc-oc"
    pc_ru: str = "pc-ru"
    pc_sa: str = "pc-sa"
    pc_sea: str = "pc-sea"
    pc_tournament: str = "pc-tournament"

shard_map = { "eu": Shard.pc_eu, "na": Shard.pc_na }

@dataclass
class ConfigOption:
    notification_channel_high_rank: str = "notification.channel.highRank"
    notification_channel_win: str = "notification.channel.win"
    notification_channel_stream_report: str = "notification.channel.streamReport"
    listener_channel_name: str = "listener.channel.name"

@dataclass
class GameMode:
    squad_fpp: str = "squad-fpp"
    duo_fpp: str = "duo-fpp"
    solo_fpp: str = "solo-fpp"
    squad: str = "squad"
    duo: str = "duo"
    solo: str = "solo"

@dataclass
class ParticipantStat:
    DBNOs: int
    assists: int
    boosts: int
    damageDealt: int
    deathType: int
    headshotKills: int
    heals: int
    killPlace: int
    killPoints: int
    killPointsDelta: int
    killStreaks: int
    kills: int
    lastKillPoints: int
    lastWinPoints: int
    longestKill: int
    mostDamage: int
    name: int
    playerId: int
    rankPoints: int
    revives: int
    rideDistance: int
    roadKills: int
    swimDistance: int
    teamKills: int
    timeSurvived: int
    vehicleDestroys: int
    walkDistance: int
    weaponsAcquired: int
    winPlace: int
    winPoints: int
    winPointsDelta: int

    def __init__(self, data):
        for key in data:
            setattr(self, key, data[key])

@dataclass
class Participant:
    id: int
    name: str
    stats: ParticipantStat

    def __init__(self, data):
        atts = data['attributes']
        stats = atts['stats']

        self.id = data['id']
        self.name = stats['name']
        self.stats = ParticipantStat(stats)

@dataclass
class Roster:
    id: int
    rank: int
    teamId: int
    won: bool
    participants: list

    def __init__(self, data):
        atts = data['attributes']
        stats = atts['stats']
        self.id = data['id']
        self.rank = stats['rank']
        self.teamId = stats['teamId']
        self.won = atts['won'] == "true"
        self.participants = []

@dataclass
class Match:
    id: int
    gameMode: str
    isCustomMatch: bool
    createdAt: str
    duration: int
    mapName: str
    rosters: dict
    #telemetry: str
    #telemetry_id: str

    def __init__(self, json):
        data = json['data']
        atts = data['attributes']
        self.id = data['id']
        self.gameMode = atts['gameMode']
        self.isCustomMatch = atts['isCustomMatch']
        self.createdAt = atts['createdAt']
        self.duration = atts['duration']
        self.mapName = atts['mapName']
        self.rosters = {}

        included = json['included']
        rosters = {}
        participants = {}

        for _data in included:
            if _data['type'] == 'participant':
                participants[_data['id']] = Participant(_data)

        for _data in included:
            if _data['type'] == "asset" and _data['attributes']['name'] == "telemetry":
                self.telemetry = _data['attributes']['URL']
                self.telemetry_id = _data['id']

            elif _data['type'] == 'roster':
                participants_meta = _data['relationships']['participants']['data']
                self.rosters[_data['id']] = Roster(_data)

                for participant in participants_meta:
                    full_participant = participants[participant['id']]

                    self.rosters[_data['id']].participants.append(full_participant)

@dataclass
class Query:
    seasons: str = "seasons"

    def playersByName(names):
        return "".join(["players?filter[playerNames]=", names])

    def seasonStats(account_id, season_id):
        return "/".join(["players", account_id, "seasons", season_id])

    def match(id):
        return "/".join(["matches", id])

@dataclass
class Season:
    id: int = 0
    isCurrentSeason: str = str()
    isOffSeason: str = str()

    def unpack(self, json):
        atts = json['attributes']
        self.id = json['id']
        self.isCurrentSeason = atts['isCurrentSeason']
        self.isOffSeason = atts['isOffseason']
        return self

@dataclass
class Stats:
    assists: int
    bestRankPoint: float
    boosts: int
    dBNOs: int
    dailyKills: int
    dailyWins: int
    damageDealt: int
    days: int
    headshotKills: int
    heals: int
    killPoints: int
    kills: int
    longestKill: int
    longestTimeSurvived: int
    losses: int
    maxKillStreaks: int
    mostSurvivalTime: int
    rankPoints: int
    rankPointsTitle: int
    revives: int
    rideDistance: int
    roadKills: int
    roundMostKills: int
    roundsPlayed: int
    suicides: int
    swimDistance: int
    teamKills: int
    timeSurvived: int
    top10s: int
    vehicleDestroys: int
    walkDistance: int
    weaponsAcquired: int
    weeklyKills: int
    weeklyWins: int
    winPoints: int
    wins: int

    def __init__(self, data):
        for key in data:
            setattr(self, key, data[key])

    @property
    def kd(self) -> str:
        if self.roundsPlayed > 0 and self.kills > 0:
            average = self.kills / (self.roundsPlayed - self.wins)
            return round(average, 2)
        else:
            return 0

@dataclass
class SeasonStats:
    squad_fpp: Stats
    duo_fpp: Stats
    solo_fpp: Stats
    squad: Stats
    duo: Stats
    solo: Stats

    def __init__(self, json):
        data = json['data']['attributes']['gameModeStats']

        self.squad_fpp = Stats(data[GameMode.squad_fpp])
        self.duo_fpp = Stats(data[GameMode.duo_fpp])
        self.solo_fpp = Stats(data[GameMode.solo_fpp])
        self.squad = Stats(data[GameMode.squad])
        self.duo = Stats(data[GameMode.duo])
        self.solo = Stats(data[GameMode.solo])


@dataclass
class Player:
    matches: list = None
    id: int = 0
    createdAt: str = str()
    updatedAt: str = str()
    name: str = str()
    stats: str = str()

    def unpack(self, json):
        atts = json['attributes']
        self.id = json['id']
        self.name = atts['name']
        self.createdAt = atts['createdAt']
        self.updatedAt = atts['updatedAt']
        self.stats = atts['stats']
        self.matches = json['relationships']['matches']['data']
        return self



@dataclass
class testtest:
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, v: str) -> None:
        self._name = v + "123"
