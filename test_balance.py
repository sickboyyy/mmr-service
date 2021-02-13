import numpy as np
from teambalance.balance import Balance


def balance_tester(ratings_G, rds_G, game_mode, number_of_teams, team_constraints, expected_teams, expected_set_cardinality):
    b = Balance()
    number_of_players = len(ratings_G)
    output_teams = b.find_best_game(ratings_G, rds_G, game_mode, team_constraints)

    #this is logic to fix the permutation
    team_order = [output_teams.index(t) for t in range(1,number_of_teams+1)]
    team_permutation = [sorted(team_order).index(t)+1 for t in team_order]
    ordered_teams = [team_permutation[output_teams[p]-1] for p in range(number_of_players)]
    games_set_constrained = b._filter_constraints(b.superset[game_mode], team_constraints)
    sets = len(games_set_constrained)
    assert sets == expected_set_cardinality
    assert ordered_teams == expected_teams

def test_footies():
    ratings_G = np.array([1500, 1300, 1100, 1510, 1320, 1070, 1530, 1360, 1010, 1550, 1400, 950])
    rds_G = np.array([90]*12)
    game_mode = "3v3v3v3"
    team_constraints = "1+1+1+1+1+1+1+1+1+1+1+1"
    expected_teams = [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4]
    expected_set_cardinality = 15400
    balance_tester(ratings_G, rds_G, game_mode, 4, team_constraints, expected_teams, expected_set_cardinality)

def test_2RTvsRT():
    ratings_G = np.array([1500, 1400, 1400, 1200])
    rds_G = np.array([90]*4)
    game_mode = "2v2"
    team_constraints = "1+1+1+1"
    expected_teams = [1, 2, 2, 1]
    expected_set_cardinality = 3
    balance_tester(ratings_G, rds_G, game_mode, 2, team_constraints, expected_teams, expected_set_cardinality)

def test_2ATvs2RT():
    ratings_G = np.array([1500, 1400, 1400, 1200])
    rds_G = np.array([90]*4)
    game_mode = "2v2"
    team_constraints = "2+1+1"
    expected_teams = [1, 1, 2, 2]
    expected_set_cardinality = 1
    balance_tester(ratings_G, rds_G, game_mode, 2, team_constraints, expected_teams, expected_set_cardinality)

def test_4RTvs4RT():
    ratings_G = np.array([1900, 1500, 1400, 1400, 1400, 1400, 1300, 1100])
    rds_G = np.array([90]*8)
    game_mode = "4v4"
    team_constraints = "1+1+1+1+1+1+1+1"
    expected_teams = [1, 1, 2, 2, 2, 2, 1, 1]
    expected_set_cardinality = 35
    balance_tester(ratings_G, rds_G, game_mode, 2, team_constraints, expected_teams, expected_set_cardinality)

def test_3ATplus1v4RT():
    ratings_G = np.array([1900, 1500, 1400, 1400, 1400, 1400, 1300, 1100])
    rds_G = np.array([90]*8)
    game_mode = "4v4"
    team_constraints = "4+1+1+1+1"
    expected_teams = [1, 1, 1, 1, 2, 2, 2, 2]
    expected_set_cardinality = 1
    balance_tester(ratings_G, rds_G, game_mode, 2, team_constraints, expected_teams, expected_set_cardinality)

def test_2RTplus2ATv4RT():
    ratings_G = np.array([1900, 1500, 1400, 1400, 1400, 1400, 1300, 1100])
    rds_G = np.array([90]*8)
    game_mode = "4v4"
    team_constraints = "2+1+1+1+1+1+1"
    expected_teams = [1, 1, 2, 2, 2, 2, 1, 1]
    expected_set_cardinality = 15
    balance_tester(ratings_G, rds_G, game_mode, 2, team_constraints, expected_teams, expected_set_cardinality)
