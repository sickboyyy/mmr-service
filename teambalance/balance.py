import numpy as np
from itertools import combinations

from common.constants import C_SD, BETA

class Balance:
    """
    This constructs the set of unique team configurations.
    Doing this divides by 24 from the "brute force" method that tries all possible combinations
    for footmen frenzy (3v3v3v3).
    As we go from 15400 possibilities to 369600 - it's really worth doing it as runtime goes from ~1 sec to 30 secs.
    I generalized this to make it for any number of teams & number of players on the team.
    This only needs to be done "once" ever - so need to make sure it's not recalculated needlessly all the time

    Examples:

        ```python
        ratings_G = np.round(np.random.normal(1500, 300, 12),0)
        print(ratings_G)
        rds_G = np.array([90]*12)
        b = Balance()
        teams_footies = b.find_best_game(ratings_G, rds_G, '3v3v3v3')
        print(teams_footies)

        ratings_G = np.round(np.random.normal(1500, 300, 8),0)
        print(ratings_G)
        rds_G = np.array([90]*8)
        b = Balance()
        teams_4s = b.find_best_game(ratings_G, rds_G, '4v4')
        print(teams_4s)
        ```

    """

    def __init__(self):
        self.superset = {}

    def recursion(self, set_players, potential_games, num_players_per_team):
        potential_game_next = []
        for game in potential_games:
            set_players_left = set_players - set([p for team in game for p in list(team)])
            for team in combinations(set_players_left, num_players_per_team):
                game_copy = game.copy()
                game_copy.append(frozenset(team))
                potential_game_next.append(game_copy)

        return potential_game_next

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

        Args:
            ratings_game: TODO
            rds: TODO
            num_teams (int): Number of participating teams.
            num_players_per_team (int): Number of players for each team.

        Returns:
            TODO
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
        """Finds the most balanced game.

        Args:
            ratings: TODO
            rds: TODO
            game_mode (str): Game mode in the form "PvPvP" or "PonPonP" (e.g. "3v3v3v3").

        Returns:
            TODO
        """
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
