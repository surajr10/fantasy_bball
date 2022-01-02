from typing import Dict, Any, Optional, cast, Union, List
from classes import Team, Player, Schedule, Matchup, Week, UserMatchup

def get_top_200_by_minutes(players) -> Dict[str, float]:
    player_mins = {}
    for player in list(players.keys()):
        has_played = players[player].stats.s21
        if has_played:
            player_mins[player] = has_played.total.minutes
    sorted_player_tuples = sorted(player_mins.items(), key = lambda item: item[1], reverse=True)
    return dict(sorted_player_tuples[:200])