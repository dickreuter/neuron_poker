"""Random player"""
import random

autplay = True  # play automatically if played against keras-rl


class Player:
    """Mandatory class with the player methods"""

    def __init__(self, env='env', name='Random'):
        """Initiaization of an agent"""
        my_import = __import__('gym_env.'+env, fromlist=['Action'])
        self.Action = getattr(my_import, 'Action')
        self.equity_alive = 0
        self.actions = []
        self.last_action_in_stage = ''
        self.temp_stack = []
        self.name = name
        self.autoplay = True

    def action(self, action_space, observation, info):  # pylint: disable=no-self-use
        """Mandatory method that calculates the move based on the observation array and the action space."""
        _ = observation  # not using the observation for random decision
        _ = info

        this_player_action_space = {self.Action.FOLD, self.Action.CHECK, self.Action.CALL, self.Action.RAISE_POT, self.Action.RAISE_HALF_POT,
                                    self.Action.RAISE_2POT}
        possible_moves = this_player_action_space.intersection(
            set(action_space))
        action = random.choice(list(possible_moves))
        return action
