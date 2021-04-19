"""
neuron poker

Usage:
  main.py selfplay random [options]
  main.py selfplay keypress [options]
  main.py selfplay consider_equity [options]
  main.py selfplay equity_improvement --improvemest_rounds=<> [options]
  main.py selfplay dqn_train [options]
  main.py selfplay dqn_play [options]
  main.py learn_table_scraping [options]

options:
  -h --help                 Show this screen.
  -r --render               render screen
  -c --use_cpp_montecarlo   use cpp implementation of equity calculator. Requires cpp compiler but is 500x faster
  -f --funds_plot           Plot funds at end of episode
  --log                     log file
  --env=<>                  Name of the enviornment version being used, 'v0' is
  --players=<>              Type of players, [0,0,(.2,.3)] : 2 random and 1 .2/.3 equity player
  --name=<>                 Name of the saved model
  --agent=<>                Agent to use, 'name of agent file in agents/', ex dqn_agent
  --screenloglevel=<>       log level on screen
  --episodes=<>             number of episodes to play
  --stack=<>                starting stack for each player [default: 500].
  --load=<>                 whether to load a model, Bool, doesn't support extended training yet
"""

import logging

import gym
import numpy as np
import pandas as pd
from docopt import docopt

import importlib

from gym_env.env import PlayerShell
from tools.helper import get_config
from tools.helper import init_logger

from agents.agent_consider_equity import Player as EquityPlayer
from agents.agent_random import Player as RandomPlayer

# pylint: disable=import-outside-toplevel


def command_line_parser():
    """Entry function"""
    args = docopt(__doc__)
    if args['--log']:
        logfile = args['--log']
    else:
        print("Using default log file")
        logfile = 'default'
    model_name = args['--name'] if args['--name'] else 'dqn1'
    env_name = args['--env'] if args['--env'] else 'v0'
    screenloglevel = logging.INFO if not args['--screenloglevel'] else \
        getattr(logging, args['--screenloglevel'].upper())
    _ = get_config()
    init_logger(screenlevel=screenloglevel, filename=logfile)
    print(f"Screenloglevel: {screenloglevel}")
    log = logging.getLogger("")
    log.info("Initializing program")

    if args['selfplay']:
        num_episodes = 1 if not args['--episodes'] else int(args['--episodes'])
        agent = args['--agent'] if args['--agent'] else None
        players = eval(args['--players']) if args['--players'] else [0]
        load = args['--load'] if args['--load'] else False
        render = args['--render']
        use_cpp_montecarlo = args['--use_cpp_montecarlo']
        funds_plot = args['--funds_plot']

        print(args)
        runner = SelfPlay(render, num_episodes,
                          use_cpp_montecarlo,
                          funds_plot,
                          model_name, agent, env_name,
                          players,
                          load,
                          stack=int(args['--stack']))

        if args['random']:
            runner.random_agents()

        elif args['keypress']:
            runner.key_press_agents()

        elif args['consider_equity']:
            runner.equity_vs_random()

        elif args['equity_improvement']:
            improvement_rounds = int(args['--improvement_rounds'])
            runner.equity_self_improvement(improvement_rounds)

        elif args['dqn_train']:
            runner.dqn_agent('train')

        elif args['dqn_play']:
            runner.dqn_agent('play')

    else:
        raise RuntimeError("Argument not yet implemented")


