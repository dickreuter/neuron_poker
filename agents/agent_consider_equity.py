"""Random player"""

from gym_env.env import Action


class Player:
    """Mandatory class with the player methods"""

    def __init__(self, name='Random', min_call_equity=0, min_bet_equity=0):
        """Initiaization of an agent"""
        self.equity_alive = 0
        self.name = name

        self.min_call_equity = min_call_equity
        self.min_bet_equity = min_bet_equity

    def action(self, action_space, observation):  # pylint: disable=no-self-use
        """Mandatory method that calculates the move based on the observation array and the action space."""
        equity_alive = observation['player_data'].equity_to_river_alive

        if equity_alive > self.min_bet_equity and Action.RAISE_POT in action_space:
            action = Action.RAISE_POT

        elif equity_alive > self.min_call_equity and Action.CALL in action_space:
            action = Action.CALL

        elif Action.CHECK in action_space:
            action = Action.CHECK

        else:
            action = Action.FOLD

        return action
