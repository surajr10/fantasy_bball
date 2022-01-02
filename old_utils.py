from typing import Dict, Any, Optional, cast, Union, List
from fantasy.classes import Team, Player, Schedule, Matchup, Week, UserMatchup
# def get_cat_dists(top_players, all_player_dict, cats, proj_type):
#     cat_dists = {}

#     cat_lists = {}
#     for cat in cats:
#         cat_lists[cat] = []

#     for player in top_players:
#         player_avg_stats = getattr(all_player_dict[player].stats, proj_type).avg
#         for cat in cats:
#             player_cat_stat = getattr(player_avg_stats, cat)
#             cat_lists[cat].append(player_cat_stat)

#     for cat in cats:
#         if cat in ('fgm', 'fga', 'fta', 'ftm'):
#             continue
#         cat_dists[cat] = NormalDist(mu=np.mean(cat_lists[cat]), sigma=np.std(cat_lists[cat]))


#     fgms, fgas = np.array(cat_lists['fgm']), np.array(cat_lists['fga'])
#     ftms, ftas = np.array(cat_lists['ftm']), np.array(cat_lists['fta'])
#     avg_fg_pct = sum(cat_lists['fgm']) / sum(cat_lists['fga'])
#     avg_ft_pct = sum(cat_lists['ftm']) / sum(cat_lists['fta'])
#     fg_diff = player_avg_stats.fgm / player_avg_stats.fga - avg_fg_pct
#     ft_diff = player_avg_stats.ftm / player_avg_stats.fta - avg_ft_pct

#     return cat_lists, cat_dists

def get_overall_score_v1(players, all_player_dict, cats, proj_type, cat_dists):
    player_probs = {}
    for player in players:
        prob = 1
        stats = getattr(all_player_dict[player].stats, proj_type)
#         print(f"curr player is {player} \n {stats}")
        if stats is None:
            continue  # Player hasn't played enough games to have recorded stats in ESPN data
        player_avg_stats = getattr(
            all_player_dict[player].stats, proj_type).avg
        player_probs[player] = {}
        for cat in cats:
            if cat in ('fgm', 'fga', 'fta', 'ftm'):
                continue
            cat_stat = getattr(player_avg_stats, cat)
            cat_prob = cat_dists[cat].cdf(cat_stat)
            player_probs[player][cat] = cat_prob
            prob *= cat_prob

        # yeah this is prob bad - using total fgm/fga for mean, vs. list of player fg_pct for std
        # latter seems unnecessarily noisy for mean tho?
        # fg_pct_mean = np.mean(fgms) / np.mean(fgas)
        # fg_pct_std = np.std(fgms / fgas)
        # ft_pct_mean = np.mean(ftms) / np.mean(ftas)
        # ft_pct_std = np.std(ftms / ftas)

        # cat_dists['fg_pct'] = NormalDist(mu=fg_pct_mean, sigma=fg_pct_std)
        # cat_dists['ft_pct'] = NormalDist(mu=ft_pct_mean, sigma=ft_pct_std)

        fgm = getattr(player_avg_stats, 'fgm')
        fga = getattr(player_avg_stats, 'fga')
        ftm = getattr(player_avg_stats, 'ftm')
        fta = getattr(player_avg_stats, 'fta')
        fg_pct = fgm/fga if fga else 0
        ft_pct = ftm/fta if fta else 0
        fg_prob = cat_dists['fg_pct'].cdf(fg_pct)
        ft_prob = cat_dists['ft_pct'].cdf(ft_pct)
        player_probs[player]['fg_pct'] = fg_prob
        player_probs[player]['ft_pct'] = ft_prob
        prob *= (fg_prob*ft_prob)

        player_probs[player]['total'] = prob

    return player_probs


def get_overall_score_v2(players, all_player_dict, cats, proj_type, cat_dists):
    player_probs = {}
    for player in players:
        prob = 1
        stats = getattr(all_player_dict[player].stats, proj_type)
        if stats is None:
            continue  # Player hasn't played enough games to have recorded stats in ESPN data
        player_avg_stats = getattr(
            all_player_dict[player].stats, proj_type).avg
        player_probs[player] = {}
        for cat in cats:
            if cat in ('fgm', 'fga', 'fta', 'ftm'):
                continue
            cat_stat = getattr(player_avg_stats, cat)
            cat_prob = cat_dists[cat].cdf(cat_stat)
            player_probs[player][cat] = cat_prob
            prob *= cat_prob

        fgm = getattr(player_avg_stats, 'fgm')
        fga = getattr(player_avg_stats, 'fga')
        ftm = getattr(player_avg_stats, 'ftm')
        fta = getattr(player_avg_stats, 'fta')

        # cat_dists['fg_makes'] = NormalDist(mu=np.mean(fgms), sigma=np.std(fgms))
        # cat_dists['fg_misses'] = NormalDist(mu=np.mean(fgas-fgms), sigma=np.std(fgas-fgms))
        # cat_dists['ft_makes'] = NormalDist(mu=np.mean(ftms), sigma=np.std(ftms))
        # cat_dists['ft_misses'] = NormalDist(mu=np.mean(ftas-ftms), sigma=np.std(ftas-ftms))

        fg_makes = getattr(player_avg_stats, 'fgm')
        fga = getattr(player_avg_stats, 'fga')
        ft_makes = getattr(player_avg_stats, 'ftm')
        fta = getattr(player_avg_stats, 'fta')
        fg_misses = fga - fg_makes
        ft_misses = fta - ft_makes

        fg_makes_prob = cat_dists['fg_makes'].cdf(fg_makes)
        fg_misses_prob = cat_dists['fg_misses'].cdf(fg_misses)
        ft_makes_prob = cat_dists['ft_makes'].cdf(ft_makes)
        ft_misses_prob = cat_dists['ft_misses'].cdf(ft_misses)

        player_probs[player]['fg_makes'] = fg_makes_prob
        player_probs[player]['fg_misses'] = fg_misses_prob
        player_probs[player]['ft_makes'] = ft_makes_prob
        player_probs[player]['ft_misses'] = ft_misses_prob
        prob *= (fg_makes_prob*fg_misses_prob*ft_makes_prob*ft_misses_prob)
