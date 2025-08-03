"""Entry point scripts for neuron poker commands."""

import sys
from main import command_line_parser


def main_random():
    """Run random agents"""
    sys.argv = ["main.py", "selfplay", "random"]
    command_line_parser()


def main_keypress():
    """Run keypress agent"""
    sys.argv = ["main.py", "selfplay", "keypress"]
    command_line_parser()


def main_equity():
    """Run equity-based agent"""
    sys.argv = ["main.py", "selfplay", "consider_equity"]
    command_line_parser()


def main_equity_improvement():
    """Run equity improvement with genetic algorithm"""
    sys.argv = [
        "main.py",
        "selfplay",
        "equity_improvement",
        "--improvement_rounds=20",
        "--episodes=10",
    ]
    command_line_parser()


def main_dqn_train():
    """Train DQN agent"""
    sys.argv = ["main.py", "selfplay", "dqn_train"]
    command_line_parser()


def main_dqn_play():
    """Play with trained DQN agent"""
    sys.argv = ["main.py", "selfplay", "dqn_play"]
    command_line_parser()


def main_random_render():
    """Run random agents with rendering"""
    sys.argv = ["main.py", "selfplay", "random", "--render"]
    command_line_parser()


def main_keypress_render():
    """Run keypress agent with rendering"""
    sys.argv = ["main.py", "selfplay", "keypress", "--render"]
    command_line_parser()


def main_equity_render():
    """Run equity-based agent with rendering"""
    sys.argv = ["main.py", "selfplay", "consider_equity", "--render"]
    command_line_parser()


def main_dqn_train_cpp():
    """Train DQN agent with C++ Monte Carlo"""
    sys.argv = ["main.py", "selfplay", "dqn_train", "--use_cpp_montecarlo"]
    command_line_parser()
