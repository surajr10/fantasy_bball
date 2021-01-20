from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass, field
from constants import stat_id_to_name


@dataclass
class Stat:
    points: float
    turnovers: float
    minutes: float
    games_played: int
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
    def parse_stat(stat_obj: Dict[str, float]) -> "Stat":
        # The 0 is necessary cuz Gobert's bum ass doesn't even have the threes stat in the json
        from_stat: Callable[[str], float] = (
            lambda index: stat_obj[index] if index in stat_obj else 0
        )
        return Stat(**{name: from_stat(idx) for idx, name in stat_id_to_name.items()})  # type: ignore


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

            # One case is rookie who have empty stats for last season, might be others
            if not stat_obj["stats"]:
                return None
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
    injured: bool
    stats: Stats
    league_tid: int
    nba_tid: int

    games_remaining: Optional[int] = None

    @staticmethod
    def from_entry(player_obj: Dict[str, Any]) -> "Player":
        player = player_obj["player"]
        return Player(
            pid=player["id"],
            name=player["fullName"],
            status=player_obj["status"],
            injured=player["injured"],
            stats=Stats.parse_stats(player["stats"]),
            league_tid=player_obj["onTeamId"],
            nba_tid=player["proTeamId"],
        )


@dataclass
class Team:
    league_tid: int
    waiver_rank: int
    location: str
    nickname: str
    abbr: str
    roster: Dict[str, Player]

    @property
    def name(self) -> str:
        return self.location + " " + self.nickname

    @staticmethod
    def parse_roster(roster: Dict[str, Any]) -> Dict[str, Player]:
        players: Dict[str, Player] = {}
        for entry in roster["entries"]:
            player_entry = entry["playerPoolEntry"]
            players[player_entry["player"]["fullName"]] = Player.from_entry(
                player_entry
            )
        return players


@dataclass
class Matchup:
    matchup_id: int
    period_id: int
    home_tid: int
    away_tid: int
    home_stat: Optional[Stat]
    away_stat: Optional[Stat]

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
        # Only available for current games
        if "rosterForMatchupPeriod" in curr_matchup_side:
            stats = {name: 0 for name in stat_id_to_name.values()}
            for entry in curr_matchup_side["rosterForMatchupPeriod"]["entries"]:
                stats_obj = entry["playerPoolEntry"]["player"]["stats"]
                # Lineup slots can have no players and thus be missing stat info
                if stats_obj:
                    stats_obj = stats_obj[0]["stats"]
                    for stat_id, name in stat_id_to_name.items():
                        stats[name] += stats_obj[stat_id]
            return Stat(**stats)
        # Only available for past games
        elif "cumulativeScore" in curr_matchup_side:
            return Stat.parse_stat(
                {
                    stat_idx: stat["score"]
                    for stat_idx, stat in curr_matchup_side["cumulativeScore"][
                        "scoreByStat"
                    ].items()
                }
            )
        return None


@dataclass
class UserMatchup:
    matchup_id: int
    period_id: int
    opp_tid: int
    user_stat: Stat
    opp_stat: Stat
