from typing import Optional, Set, Dict
from dataclasses import dataclass

@dataclass
class Stat:
    points: float
    turnovers: float
    minutes: float
    fgm: float
    fga: float
    ftm: float
    fta: float
    made_threes: float
    attempted_threes: float
    off_rebounds: float
    def_rebounds: float
    rebounds: float
    assists: float
    steals: float
    blocks: float
    fouls: float
    @property
    def fg_pct(self) -> float:
        return self.fgm/self.fga

    @property
    def ft_pct(self) -> float:
        return self.ftm/self.fta
    
    @staticmethod
    def parse_stat(stat_obj):
        def from_stat(index):
            return stat_obj[index] if index in stat_obj else None

        return Stat(
            points = from_stat('0'),
            blocks = from_stat('1'),
            steals = from_stat('2'),
            assists = from_stat('3'),
            off_rebounds = from_stat('4'),
            def_rebounds = from_stat('5'),
            rebounds = from_stat('6'),
            fouls = from_stat('9'),
            turnovers = from_stat('11'),
            fgm = from_stat('13'),
            fga = from_stat('14'),
            ftm = from_stat('15'),
            fta = from_stat('16'),
            made_threes = from_stat('17'),
            attempted_threes = from_stat('18'),
            minutes = from_stat('40')
        )

        # 7,8 = ?
        # fg_pct = 19
        # ft_pct = 20
        # 3_pct = 21
        # efg = 22
    
@dataclass
class StatDict:
    avg: Stat
    total: Stat
        
@dataclass
class Stats:
    last7: StatDict
    last15: StatDict
    last30: StatDict
    s20: StatDict
    s21: StatDict
    s21_proj: StatDict

    @staticmethod
    def parse_stats(stats):
        def get_stat(stat_id):
            stat_objs = [stat for stat in stats if stat['id'] == stat_id]
            if not stat_objs:
                return None
            stat_obj = stat_objs[0]
            return StatDict(
                avg = Stat.parse_stat(stat_obj['averageStats']) if 'averageStats' in stat_obj else None, 
                total= Stat.parse_stat(stat_obj['stats']))

        return Stats(
            last7 = get_stat('012021'),
            last15 = get_stat('022021'),
            last30 = get_stat('032021'),
            s20 = get_stat('002020'),
            s21 = get_stat('002021'),
            s21_proj = get_stat('102021')
        )

@dataclass
class Player:
    pid: int
    name: str
    status: str # FREEAGENT, WAIVERS, etc.
    stats: Stats
    league_tid: int
    nba_tid: int

    games_remaining: Optional[int] = None

@dataclass
class Team:
    league_tid: int
    waiver_rank: int
    location: str
    nickname: str
    abbr: str

    roster: Optional[Dict[int, Player]] = None

    @property
    def name(self):
        return self.location + " " + self.nickname

