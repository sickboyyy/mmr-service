import numpy as np
from itertools import combinations

# TODO: Not sure what this is, could use a more descriptive name.
C_SD = 0.551328895
# TODO: Should be hardcoded to the same value as in the python mmr service
BETA = 215

class Balance:
    """
    This constructs the set of unique team configurations.
    Doing this divides by 24 from the "brute force" method that tries all possible combinations
    for footmen frenzy (3v3v3v3).
    As we go from 15400 possibilities to 369600 - it's really worth doing it as runtime goes from ~1 sec to 30 secs.
    I generalized this to make it for any number of teams & number of players on the team.
    This only needs to be done "once" ever - so need to make sure it's not recalculated needlessly all the time
    """

    def __init__(self):
        self.superset = {}

    def recursion(self, set_players, potential_games, P):
        potential_G_next = []
        for G in potential_games:
            set_players_left = set_players - set([p for team in G for p in list(team)])
            for T in combinations(set_players_left, P):
                G_T = G.copy()
                fs = frozenset(T)
                G_T.append(fs)
                potential_G_next.append(G_T)

        return potential_G_next

    def generate_superset(self, num_teams, num_players_per_team):
        superset = set()
        set_players = set(i for i in range(num_teams * num_players_per_team))
        potential_games = []
        for c in combinations(set_players, num_players_per_team):
            potential_games.append([frozenset(c)])

        counter = 1
        while counter < num_teams:
            potential_games = self.recursion(set_players, potential_games, num_players_per_team)
            counter += 1

        return set(frozenset(game) for game in potential_games)

    def game_odds(self, ratings_game, rds, num_teams, num_players_per_team):
        """This gives the winning odds for each team for configuration of the game.
        """

        num_players_per_game = len(rds)
        rd_game = np.sqrt(np.sum(rds ** 2) + num_players_per_game * BETA ** 2)

        # TODO: these following lines are a bit hell to understand, could use
        #       some breakdown.
        ratings_team = np.array([])
        for team in range(num_teams):
            cur_ratings_game = ratings_game[team*num_players_per_team:(team + 1)*num_players_per_team]
            rating = np.prod(np.power(cur_ratings_game, 1 / float(num_players_per_team)))
            np.append(ratings_team, rating)

        odds = np.exp((num_players_per_team * rating) / (C_SD * rd_game)) / \
                      np.sum(np.exp((num_players_per_team * rating) / (C_SD * rd_game)))
        return odds

    def find_best_game(self, ratings, rds, game_mode):
        """
        :param game_mode: Should be of the form "PvPvP" or "PonPonP".
        """
        # Number of teams is occurences of "v"+1

        num_teams = game_mode.count(game_mode[0])
        num_players_per_team = int(game_mode[0])

        if game_mode not in self.superset:
            self.superset[game_mode] = self.generate_superset(num_teams,
                                                              num_players_per_team)

        most_fair = 1
        for game in self.superset[game_mode]:
            potential_game = [p for Team in game for p in Team]
            ratings_game = ratings[potential_game]
            probas = self.game_odds(ratings_game, rds, num_teams, num_players_per_team)
            
            # That's helpstone's metric for a fair game.
            fairness_game = np.max(probas) - np.min(probas)

            if fairness_game < most_fair:
                best_game = potential_game
                # best_ratings = ratings_game
                most_fair = fairness_game

        # TODO: These one-liners should be avoided.
        #       In order to simplify life of maintainers, should make these
        #       as explicit as possible.
        return [int(np.ceil((best_game.index(p) + 1) / num_players_per_team)) for p in range(num_teams * num_players_per_team)]


# Example usage
# ratings_G = np.round(np.random.normal(1500, 300, 12),0)
# print(ratings_G)
# rds_G = np.array([90]*12)
# b = Balance()
# teams_footies = b.find_best_game(ratings_G, rds_G, '3v3v3v3')
# print(teams_footies)

# ratings_G = np.round(np.random.normal(1500, 300, 8),0)
# print(ratings_G)
# rds_G = np.array([90]*8)
# b = Balance()
# teams_4s = b.find_best_game(ratings_G, rds_G, '4v4')
# print(teams_4s)
