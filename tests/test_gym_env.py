"""Tests for the gym environment"""

from gym_env.env import HoldemTable, Action, Stage, PlayerCycle
from gym_env.random_agent import Player


def _create_env(n_players):
    """Create an environment"""
    env = HoldemTable(n_players)
    for _ in range(n_players):
        player = Player(100)
        env.add_player(player)
    env.reset()
    return env


def test_init_env():
    """Test basic actions with 6 players."""
    env = _create_env(6)
    assert len(env.players[0].cards) == 2
    assert env.current_player.seat == 3  # start with utg

    env.step(Action.CALL)
    env.step(Action.FOLD)
    env.step(Action.FOLD)
    env.step(Action.FOLD)
    env.step(Action.CALL)
    env.step(Action.CALL)
    assert env.players[3].stack == 98
    assert env.players[4].stack == 100
    assert env.players[5].stack == 100
    assert env.players[0].stack == 100
    assert env.players[1].stack == 98
    assert env.players[2].stack == 98
    assert env.stage == Stage.FLOP

    env.step(Action.RAISE_POT)
    env.step(Action.FOLD)
    env.step(Action.CALL)
    env.step(Action.FOLD)
    env.step(Action.CALL)
    env.step(Action.CALL)


def test_random_action():
    """Test random actions until the end with 2 players."""
    env = _create_env(2)
    while True:
        _, _, done, _ = env.step()
        if done:
            break


def test_cycle_forever():
    """Test cycle"""
    lst = ['dealer', 'sb', 'bb', 'utg', 'utg1', 'utg2']
    cycle = PlayerCycle(lst)
    current = cycle.next_player()
    assert current == 'sb'
    current = cycle.next_player(step=2)
    assert current == 'utg'
    cycle.deactivate_current()
    current = cycle.next_player(step=6)
    assert current == 'utg1'
    current = cycle.next_player(step=1)
    assert current == 'utg2'
    current = cycle.next_player()
    assert current == 'dealer'
    cycle.deactivate_player(0)
    cycle.deactivate_player(1)
    cycle.deactivate_player(2)
    current = cycle.next_player(step=2)
    assert current == 'utg1'


def test_cycle_max_rounds():
    """Test cycle"""
    lst = ['dealer', 'sb', 'bb', 'utg']
    cycle = PlayerCycle(lst, start_idx=2, max_steps_total=5)
    current = cycle.next_player()
    assert current == 'utg'
    cycle.next_player()
    cycle.next_player()
    current = cycle.next_player(step=2)
    assert current == 'utg'
    current = cycle.next_player()
    assert cycle.counter == 6
    assert not current
