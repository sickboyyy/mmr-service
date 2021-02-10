import numpy as np
from teambalance.balance import Balance



def test_team_balance_3v3v3v3():
    ratings_G = np.round(np.random.normal(1500, 300, 12),0)
    rds_G = np.array([90]*12)

    game_mode = "3v3v3v3"

    b = Balance()
    teams_footies = b.find_best_game(ratings_G, rds_G, game_mode, "1+1+1+1+1+1+1+1+1+1+1+1")

    sets = len(b.superset[game_mode])
    assert sets == 15400

def test_team_balance_4v4():
    ratings_G = np.round(np.random.normal(1500, 300, 8),0)
    rds_G = np.array([90]*8)

    game_mode = "4v4"
    b = Balance()
    at_constraints = "1+1+1+1+1+1+1+1"
    teams_4v4 = b.find_best_game(ratings_G, rds_G, game_mode, at_constraints)
    games_set_constrained = b._filter_constraints(b.superset[game_mode], at_constraints)
    sets = len(games_set_constrained)
    assert sets == 35

def test_team_balance_3plus1v4():
    ratings_G = np.round(np.random.normal(1500, 300, 8),0)
    rds_G = np.array([90]*8)

    game_mode = "4v4"

    b = Balance()
    at_constraints = "3+1+1+1+1+1"
    teams_4v4 = b.find_best_game(ratings_G, rds_G, game_mode, at_constraints)
    games_set_constrained = b._filter_constraints(b.superset[game_mode], at_constraints)
    sets = len(games_set_constrained)
    assert sets == 5

def test_team_balance_4atv4():
    ratings_G = np.round(np.random.normal(1500, 300, 8),0)
    rds_G = np.array([90]*8)

    game_mode = "4v4"

    b = Balance()
    at_constraints = "4+1+1+1+1"
    teams_4v4 = b.find_best_game(ratings_G, rds_G, game_mode, at_constraints)
    games_set_constrained = b._filter_constraints(b.superset[game_mode], at_constraints)
    sets = len(games_set_constrained)
    assert sets == 1