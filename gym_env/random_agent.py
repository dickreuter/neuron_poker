"""Random player"""
import random

from gym_env.env import Action


class Player:
    """Mandatory class with the player methods"""

    def __init__(self, stack_size, name=None):
        """Initiaization of an agent"""
        self.stack = stack_size
        self.actions = []
        self.last_action_in_stage = ''
        self.temp_stack = []
        self.name = name

    def action(self, action_space, observation):  # pylint: disable=no-self-use
        """Mandatory method that calculates the move based on the observation array and the action space."""
        _ = observation  # not using the observation for random decision
        this_player_action_space = {Action.FOLD, Action.CHECK, Action.CALL, Action.RAISE_POT, Action.RAISE_HAlF_POT}
        possible_moves = this_player_action_space.intersection(set(action_space))
        action = random.choice(list(possible_moves))
        return action
