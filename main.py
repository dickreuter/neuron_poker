"""
neuron poker

Usage:
  main.py random [options]
  main.py keypress [options]
  main.py consider_equity [options]

options:
  -h --help         Show this screen.
  -r --render       render screen
  --log             log file
  --screenloglevel  log level on screen
  --episodes=<>     number of episodes to play

"""

import logging

from docopt import docopt

from agents.agent_consider_equity import Player as EquityPlayer
from agents.agent_keypress import Player as KeyPressAgent
from agents.agent_random import Player as RandomPlayer
from gym_env.env import HoldemTable
from tools.helper import get_config
from tools.helper import init_logger


def command_line_parser():
    """Entry function"""
    args = docopt(__doc__)
    if args['--log']:
        logfile = args['--log']
    else:
        print("Using default log file")
        logfile = 'default'
    screenloglevel = logging.INFO if not args['--screenloglevel'] else \
        getattr(logging, args['--screenloglevel'].upper())
    _ = get_config()
    init_logger(screenlevel=screenloglevel, filename=logfile)
    print(f"Screenloglevel: {screenloglevel}")
    log = logging.getLogger("")
    log.info("Initializing program")

    num_eposodes = 1 if not args['--episodes'] else int(args['--episodes'])
    runner = Runner(render=args['--render'], num_episodes=num_eposodes)

    if args['random']:
        runner.random_agents()

    elif args['keypress']:
        runner.key_press_agents()

    elif args['consider_equity']:
        runner.consider_equity_vs_random()

    else:
        raise RuntimeError("Agrument not yet implemented")


class Runner:
    """Orchestration"""
    def __init__(self, render, num_episodes):
        """Initialize"""
        self.winner_in_episodes = []
        self.render = render
        self.env = None
        self.num_episodes = num_episodes

    def run_episode(self):
        """Run an episode"""
        self.env.reset()
        while True:
            if self.render:
                self.env.render()
            _, _, done, _ = self.env.step()

            if done:
                break

    def random_agents(self):
        """Create an environment with 6 random players"""
        num_of_plrs = 6
        self.env = HoldemTable(num_of_players=num_of_plrs, initial_stacks=500)
        for _ in range(num_of_plrs):
            player = RandomPlayer(500)
            self.env.add_player(player)

        self.run_episode()

    def key_press_agents(self):
        """Create an environment with 6 key press agents"""
        num_of_plrs = 6
        self.env = HoldemTable(num_of_players=num_of_plrs, initial_stacks=500)
        for _ in range(num_of_plrs):
            player = KeyPressAgent(500)
            self.env.add_player(player)

        self.run_episode()

    def consider_equity_vs_random(self):
        """Create 6 players, 4 of them equity based, 2 of them random"""
        self.env = HoldemTable(num_of_players=5, initial_stacks=500)
        self.env.add_player(EquityPlayer(name='equity/50/50', min_call_equity=.5, min_bet_equity=-.5))
        self.env.add_player(EquityPlayer(name='equity/50/80', min_call_equity=.8, min_bet_equity=-.8))
        self.env.add_player(EquityPlayer(name='equity/70/70', min_call_equity=.7, min_bet_equity=-.7))
        self.env.add_player(EquityPlayer(name='equity/20/30', min_call_equity=.2, min_bet_equity=-.3))
        self.env.add_player(RandomPlayer())
        self.env.add_player(RandomPlayer())

        for _ in range(self.num_episodes):
            self.run_episode()
            self.winner_in_episodes.append(self.env.winner_ix)

        print(self.winner_in_episodes)


if __name__ == '__main__':
    command_line_parser()
