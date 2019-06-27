"""
neuron poker

Usage:
  main.py random [options]
  main.py keypress [options]

options:
  -h --help         Show this screen.
  -r --render       render screen
  --log             log file
  --screenloglevel  log level on screen
"""

import logging

from docopt import docopt

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

    if args['random']:
        random_agents(render=args['--render'])

    if args['keypress']:
        key_press_agents(render=args['--render'])


def random_agents(render):
    """Create an environment with 6 random players"""
    n_players = 6
    env = HoldemTable(n_players)
    for _ in range(n_players):
        player = RandomPlayer(500)
        env.add_player(player)
    env.reset()

    while True:
        _, _, done, _ = env.step()
        if render:
            env.render()
        if done:
            break


def key_press_agents(render):
    """Create an environment with 6 key press agents"""
    n_players = 6
    env = HoldemTable(n_players)
    for _ in range(n_players):
        player = KeyPressAgent(500)
        env.add_player(player)
    env.reset()

    while True:
        _, _, done, _ = env.step()
        if render:
            env.render()
        if done:
            break


if __name__ == '__main__':
    command_line_parser()
    input()
