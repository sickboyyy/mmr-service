import numpy as np
from teambalance.balance import Balance

def test_team_balance():
    ratings_G = np.round(np.random.normal(1500, 300, 12),0)
    rds_G = np.array([90]*12)

    game_mode = "3v3v3v3"

    b = Balance()
    teams_footies = b.find_best_game(ratings_G, rds_G, game_mode)

    sets = len(b.superset[game_mode])
    assert sets == 15400
