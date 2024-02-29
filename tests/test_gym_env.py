"""Tests for the gym environment"""
import pytest

from gym_env.cycle import PlayerCycle
from gym_env.enums import Action, Stage
from gym_env.env import HoldemTable


def _create_env(n_players,
                initial_stacks=100, small_blind=1, big_blind=2, render=False, funds_plot=False,
                max_raises_per_player_round=2,
                use_cpp_montecarlo=False):
    """Create an environment"""
    env = HoldemTable(small_blind=small_blind, big_blind=big_blind, initial_stacks=initial_stacks,
                      max_raises_per_player_round=max_raises_per_player_round,
                      use_cpp_montecarlo=use_cpp_montecarlo, funds_plot=funds_plot, render=render)

    for _ in range(n_players):
        player = PlayerForTest()
        env.add_player(player)
    env.reset()
    return env


def test_basic_actions_with_6_player():
    """Test basic actions with 6 players."""
    env = _create_env(6)
    assert len(env.players[0].cards) == 2
    assert env.current_player.seat == 3  # start with utg

    env.step(Action.CALL)  # 3
    env.step(Action.FOLD)  # 4
    env.step(Action.FOLD)  # 5
    env.step(Action.FOLD)  # 0 dealer
    env.step(Action.CALL)  # 1 small blind
    assert env.current_player.seat == 2  # 2 big blind
    assert env.players[3].stack == 98
    assert env.players[4].stack == 100
    assert env.players[5].stack == 100
    assert env.players[0].stack == 100
    assert env.players[1].stack == 98
    assert env.players[2].stack == 98
    assert env.stage == Stage.PREFLOP
    env.step(Action.RAISE_POT)  # big blind raises
    assert env.player_cycle.round_number_in_street
    env.step(Action.FOLD)  # utg
    env.step(Action.CALL)  # 4 only remaining player calls
    assert env.stage == Stage.FLOP
    env.step(Action.CHECK)


def test_no_player_raise_big_blind_do_last_action_in_round():
    """1. Test verifies solving of bugs see posts of dsfdsfgdsa in
    https://github.com/dickreuter/neuron_poker/issues/25.
    Bug description: In a round where no one raise, should the big blind do the last action.
    Without fix from  dsfdsfgdsa on 10.06.2020 the small blind do the last action.
    2. Bug description: Check of big blind does not end round (pre-flop).
    The problem for this bug is that the check of big blind is not recognized as legal move.
    This bug is solved with fix from dsfdsfgdsa on 10.06.2020"""
    env = _create_env(2)

    env.step(Action.SMALL_BLIND)
    env.step(Action.BIG_BLIND)
    env.step(Action.CALL)

    assert env.stage == Stage.PREFLOP

    env.step(Action.CHECK)

    assert env.stage == Stage.FLOP


def test_one_player_raise3bb_one_call_this_call_is_last_action_in_round():
    """1. Test verifies solving of bugs see posts of dsfdsfgdsa from 11.06.2020 in
    https://github.com/dickreuter/neuron_poker/issues/25.
    Bug description: One player Raise_3BB and other call normally now is the round over, but with bug the first player can check again."""
    env = _create_env(2)

    env.step(Action.SMALL_BLIND)
    env.step(Action.BIG_BLIND)
    env.step(Action.RAISE_3BB)

    assert env.stage == Stage.PREFLOP

    env.step(Action.CALL)

    assert env.stage == Stage.FLOP


def test_raise_to_3_times_big_blind_after_big_blind_bet():
    """1. Test size of raise to 3 times big blind after betting of big blind.
    See https://github.com/dickreuter/neuron_poker/issues/41"""
    env = _create_env(2)  # bet small blind and big blind

    assert env.player_pots[0] == 2  # check bet of big blind by creation of environment

    env.step(Action.CALL)
    env.step(Action.RAISE_3BB)

    assert env.player_pots[0] == 6  # raised to 3 times big blind like on Pokerstars


def test_raise_to_3_times_big_blind_is_not_possible_with_not_enough_remaining_stack():
    """1. Test raise to 3 times big blind is only possible with enough chips.
    See https://github.com/dickreuter/neuron_poker/issues/41"""
    env = _create_env(4, initial_stacks=2)  # bet small blind and big blind

    env.step(Action.CALL)
    assert Action.RAISE_3BB not in env.legal_moves


def test_raise_to_3_times_big_blind_is_possible_with_enough_remaining_stack():
    """1. Test raise to 3 times big blind is only possible with enough chips.
    See https://github.com/dickreuter/neuron_poker/issues/41"""
    env = _create_env(2)  # bet small blind and big blind
    env.players[0].stack = 4

    env.step(Action.CALL)

    assert Action.RAISE_3BB in env.legal_moves

    env.step(Action.RAISE_3BB)

    assert env.players[0].stack == 0


