from typing import Optional
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

@dataclass
class Player:
    pid: int
    name: str
    status: str # FREEAGENT, WAIVERS, etc.
    stats: Stats