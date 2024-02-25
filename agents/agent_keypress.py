"""manual keypress agent"""

from gym_env.enums import Action


class Player:
    """Mandatory class with the player methods"""

    def __init__(self, name='Keypress'):
        """Initiaization of an agent"""
        self.equity_alive = 0
        self.actions = []
        self.last_action_in_stage = ''
        self.temp_stack = []
        self.name = name
        self.autoplay = True

    def action(self, action_space, observation, info):  # pylint: disable=no-self-use
        """Mandatory method that calculates the move based on the observation array and the action space."""
        _ = (observation, info)  # not using the observation for random decision
        action = None
        while action is None:
            print(f"Choose action with number: {action_space}")
            getch = input()
            try:
                action = Action(int(getch))
            except:  # pylint: disable=bare-except
                pass
        return action
