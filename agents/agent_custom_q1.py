"""manual keypress agent"""
# pylint: disable=import-error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from rl.memory import SequentialMemory

from agents.agent_keras_rl_dqn import TrumpPolicy, memory_limit, window_length
from gym_env import env

class Player:
    """Mandatory class with the player methods"""

    def __init__(self, name='Custom_Q1'):
        """Initiaization of an agent"""
        self.equity_alive = 0
        self.actions = []
        self.last_action_in_stage = ''
        self.temp_stack = []
        self.name = name
        self.autoplay = True
        self.model = None

    def initiate_agent(self, nb_actions):
        """initiate a deep Q agent"""

        self.model = Sequential()
        self.model.add(Dense(512, activation='relu', input_shape=env.observation_space))  # pylint: disable=no-member
        self.model.add(Dropout(0.2))
        self.model.add(Dense(512, activation='relu'))
        self.model.add(Dropout(0.2))
        self.model.add(Dense(512, activation='relu'))
        self.model.add(Dropout(0.2))
        self.model.add(Dense(nb_actions, activation='linear'))

        # Finally, we configure and compile our agent. You can use every built-in Keras optimizer and
        # even the metrics!
        memory = SequentialMemory(limit=memory_limit, window_length=window_length)  # pylint: disable=unused-variable
        policy = TrumpPolicy()  # pylint: disable=unused-variable

    def action(self, action_space, observation, info):  # pylint: disable=no-self-use,unused-argument
        """Mandatory method that calculates the move based on the observation array and the action space."""
        _ = (observation, info)  # not using the observation for random decision
        action = None

        # decide if explore or explot

        # forward

        # save to memory

        # backward
        # decide what to use for training
        # update model
        # save weights

        return action
