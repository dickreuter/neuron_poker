"""manual keypress agent"""

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
        action = None
        while action is None:
            print(f"Choose action with number: {action_space}")
            try:
                getch = input()
                action = Action(int(getch))
            except:  # pylint: disable=bare-except
                print("Choice not available.")
        return action
