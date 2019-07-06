"""
neuron poker

Usage:
  main.py random [options]
  main.py keypress [options]
  main.py consider_equity [options]
  main.py equity_improvement --improvement_rounds=<> [options]
  main.py deep_q_learning [options]

options:
  -h --help         Show this screen.
  -r --render       render screen
  --log             log file
  --screenloglevel  log level on screen
  --episodes=<>     number of episodes to play

"""

import logging

import gym
import numpy as np
import pandas as pd
from docopt import docopt

from agents.agent_consider_equity import Player as EquityPlayer
from agents.agent_keypress import Player as KeyPressAgent
from agents.agent_random import Player as RandomPlayer
from gym_env.env import PlayerShell
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

    num_episodes = 1 if not args['--episodes'] else int(args['--episodes'])
    runner = Runner(render=args['--render'], num_episodes=num_episodes)

    if args['random']:
        runner.random_agents()

    elif args['keypress']:
        runner.key_press_agents()

    elif args['consider_equity']:
        runner.equity_vs_random()

    elif args['equity_improvement']:
        improvement_rounds = int(args['--improvement_rounds'])
        runner.equity_self_improvement(improvement_rounds)

    elif args['deep_q_learning']:
        runner.deep_q_learning()

    else:
        raise RuntimeError("Argument not yet implemented")


class Runner:
    """Orchestration"""

    def __init__(self, render, num_episodes):
        """Initialize"""
        self.winner_in_episodes = []
        self.render = render
        self.env = None
        self.num_episodes = num_episodes
        self.log = logging.getLogger(__name__)

    def random_agents(self):
        """Create an environment with 6 random players"""
        env_name = 'neuron_poker-v0'
        stack = 500
        num_of_plrs = 6
        self.env = gym.make(env_name, num_of_players=num_of_plrs, initial_stacks=stack, render=self.render)
        for _ in range(num_of_plrs):
            player = RandomPlayer()
            self.env.add_player(player)

        self.env.reset()

    def key_press_agents(self):
        """Create an environment with 6 key press agents"""
        env_name = 'neuron_poker-v0'
        stack = 500
        num_of_plrs = 6
        self.env = gym.make(env_name, num_of_players=num_of_plrs, initial_stacks=stack, render=self.render)
        for _ in range(num_of_plrs):
            player = KeyPressAgent()
            self.env.add_player(player)

        self.env.reset()

    def equity_vs_random(self):
        """Create 6 players, 4 of them equity based, 2 of them random"""
        env_name = 'neuron_poker-v0'
        stack = 500
        num_of_plrs = 6
        self.env = gym.make(env_name, num_of_players=num_of_plrs, initial_stacks=stack, render=self.render)
        self.env.add_player(EquityPlayer(name='equity/50/50', min_call_equity=.5, min_bet_equity=-.5))
        self.env.add_player(EquityPlayer(name='equity/50/80', min_call_equity=.8, min_bet_equity=-.8))
        self.env.add_player(EquityPlayer(name='equity/70/70', min_call_equity=.7, min_bet_equity=-.7))
        self.env.add_player(EquityPlayer(name='equity/20/30', min_call_equity=.2, min_bet_equity=-.3))
        self.env.add_player(RandomPlayer())
        self.env.add_player(RandomPlayer())

        for _ in range(self.num_episodes):
            self.env.reset()
            self.winner_in_episodes.append(self.env.winner_ix)

        league_table = pd.Series(self.winner_in_episodes).value_counts()
        best_player = league_table.index[0]

        print(league_table)
        print(f"Best Player: {best_player}")

    def equity_self_improvement(self, improvement_rounds):
        """Create 6 players, 4 of them equity based, 2 of them random"""
        calling = [.1, .2, .3, .4, .5, .6]
        betting = [.2, .3, .4, .5, .6, .7]

        for improvement_round in range(improvement_rounds):
            env_name = 'neuron_poker-v0'
            stack = 500
            self.env = gym.make(env_name, num_of_players=5, initial_stacks=stack, render=self.render)
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

    @staticmethod
    def deep_q_learning():
        """Implementation of kreras-rl deep q learing."""
        env_name = 'neuron_poker-v0'
        stack = 100
        env = gym.make(env_name, num_of_players=5, initial_stacks=stack)

        np.random.seed(123)
        env.seed(123)

        env.add_player(EquityPlayer(name='equity/50/50', min_call_equity=.5, min_bet_equity=-.5))
        env.add_player(EquityPlayer(name='equity/50/80', min_call_equity=.8, min_bet_equity=-.8))
        env.add_player(EquityPlayer(name='equity/70/70', min_call_equity=.7, min_bet_equity=-.7))
        env.add_player(EquityPlayer(name='equity/20/30', min_call_equity=.2, min_bet_equity=-.3))
        env.add_player(RandomPlayer())
        env.add_player(PlayerShell(name='keras-rl', stack_size=stack))  # shell is used for callback to keras rl

        env.reset()

        nb_actions = env.action_space.n

        # Next, we build a very simple model.
        from keras import Sequential
        from keras.optimizers import Adam
        from keras.layers import Dense, Dropout
        from rl.memory import SequentialMemory
        from rl.agents import DQNAgent
        from rl.policy import BoltzmannQPolicy

        model = Sequential()
        model.add(Dense(512, activation='relu', input_shape=env.observation_space))
        model.add(Dropout(0.2))
        model.add(Dense(512, activation='relu'))
        model.add(Dropout(0.2))
        model.add(Dense(512, activation='relu'))
        model.add(Dropout(0.2))
        model.add(Dense(nb_actions, activation='linear'))

        # Finally, we configure and compile our agent. You can use every built-in Keras optimizer and
        # even the metrics!
        memory = SequentialMemory(limit=200, window_length=1)
        policy = BoltzmannQPolicy()
        from rl.core import Processor

        class CustomProcessor(Processor):
            """he agent and the environment"""

            def process_state_batch(self, batch):
                """
                Given a state batch, I want to remove the second dimension, because it's
                useless and prevents me from feeding the tensor into my CNN
                """
                return np.squeeze(batch, axis=1)

            def process_info(self, info):
                processed_info = info['player_data']
                if 'stack' in processed_info:
                    del processed_info['stack']
                return processed_info

        dqn = DQNAgent(model=model, nb_actions=nb_actions, memory=memory, nb_steps_warmup=100,
                       target_model_update=1e-2, policy=policy,
                       processor=CustomProcessor(),
                       batch_size=10)
        dqn.compile(Adam(lr=1e-3), metrics=['mae'])

        # initiate training loop
        dqn.fit(env, nb_max_start_steps=50, nb_steps=1000, visualize=False, verbose=2)

        # After training is done, we save the final weights.
        dqn.save_weights('dqn_{}_weights.h5f'.format(env_name), overwrite=True)

        # Finally, evaluate our algorithm for 5 episodes.
        dqn.test(env, nb_episodes=5, visualize=False)


if __name__ == '__main__':
    command_line_parser()