@pytest.mark.skip("Test-scenario is not like title of the test and player_cycle.alive has by several executions a "
                  "changed behaviour")
def test_heads_up_after_flop():
    """All in at pre-flop leads to heads up after flop.
    For more info about skipping of this test see https://github.com/dickreuter/neuron_poker/issues/39.
    Feel free to fix the issue"""
    env = _create_env(6)
    env.step(Action.ALL_IN)  # seat 3 utg
    env.step(Action.ALL_IN)  # seat 4
    env.step(Action.ALL_IN)  # seat 5
    env.step(Action.ALL_IN)  # seat 0
    env.step(Action.CALL)  # seat 1 small blind = all in
    assert Action.ALL_IN in env.legal_moves  # seat 2 big blind has the option to raise
    env.step(Action.FOLD)  # seat 2 big blind folds
    assert sum(env.player_cycle.alive) == 2
    # two players left - heads up
    assert env.stage == Stage.PREFLOP  # start new hand
    assert sum(env.player_cycle.alive) == 2
    env.step(Action.CALL)  # sb calls at preflop, first mover
    assert env.stage == Stage.PREFLOP
    env.step(Action.RAISE_POT)  # bb raises pot
    assert env.stage == Stage.PREFLOP
    assert len(env.legal_moves) == 2
    env.step(Action.CALL)  # sb can now call and then turn
    assert env.stage == Stage.FLOP
    env.step(Action.CHECK)
    env.step(Action.CHECK)
    assert env.stage == Stage.TURN
    env.step(Action.RAISE_POT)
    assert env.stage == Stage.TURN
    env.step(Action.FOLD)
    assert env.stage == Stage.PREFLOP


def test_base_actions_6_players_check_legal_moves_and_stages():
    """Test basic actions with 6 players."""
    env = _create_env(6)
    env.step(Action.CALL)  # seat 3 utg
    env.step(Action.CALL)  # seat 4
    env.step(Action.CALL)  # seat 5
    env.step(Action.CALL)  # seat 0 dealer
    assert env.stage == Stage.PREFLOP
    env.step(Action.RAISE_HALF_POT)  # seat 1 small blind
    # todo: check if this is correct
    assert len(env.legal_moves) > 2
    assert env.stage == Stage.PREFLOP
    env.step(Action.RAISE_HALF_POT)  # seat 2 big blind
    assert env.stage == Stage.PREFLOP
    assert len(env.legal_moves) > 2
    env.step(Action.CALL)  # seat 3 utg in second round
    env.step(Action.CALL)  # seat 4
    env.step(Action.CALL)  # seat 5
    env.step(Action.CALL)  # seat 0 dealer
    assert env.stage == Stage.FLOP
    assert env.current_player.seat == 1
    env.step(Action.CALL)  # seat 1 small blind
    assert env.stage == Stage.FLOP
    assert env.current_player.seat == 1
    env.step(Action.RAISE_HALF_POT)  # seat 2 big blind
    env.step(Action.FOLD)


def test_cycle_mechanism1():
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


class PlayerForTest:
    """Player shell"""

    def __init__(self, stack_size=100, name='TestPlayer'):
        """Initiaization of an agent"""
        self.stack = stack_size
        self.seat = None
        self.equity_alive = 0
        self.actions = []
        self.last_action_in_stage = ''
        self.temp_stack = []
        self.name = name
        self.agent_obj = None

    @staticmethod
    def action(action, observation, info):
        """Perform action."""
        _ = (observation, info)
        return action


@pytest.mark.skip("Values need to be updated and be presented as proportion of bb*100")
def test_call_proper_amount():
    """Test if a player contributes the correct amount if they call behind a caller who could not cover and went all
    in """
    env = _create_env(3)
    raise_size = 2 * (env.small_blind + env.big_blind)

    # Blinds should have been posted
    assert env.community_data.current_round_pot == env.big_blind + env.small_blind

    # Button will raise pot size (2*(sb+bb)), sb will call all in with 1 for a total contribution of sb+1,
    # bb should have to bet 2*sb+bb in order to call
    env.players[0].stack = raise_size
    env.players[1].stack = 1
    env.players[2].stack = raise_size - env.big_blind

    env.step(Action.ALL_IN)  # button raise
    assert env.min_call == raise_size
    env.step(Action.CALL)  # sb calls but does not cover
    assert env.min_call == raise_size
    env.step(Action.CALL)  # bb calls full amount
    assert env.stage_data[0].contribution[0] == 0.03
    assert env.stage_data[0].contribution[1] == 0.01
    assert env.stage_data[0].contribution[2] == 0.03


