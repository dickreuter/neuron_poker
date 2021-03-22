import tensorflow as tf
import json

import gym
from gym_env.env import Action

import spinup.utils.logx
from spinup import sac_tf1

import time


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

    def train(self, env_fn):
        # need to pass in function that can make copy of the env...
        sac_tf1(env_fn, actor_critic='pi', ac_kwargs={},
                seed=0, steps_per_epoch=4000, epochs=100, replay_size=1000000,
                gamma=0.99, polyak=0.995, lr=0.001, alpha=0.2, batch_size=100,
                start_steps=10000, update_after=1000, update_every=50,
                num_test_episodes=5, max_ep_len=1000, logger_kwargs={},
                save_freq=1)

    def load(self, env_name):
        pass

    def play(self, nb_episodes=5, render=False):
        pass
