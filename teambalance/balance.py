import numpy as np
from itertools import combinations
from pydantic import BaseModel

from common.constants import C_SD, BETA

class BalanceTeamRequestBody(BaseModel):
    ratings_list: list
    rds_list: list
    gamemode: str


class BalanceTeamResponseBody(BaseModel):
    ratings_list: list
    rds_list: list


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

    def parse_game_mode(self, game_mode):
        """Parse a game mode string into number of teams and players.
        This might come useful to simplify calling generate_superset()
        externally, if we would want to generate for all available game modes
        in advance.

        Args:
            game_mode (str): Game mode in string format (e.g. "3v3v3v3")

        Returns:
            A tuple containing the number of teams and the number of players
            per team.
        """
        num_teams = game_mode.count(game_mode[0])
        num_players_per_team = int(game_mode[0])
        return (num_teams, num_players_per_team)

    def _recursion(self, set_players, potential_games, num_players_per_team):
        """Expands the set of potential_games by adding (all the possible combinations of)
           a new team. This function gets called (T-1) times where T is the number
           of teams for that game mode.

        Args:
            set_players: the set players.
            potential_games: the incomplete set of potential games.
            num_players_per_team: the number of players per team.

        Returns:
            Potential_games with one more team than before call.
        """
        potential_game_next = []
        for game in potential_games:
            set_players_left = set_players - set([p for team in game for p in list(team)])
            for team in combinations(set_players_left, num_players_per_team):
                game_copy = game.copy()
                game_copy.append(frozenset(team))
                potential_game_next.append(game_copy)

        return potential_game_next

    def generate_superset(self, num_teams, num_players_per_team):
        """Generates the set of unique games with a certain number of players
           and a certain number of players per team.

        Args:
            num_teams (int): Number of participating teams.
            num_players_per_team (int): Number of players for each team.

        Returns:
            A set that has all the unique games for that game mode.
        """
        set_players = set(i for i in range(num_teams * num_players_per_team))
        potential_games = []
        for c in combinations(set_players, num_players_per_team):
            potential_games.append([frozenset(c)])
        for k in range(1,num_teams):
            potential_games = self._recursion(set_players, potential_games, num_players_per_team)
        return set(frozenset(game) for game in potential_games)

    def _game_odds(self, ratings_game, rds, num_teams, num_players_per_team):
        """This gives the winning odds for each team for configuration of the game.

        Args:
            ratings_game: ratings of players in the potential game, ordered by team
            rds: rating deviations of players in the potential game, ordered by team
            num_teams (int): Number of participating teams.
            num_players_per_team (int): Number of players for each team.

        Returns:
            a list of length num_teams with the modeled win probability for each team as values
        """
        num_players_per_game = len(rds)
        rd_game = np.sqrt(np.sum(rds ** 2) + num_players_per_game * BETA ** 2)

        rating_teams = []
        for team_index in range(num_teams):
            #ratings of the players on the team
            cur_game_ratings = ratings_game[team_index*num_players_per_team:(team_index + 1)*num_players_per_team]
            #geometric mean of the ratings on the team
            team_rating = np.prod(np.power(cur_game_ratings, 1 / float(num_players_per_team)))
            rating_teams.append(team_rating)
        ratings_T = np.array(rating_teams)
        #winning odds from Bradley-terry model
        odds = np.exp((num_players_per_team * ratings_T) / (C_SD * rd_game)) / np.sum(np.exp((num_players_per_team * ratings_T) / (C_SD * rd_game)))
        return odds

    def _filter_constraints(self, gm_set, gm_const):
        k = 0
        teams = gm_const.split('+')
        set_teams = set()
        for team_size in teams:
            arranged_team = frozenset(k + i for i in range(int(team_size)))
            k += int(team_size)
            set_teams.add(arranged_team)
        gm_spec_set = set()
        for potential_game in gm_set:
            all_constraints = []
            for arranged_team in set_teams:
                all_constraints.append(any([arranged_team.issubset(team) for team in potential_game]))
            if all(all_constraints):
                gm_spec_set.add(potential_game)
        return gm_spec_set

    def find_best_game(self, ratings, rds, game_mode, team_constraints):
        """Finds the most balanced game.

        Args:
            ratings_game: ratings of players in the potential game
            rds: rating deviations of players in the potential game
            game_mode (str): Game mode in the form "PvPvP" or "PonPonP" (e.g. "3v3v3v3").
            team_constraints (str): A string in the form "T1+T2+T3+T4" (e.g. 1+1+2+1) that entails the AT constraints.
        Returns:
            a list with the index of the team each player should be put on
        """
        (num_teams, num_players_per_team) = self.parse_game_mode(game_mode)

        if game_mode not in self.superset:
            self.superset[game_mode] = self.generate_superset(num_teams,
                                                              num_players_per_team)
        games_set_constrained = self._filter_constraints(self.superset[game_mode], team_constraints)
        most_fair = 1
        for game in games_set_constrained:
            potential_game = [p for Team in game for p in Team]
            ratings_game = ratings[potential_game]
            odds = self._game_odds(ratings_game, rds, num_teams, num_players_per_team)
            
            # That's helpstone's metric for a fair game.
            fairness_game = np.max(odds) - np.min(odds)

            if fairness_game < most_fair:
                best_game = potential_game
                most_fair = fairness_game
        #this inverts the index so that each player, ordered as in the initial MMR list is mapped to a team
        return [int(np.ceil((best_game.index(p) + 1) / num_players_per_team)) for p in range(num_teams * num_players_per_team)]