def test_unlimited_raising_preflop():
    """Test raising unlimited preflop"""
    env = _create_env(2, initial_stacks=100000, max_raises_per_player_round=3)
    env.step(Action.CALL)  # sb
    env.step(Action.RAISE_POT)  # bb raises
    env.step(Action.RAISE_POT)  # sb
    assert env.stage == Stage.PREFLOP
    env.step(Action.RAISE_POT)  # bb raises
    assert env.stage == Stage.PREFLOP
    env.step(Action.RAISE_POT)  # sb calls
    assert env.stage == Stage.PREFLOP
    env.step(Action.CALL)  # sb calls
    assert env.stage == Stage.FLOP


def test_end_preflop_on_call():
    """Test that the preflop round ends when there is
       a call after a raise
    """
    env = _create_env(2, initial_stacks=100000, max_raises_per_player_round=3)
    env.step(Action.CALL)  # sb
    env.step(Action.RAISE_POT)  # bb raises
    assert env.stage == Stage.PREFLOP
    env.step(Action.CALL)  # sb
    assert env.stage == Stage.FLOP


def test_preflop_call_after_max_raises():
    """Test that the preflop round ends when there is
       a call after a raise
    """
    env = _create_env(2, initial_stacks=100000, max_raises_per_player_round=2)
    # sb
    # bb
    env.step(Action.CALL)  # sb
    env.step(Action.RAISE_POT)  # bb raises
    env.step(Action.RAISE_POT)  # sb raises
    assert env.stage == Stage.PREFLOP
    env.step(Action.RAISE_POT)  # bb raises
    assert env.stage == Stage.PREFLOP
    env.step(Action.RAISE_POT)  # sb raises
    assert env.stage == Stage.PREFLOP
    # Now we should still be in preflop, but raises are no longer legal actions
    # Only a Call or Fold would end the round
    assert env.legal_moves == [Action.CALL, Action.FOLD]

    env.step(Action.CALL)
    assert env.stage == Stage.FLOP
    env.step(Action.RAISE_POT)
    env.step(Action.CALL)
    assert env.stage == Stage.TURN
    env.step(Action.RAISE_POT)
    env.step(Action.CALL)
    assert env.stage == Stage.RIVER
    env.step(Action.RAISE_POT)
    env.step(Action.CALL)


@pytest.mark.skip(reason="raise 3bb is currently not handled correctly")
def test_preflop_call_after_max_3bb_raises():
    """Test that the preflop round ends when there is
       a call after a raise
    """
    env = _create_env(2, initial_stacks=100000, max_raises_per_player_round=2)
    # sb
    # bb
    env.step(Action.CALL)  # sb
    env.step(Action.RAISE_3BB)  # bb raises
    env.step(Action.RAISE_3BB)  # sb raises
    assert env.stage == Stage.PREFLOP
    env.step(Action.RAISE_3BB)  # bb raises
    assert env.stage == Stage.PREFLOP
    env.step(Action.RAISE_3BB)  # sb raises
    assert env.stage == Stage.PREFLOP
    # Now we should still be in preflop, but raises are no longer legal actions
    # Only a Call or Fold would end the round
    assert env.legal_moves == [Action.CALL, Action.FOLD]

    env.step(Action.CALL)
    assert env.stage == Stage.FLOP


def test_one_max_raise_per_player():
    """Test the possibility to make one max raise per player
    """
    env = _create_env(2, initial_stacks=100000, max_raises_per_player_round=1)
    assert env.stage == Stage.PREFLOP


def test_headsup_bb_starts_flop_bb_ends_preflop():
    """Test that the big blind player should  play first in Flop even if
    they ends preflop.
    """
    env = _create_env(2, initial_stacks=100000, max_raises_per_player_round=2)
    # sb (player seat is 1)
    # bb (player seat is 0)
    assert env.stage == Stage.PREFLOP and env.current_player.seat == 1
    env.step(Action.CALL)  # sb
    assert env.stage == Stage.PREFLOP and env.current_player.seat == 0
    env.step(Action.CHECK)  # bb raises
    assert env.stage == Stage.FLOP
    assert env.current_player.seat == 0  # The bb should play first in FLOP


def test_headsup_bb_starts_flop_sb_ends_preflop():
    """Test that the big blind player should  play first in Flop after small
    blind ends preflop.
    """
    env = _create_env(2, initial_stacks=100000, max_raises_per_player_round=2)
    # sb (player seat is 1)
    # bb (player seat is 0)
    assert env.stage == Stage.PREFLOP and env.current_player.seat == 1
    env.step(Action.CALL)  # sb
    assert env.stage == Stage.PREFLOP and env.current_player.seat == 0
    env.step(Action.RAISE_3BB)  # bb raises
    assert env.stage == Stage.PREFLOP and env.current_player.seat == 1
    env.step(Action.CALL)  # sb calls
    assert env.stage == Stage.FLOP
    assert env.current_player.seat == 0  # The bb should play first in FLOP
