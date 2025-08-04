"""Registration to gymnasium"""
from gymnasium.envs.registration import register

register(id="neuron_poker-v0", entry_point="gym_env.env:HoldemTable")
