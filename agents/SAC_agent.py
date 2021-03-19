import tensorflow as tf
import json

from gym_env.end import Action

import spinup.utils.logx
from spinup import sac_tf1


class Player:

    def __init__(self, name='SAC', load_model=None, env=None):
        self.equity_alive = 0
        self.actions = []
        self.last_action_in_stage = ''
        self.temp_stack = []
        self.name = name
        self.autoplay = True

        self.sac = None
        self.env = env

        if load_model:
            self.load(load_model)

    def initiate_agent(self, env):
        # not sure if this line is needed
        tf.compat.v1.disable_eager_execution()

        self.env = env

        nb_actions = self.env.action_space.n

    def train(self, env_name):
        pass

    def load(self, env_name):
        pass

    def play(self, nb_episodes=5, render=False):
        pass
