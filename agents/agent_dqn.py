"""Player based on a trained neural network"""

import numpy as np
from rl.policy import BoltzmannQPolicy

from gym_env.env import Action

autplay = True  # play automatically if played against keras-rl

window_length = 1
memory_limit = 200
nb_steps_warmup = 100
nb_max_start_steps = 100
nb_steps = 10000
batch_size = 100


class Player:
    """Mandatory class with the player methods"""

    def __init__(self, name='DQN'):
        """Initiaization of an agent"""
        self.equity_alive = 0
        self.actions = []
        self.last_action_in_stage = ''
        self.temp_stack = []
        self.name = name
        self.autoplay = True

        self.dqn = None
        self.env = None

    def initiate_agent(self, env):
        """initiate a deep Q agent"""
        from keras import Sequential
        from keras.optimizers import Adam
        from keras.layers import Dense, Dropout
        from rl.memory import SequentialMemory
        from rl.agents import DQNAgent
        from rl.policy import BoltzmannQPolicy

        self.env = env

        nb_actions = self.env.action_space.n

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
        memory = SequentialMemory(limit=memory_limit, window_length=window_length)
        policy = TrumpPolicy()
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
                    processed_info = {'x': 1}
                return processed_info

        nb_actions = env.action_space.n

        self.dqn = DQNAgent(model=model, nb_actions=nb_actions, memory=memory, nb_steps_warmup=nb_steps_warmup,
                            target_model_update=1e-2, policy=policy,
                            processor=CustomProcessor(),
                            batch_size=batch_size)
        self.dqn.compile(Adam(lr=1e-3), metrics=['mae'])

    def start_step_policy(self, observation):
        print("Random step")
        action = self.env.action_space.sample()
        return action

    def train(self, env_name):
        """Train a model"""
        # initiate training loop

        self.dqn.fit(self.env, nb_max_start_steps=nb_max_start_steps, nb_steps=nb_steps, visualize=False, verbose=2,
                     start_step_policy=self.start_step_policy)

        # After training is done, we save the final weights.
        self.dqn.save_weights('dqn_{}_weights.h5f'.format(env_name), overwrite=True)

        # Finally, evaluate our algorithm for 5 episodes.
        self.dqn.test(self.env, nb_episodes=5, visualize=False)

    def load(self, env_name):
        """Load a model"""
        self.dqn.load_weights('dqn_{}_weights.h5f'.format(env_name))

    def action(self, action_space, observation, info):  # pylint: disable=no-self-use
        """Mandatory method that calculates the move based on the observation array and the action space."""
        _ = observation  # not using the observation for random decision
        _ = info

        this_player_action_space = {Action.FOLD, Action.CHECK, Action.CALL, Action.RAISE_POT, Action.RAISE_HALF_POT,
                                    Action.RAISE_2POT}
        _ = this_player_action_space.intersection(set(action_space))

        action = None
        return action


class TrumpPolicy(BoltzmannQPolicy):
    def select_action(self, q_values):
        """Return the selected action

        # Arguments
            q_values (np.ndarray): List of the estimations of Q for each action

        # Returns
            Selection action
        """
        assert q_values.ndim == 1
        q_values = q_values.astype('float64')
        nb_actions = q_values.shape[0]

        exp_values = np.exp(np.clip(q_values / self.tau, self.clip[0], self.clip[1]))
        probs = exp_values / np.sum(exp_values)
        action = np.random.choice(range(nb_actions), p=probs)
        print ("Chosen action")
        return action
