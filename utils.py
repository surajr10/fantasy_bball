from typing import Dict, Any, Optional, cast, Union, List
from fantasy.classes import Team, Player, Schedule, Matchup, Week, UserMatchup


def top_players_by_minutes(espn_league, num_players=200):
    all_players = espn_league.players
    player_mins = {}
    for player in list(all_players.keys()):
        has_played = all_players[player].stats.s22
        if has_played:
            player_mins[player] = has_played.total.minutes
    sorted_player_tuples = sorted(
        player_mins.items(), key=lambda item: item[1], reverse=True)
    return dict(sorted_player_tuples[:num_players])
