import requests
import json

class ESPN_API:
    fantasy_filter = {
            "players":
                {"filterStatus": {"value": ["FREEAGENT","WAIVERS"]},
                "filterSlotIds":{"value":[0,1,2,3,4,5,6,7,8,9,10,11]},
                "filterRanksForScoringPeriodIds":{"value":[12]},
                "limit":1000,
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
    

    def get_player_info(self):
        return requests.get(
            self.url,
            params = {"view": kona_player_info},
            headers={
                'x-fantasy-filter': json.dumps(fantasy_filter),
                'x-fantasy-platform': "kona-PROD-a5abcf16cafe5c335041277beeafcabc2a236402",
                'x-fantasy-source': 'kona'
            }
        ).json()

    