class SelfPlay:
    """Orchestration of playing against itself"""

    def __init__(self, render, num_episodes, use_cpp_montecarlo, funds_plot,
                 model_name, agent, env_name,
                 players, load, stack=500):
        """Initialize"""
        self.winner_in_episodes = []
        self.use_cpp_montecarlo = use_cpp_montecarlo
        self.funds_plot = funds_plot
        self.render = render
        self.env = None
        self.num_episodes = num_episodes
        self.stack = stack
        self.log = logging.getLogger(__name__)
        self.players = players
        self.agent = agent
        self.model_name = model_name
        self.env_name = env_name
        self.load = load

    def random_agents(self):
        """Create an environment with 6 random players"""
        from agents.agent_random import Player as RandomPlayer
        env_name = 'neuron_poker-v0'
        num_of_plrs = 2
        self.env = gym.make(
            env_name, initial_stacks=self.stack, render=self.render)
        for _ in range(num_of_plrs):
            player = RandomPlayer()
            self.env.add_player(player)

        self.env.reset()

    def key_press_agents(self):
        """Create an environment with 6 key press agents"""
        from agents.agent_keypress import Player as KeyPressAgent
        env_name = 'neuron_poker-v0'
        num_of_plrs = 2
        self.env = gym.make(
            env_name, initial_stacks=self.stack, render=self.render)
        for _ in range(num_of_plrs):
            player = KeyPressAgent()
            self.env.add_player(player)

        self.env.reset()

    def equity_vs_random(self):
        """Create 6 players, 4 of them equity based, 2 of them random"""
        from agents.agent_consider_equity import Player as EquityPlayer
        from agents.agent_random import Player as RandomPlayer
        env_name = 'neuron_poker-v0'
        self.env = gym.make(
            env_name, initial_stacks=self.stack, render=self.render)
        self.env.add_player(EquityPlayer(
            name='equity/50/50', min_call_equity=.5, min_bet_equity=-.5))
        self.env.add_player(EquityPlayer(
            name='equity/50/80', min_call_equity=.8, min_bet_equity=-.8))
        self.env.add_player(EquityPlayer(
            name='equity/70/70', min_call_equity=.7, min_bet_equity=-.7))
        self.env.add_player(EquityPlayer(
            name='equity/20/30', min_call_equity=.2, min_bet_equity=-.3))
        self.env.add_player(RandomPlayer())
        self.env.add_player(RandomPlayer())

        for _ in range(self.num_episodes):
            self.env.reset()
            self.winner_in_episodes.append(self.env.winner_ix)

        league_table = pd.Series(self.winner_in_episodes).value_counts()
        best_player = league_table.index[0]

        print("League Table")
        print("============")
        print(league_table)
        print(f"Best Player: {best_player}")

    def equity_self_improvement(self, improvement_rounds):
        """Create 6 players, 4 of them equity based, 2 of them random"""
        from agents.agent_consider_equity import Player as EquityPlayer
        calling = [.1, .2, .3, .4, .5, .6]
        betting = [.2, .3, .4, .5, .6, .7]

        for improvement_round in range(improvement_rounds):
            env_name = 'neuron_poker-v0'
            self.env = gym.make(
                env_name, initial_stacks=self.stack, render=self.render)
            for i in range(6):
                self.env.add_player(EquityPlayer(name=f'Equity/{calling[i]}/{betting[i]}',
                                                 min_call_equity=calling[i],
                                                 min_bet_equity=betting[i]))

            for _ in range(self.num_episodes):
                self.env.reset()
                self.winner_in_episodes.append(self.env.winner_ix)

            league_table = pd.Series(self.winner_in_episodes).value_counts()
            best_player = int(league_table.index[0])
            print(league_table)
            print(f"Best Player: {best_player}")

            # self improve:
            self.log.info(f"Self improvment round {improvement_round}")
            for i in range(6):
                calling[i] = np.mean([calling[i], calling[best_player]])
                self.log.info(f"New calling for player {i} is {calling[i]}")
                betting[i] = np.mean([betting[i], betting[best_player]])
                self.log.info(f"New betting for player {i} is {betting[i]}")

    def dqn_agent(self, mode):
        my_import = __import__('agents.'+self.agent, fromlist=['Player'])
        player = getattr(my_import, 'Player')

        env_path = 'env'
        if self.env_name != 'v0':
            env_path += '_' + self.env_name

        shell_import = __import__(
            'gym_env.' + env_path, fromlist=['PlayerShell'])
        PlayerShell_import = getattr(shell_import, 'PlayerShell')

        env_name = 'neuron_poker-' + self.env_name
        self.env = gym.make(env_name, initial_stacks=self.stack, funds_plot=self.funds_plot, render=self.render,
                            use_cpp_montecarlo=self.use_cpp_montecarlo)
        np.random.seed(42)
        self.env.seed(42)

        count = 1

        for player_type in self.players:
            if player_type == 0:
                self.env.add_player(RandomPlayer(env_path))
            elif type(player_type) == tuple and len(player_type) == 2:
                self.env.add_player(EquityPlayer(name='equity_' + str(count), env=env_path,
                                                 min_call_equity=player_type[0], min_bet_equity=player_type[1]))
                count += 1

        self.env.add_player(PlayerShell_import(
            name='keras-rl', stack_size=self.stack))

        self.env.reset()

        if mode == 'train':
            dqn = player()
            dqn.initiate_agent(self.env)
            dqn.train(env_name=self.model_name)
        elif mode == 'play':
            dqn = player(load_model=self.model_name, env=self.env)
            dqn.play(nb_episodes=self.num_episodes, render=self.render)


if __name__ == '__main__':
    command_line_parser()
