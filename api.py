import requests
import json
from constants import team_dict 
from classes import Team, Stats, Player
from typing import Tuple, Dict

class ESPN_API:
    fantasy_filter = {
            "players":
                {
                "filterSlotIds":{"value":[0,1,2,3,4,5,6,7,8,9,10,11]},
                "filterRanksForScoringPeriodIds":{"value":[12]},
                "limit":1200,
                "sortPercOwned":{"sortAsc":"false","sortPriority":1},
                "sortDraftRanks":{"sortPriority":100,"sortAsc":"true","value":"STANDARD"},
                "filterRanksForRankTypes":{"value":["STANDARD"]},
                "filterStatsForTopScoringPeriodIds":{"value":5,"additionalValue":["002021","102021","002020","012021","022021","032021","042021"]}
                }
        }

    def __init__(self):
        with open('config.json') as config_file:
            config = json.load(config_file)
        self.url = "http://fantasy.espn.com/apis/v3/games/fba/seasons/2021/segments/0/leagues/" + str(config["league_id"])
        self.cookies = config["cookies"]
    
    def get_req(self, params=None, headers=None):
        return requests.get(
            self.url,
            cookies=self.cookies,
            params=params,
            headers=headers
        ).json()

    def get_teams(self):
        team_json = self.get_req(params={"view":"mTeam"})
        teams = {}
        for team in team_json['teams']:
            teams[team['id']] = Team(
                tid = team['id'],
                location = team['location'],
                nickname = team['nickname'],
                abbr = team['abbrev'],
                waiver_rank = team['waiverRank']
            )
        return teams

    def get_player_info(self) -> Tuple[Dict[int, Player], Dict[str, int]]:
        player_json = self.get_req(
            params = {"view": 'kona_player_info'},
            headers={
                'x-fantasy-filter': json.dumps(self.fantasy_filter),
                'x-fantasy-platform': "kona-PROD-a5abcf16cafe5c335041277beeafcabc2a236402",
                'x-fantasy-source': 'kona'
            }
        )
        players = {}
        name_to_pid = {}
        for player in player_json['players']:
            player_obj = player['player']
            players[player['id']] = Player(
                pid = player['id'],
                name = player_obj['fullName'],
                status = player['status'],
                stats = Stats.parse_stats(player_obj['stats']),
                league_tid = player['onTeamId'],
                nba_tid = player_obj['proTeamId'],
            )
            name_to_pid[player_obj['fullName']] = player['id']
        return players, name_to_pid









    # @staticmethod
    # def load_team_dict():
    #     teams = requests.get("https://site.web.api.espn.com/apis/site/v2/teams?region=us&lang=en&leagues=nba").json()
    #     team_dict = {'0': 'No Team'}
    #     for div in teams['nba']:
    #         for team in div['teams']:
    #             team_dict[team['id']] = team['shortDisplayName']
    #     return team_dict