"""Random player"""

from gym_env.enums import Action


class Player:
    """Mandatory class with the player methods"""

    def __init__(self, name="Random", min_call_equity=None, min_bet_equity=None):
        """Initiaization of an agent"""
        self.equity_alive = 0
        self.name = name

        self.min_call_equity = min_call_equity
        self.min_bet_equity = min_bet_equity

        self.autoplay = True

    def action(self, action_space, observation, info):  # pylint: disable=no-self-use
        """Mandatory method that calculates the move based on the observation array and the action space."""
        _ = observation
        equity_alive = info["player_data"]["equity_to_river_alive"]

        incremen1 = 0.1
        increment2 = 0.2

        if (
            equity_alive > self.min_bet_equity + increment2
            and Action.ALL_IN in action_space
        ):
            action = Action.ALL_IN

        elif (
            equity_alive > self.min_bet_equity + incremen1
            and Action.RAISE_2POT in action_space
        ):
            action = Action.RAISE_2POT

        elif equity_alive > self.min_bet_equity and Action.RAISE_POT in action_space:
            action = Action.RAISE_POT

        elif (
            equity_alive > self.min_bet_equity - incremen1
            and Action.RAISE_HALF_POT in action_space
        ):
            action = Action.RAISE_HALF_POT

        elif equity_alive > self.min_call_equity and Action.CALL in action_space:
            action = Action.CALL

        elif Action.CHECK in action_space:
            action = Action.CHECK

        else:
            action = Action.FOLD

        return action
