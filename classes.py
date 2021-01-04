from typing import Optional, Dict, List, Any, Callable, cast, Union
from dataclasses import dataclass, field


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
    rebounds: float
    assists: float
    steals: float
    blocks: float
    # attempted_threes: float
    # off_rebounds: float
    # def_rebounds: float
    # fouls: float

    @property
    def fg_pct(self) -> float:
        return self.fgm / self.fga

    @property
    def ft_pct(self) -> float:
        return self.ftm / self.fta

    @staticmethod
    def from_stat_basic(stat_obj: Dict[str, float]) -> Callable[[str], float]:
        # Player info returns a dict of pure stats
        return lambda index: stat_obj[index]

    @staticmethod
    def from_stat_matchup(
        stat_obj: Dict[str, Dict[str, Any]]
    ) -> Callable[[str], float]:
        # Matchup info returns a dict where raw stat is listed under score
        return lambda index: cast(float, stat_obj[index]["score"])

    @staticmethod
    def parse_stat(
        stat_obj: Union[Dict[str, Dict[str, Any]], Dict[str, float]],
        from_stat_type: str = "basic",
    ) -> "Stat":
        if from_stat_type == "basic":
            from_stat = Stat.from_stat_basic(cast(Dict[str, float], stat_obj))
        else:
            from_stat = Stat.from_stat_matchup(
                cast(Dict[str, Dict[str, Any]], stat_obj)
            )

        return Stat(
            points=from_stat("0"),
            blocks=from_stat("1"),
            steals=from_stat("2"),
            assists=from_stat("3"),
            rebounds=from_stat("6"),
            turnovers=from_stat("11"),
            fgm=from_stat("13"),
            fga=from_stat("14"),
            ftm=from_stat("15"),
            fta=from_stat("16"),
            made_threes=from_stat("17"),
            minutes=from_stat("40"),
            # attempted_threes = from_stat('18'),
            # fouls = from_stat('9'),
            # off_rebounds = from_stat('4'),
            # def_rebounds = from_stat('5'),
        )

        # 7,8 = ?
        # fg_pct = 19
        # ft_pct = 20
        # 3_pct = 21
        # efg = 22


@dataclass
class StatDict:
    avg: Optional[Stat]
    total: Stat


@dataclass
class Stats:
    last7: Optional[StatDict]
    last15: Optional[StatDict]
    last30: Optional[StatDict]
    s20: Optional[StatDict]
    s21: Optional[StatDict]
    s21_proj: Optional[StatDict]

    @staticmethod
    def parse_stats(stats: Dict[Any, Any]) -> "Stats":
        def get_stat(stat_id: str) -> Optional[StatDict]:
            stat_objs = [stat for stat in stats if stat["id"] == stat_id]
            if not stat_objs:
                return None
            stat_obj = stat_objs[0]
            return StatDict(
                avg=Stat.parse_stat(stat_obj["averageStats"])
                if "averageStats" in stat_obj
                else None,
                total=Stat.parse_stat(stat_obj["stats"]),
            )

        return Stats(
            last7=get_stat("012021"),
            last15=get_stat("022021"),
            last30=get_stat("032021"),
            s20=get_stat("002020"),
            s21=get_stat("002021"),
            s21_proj=get_stat("102021"),
        )


@dataclass
class Player:
    pid: int
    name: str
    status: str  # FREEAGENT, WAIVERS, etc.
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
    def name(self) -> str:
        return self.location + " " + self.nickname


@dataclass
class Matchup:
    matchup_id: int
    period_id: int
    home_tid: int
    away_tid: int
    home_stat: Stat
    away_stat: Stat

    winner: Optional[int] = None  # None if currently active


@dataclass
class Week:
    week_id: int
    matchups: Dict[int, Matchup]


@dataclass
class Schedule:
    weeks: List[Week] = field(default_factory=list)  # 16 weeks
    # Store last processed period to avoid repeat processing (1-indexed)
    last_processed_period: int = 0

    @staticmethod
    def get_stats_from_matchup(
        curr_matchup_side: Dict[str, Dict[str, Any]]
    ) -> Optional[Stat]:
        if "cumulativeScore" in curr_matchup_side:
            return Stat.parse_stat(
                curr_matchup_side["cumulativeScore"]["scoreByStat"], "matchup"
            )
        return None


@dataclass
class UserMatchup:
    matchup_id: int
    period_id: int
    opp_tid: int
    user_stat: Stat
    opp_stat: Stat
