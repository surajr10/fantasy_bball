import requests
import json

from classes import Team, Player, Schedule, Matchup, Week, UserMatchup
from typing import Dict, Any, Optional, cast, Union, List
from functools import cached_property
from constants import team_dict
import datetime as dt
import pytz

ny_tz = pytz.timezone("America/New_York")


class League:
    fantasy_filter = {
        "players": {
            "filterSlotIds": {"value": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]},
            "filterRanksForScoringPeriodIds": {"value": [12]},
            "limit": 1200,
            "sortPercOwned": {"sortAsc": "false", "sortPriority": 1},
            "sortDraftRanks": {
                "sortPriority": 100,
                "sortAsc": "true",
                "value": "STANDARD",
            },
            "filterRanksForRankTypes": {"value": ["STANDARD"]},
            "filterStatsForTopScoringPeriodIds": {
                "value": 5,
                "additionalValue": [
                    "002021",
                    "102021",
                    "002020",
                    "012021",
                    "022021",
                    "032021",
                    "042021",
                ],
            },
        }
    }

    def __init__(self) -> None:
        with open("config.json") as config_file:
            config = json.load(config_file)
        self.url = (
            "http://fantasy.espn.com/apis/v3/games/fba/seasons/2021/segments/0/leagues/"
            + str(config["league_id"])
        )
        self.cookies = config["cookies"]
        # Find a way to determine this, probably input the user's name
        #  and cross against teams view
        self.user_tid = 9

    def get_req(
        self,
        params: Optional[Dict[str, Union[str, List[str]]]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        return requests.get(
            self.url, cookies=self.cookies, params=params, headers=headers
        ).json()

    def get_players_json(self) -> Dict[Any, Any]:
        player_json = self.get_req(
            params={"view": "kona_player_info"},
            headers={
                "x-fantasy-filter": json.dumps(self.fantasy_filter),
                "x-fantasy-platform": "kona-PROD-a5abcf16cafe5c335041277beeafcabc2a236402",
                "x-fantasy-source": "kona",
            },
        )
        return cast(Dict[Any, Any], player_json)

    @property
    def teams(self) -> Dict[int, Team]:
        team_json = self.get_req(params={"view": ["mTeam", "mRoster"]})
        teams = {}
        for team in team_json["teams"]:
            teams[team["id"]] = Team(
                league_tid=team["id"],
                location=team["location"],
                nickname=team["nickname"],
                abbr=team["abbrev"],
                waiver_rank=team["waiverRank"],
                roster=Team.parse_roster(team["roster"]),
            )
        return teams

    @cached_property
    def players(self) -> Dict[str, Player]:
        player_json = self.get_players_json()
        players = {}
        for player in player_json["players"]:
            players[player["player"]["fullName"]] = Player.from_entry(player)
        return players

    @property
    def remaining_games(self) -> Dict[int, int]:
        nba_schedule_url = "https://fantasy.espn.com/apis/v3/games/fba/seasons/2021?view=proTeamSchedules_wl"
        schedule = requests.get(nba_schedule_url).json()
        team_schedule = schedule["settings"]["proTeams"]
        games: Dict[int, int] = {team_id: 0 for team_id in team_dict}

        # Cutoff is at midnight Monday morning since games use start time
        # ESPN data recorded in terms of EST
        now = dt.datetime.now(pytz.utc).astimezone(ny_tz)
        cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff += dt.timedelta(days=7 - cutoff.weekday())

        for team in team_schedule:
            if team["abbrev"] == "FA":
                continue
            for game in team["proGamesByScoringPeriod"].values():
                # Their unix ts includes ms, which fromtimestamp doesn't support
                game_ts = game[0]["date"] // 1000
                game_date = dt.datetime.fromtimestamp(game_ts).astimezone(ny_tz)
                if now < game_date < cutoff:
                    games[team["id"]] += 1
        return games

    @cached_property
    def schedule(self) -> Schedule:
        matchup_json = self.get_req(
            params={
                "view": ["mScoreboard", "mMatchup", "mMatchupScore", "mRoster", "mTeam"]
            }
        )
        schedule = Schedule()
        for week in range(16):
            matchups = {}
            for i in range(6):
                curr_matchup = matchup_json["schedule"][week * 6 + i]

                matchups[curr_matchup["id"]] = Matchup(
                    matchup_id=curr_matchup["id"],
                    period_id=curr_matchup["matchupPeriodId"],
                    home_tid=curr_matchup["home"]["teamId"],
                    away_tid=curr_matchup["away"]["teamId"],
                    home_stat=Schedule.get_stats_from_matchup(curr_matchup["home"]),
                    away_stat=Schedule.get_stats_from_matchup(curr_matchup["away"]),
                    winner=None
                    if curr_matchup["winner"] == "UNDECIDED"
                    else curr_matchup["winner"],
                )
            if curr_matchup["winner"] != "UNDECIDED":
                schedule.last_processed_period = curr_matchup[
                    "matchupPeriodId"
                ]  # Update last processed period id
            schedule.weeks.append(Week(week_id=week, matchups=matchups))
        return schedule

    @property
    def matchup(self) -> UserMatchup:
        schedule = self.schedule
        curr_period_id = schedule.last_processed_period + 1
        curr_week = schedule.weeks[curr_period_id - 1]
        for matchup in curr_week.matchups.values():
            if matchup.home_tid == self.user_tid:
                user_stat = matchup.home_stat
                opp_stat = matchup.away_stat
                opp_tid = matchup.away_tid
            elif matchup.away_tid == self.user_tid:
                user_stat = matchup.away_stat
                opp_stat = matchup.home_stat
                opp_tid = matchup.home_tid

        assert user_stat and opp_stat

        return UserMatchup(
            matchup_id=matchup.matchup_id,
            period_id=curr_period_id,
            opp_tid=opp_tid,
            user_stat=user_stat,
            opp_stat=opp_stat,
        )
