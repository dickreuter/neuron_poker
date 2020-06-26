"""Tests for the gym environment"""
import pytest

from gym_env.env import HoldemTable, Action, Stage, PlayerCycle


def _create_env(n_players):
    """Create an environment"""
    env = HoldemTable()
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
    assert env.player_cycle.second_round
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
    env = _create_env(2)  # bet small blind and big blind
    env.players[0].stack = 2

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
    assert len(env.legal_moves) > 2
    assert env.stage == Stage.PREFLOP
    env.step(Action.RAISE_HALF_POT)  # seat 2 big blind
    assert env.stage == Stage.PREFLOP
    assert len(env.legal_moves) == 2
    env.step(Action.CALL)  # seat 3 utg in second round
    env.step(Action.CALL)  # seat 4
    env.step(Action.CALL)  # seat 5
    env.step(Action.CALL)  # seat 0 dealer
    # todo: check if this is correct
    # assert env.stage == Stage.FLOP
    # env.step(Action.CALL)  # seat 1 small blind
    # assert env.stage == Stage.FLOP
    # assert env.current_player.seat == 1
    # env.step(Action.RAISE_HALF_POT) # seat 2 big blind


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


def test_cycle_mechanism2():
    """Test cycle"""
    lst = ['dealer', 'sb', 'bb', 'utg']
    cycle = PlayerCycle(lst, start_idx=2, max_steps_total=5)
    current = cycle.next_player()
    assert current == 'utg'
    cycle.next_player()
    cycle.next_player()
    current = cycle.next_player(step=2)
    assert not current


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


def test_call_all_in_with_not_enough_stack_is_not_allowed():
    """Bug description: Player with a stack of 100 goes allin. The player after that calls this,
    but he has only a stack of 1. In a case like this the remaining stack was negative. Call is not allowed in a
    situation like that, because player has not enough chips he can only go all in. This test check if the bug is solved
     or not."""
    env = _create_env(2)  # bet small blind and big blind
    env.players[0].stack = 1  # seat 0 big blind has a remaining stack of 1
    env.step(Action.ALL_IN)  # seat 0  small blind goes all in

    assert Action.CALL not in env.legal_moves


def test_one_side_pot_three_possible_winners():
    """Test checks all possibilities of one side pot.
    Loop is required to get all possibilities, because cards on table and winner is every time different"""
    winner_index_checked = np.array([False, False, False])
    while winner_index_checked.sum() != 3:
        env = _create_env(3)  # bet small blind and big blind
        env.players[0].stack = 50  # seat 0

        env.step(Action.ALL_IN)  # seat 0 goes all in
        env.step(Action.ALL_IN)  # seat 1 small blind calls
        env.step(Action.CALL)  # seat 2 big blind calls

        if env.winner_index[0] == 0:
            assert env.stage == Stage.PREFLOP  # new hand started, because 2 player left the reason for this
            # behaviour is the side-pot
            assert env.players[0].stack == 149  # main pot (150) - new small blind (1) = 149
            assert env.players[env.winner_index[1]].stack == 98  # side pot (100) - new big blind (2) = 98
            winner_index_checked[env.winner_index] = True
        elif env.winner_index[0] == 1:
            assert env.stage == Stage.SHOWDOWN
            assert env.players[1].stack == 250
            assert env.players[0].stack == 0
            assert env.players[2].stack == 0
            winner_index_checked[env.winner_index] = True
        elif env.winner_index[0] == 2:
            assert env.stage == Stage.SHOWDOWN
            assert env.players[2].stack == 250
            assert env.players[1].stack == 0
            assert env.players[0].stack == 0
            winner_index_checked[env.winner_index] = True
        else:
            assert False


def test_two_side_pots_check_4_cases():
    """Test checks all cases of two side pots.
    Loop is required to get all possibilities, because cards on table and winner is every time different"""
    winner_index_checked = np.array([False, False, False, False])
    while winner_index_checked.sum() != 4:
        env = _create_env(4)  # bet small blind and big blind
        env.players[0].stack = 50  # seat 0
        env.players[3].stack = 25  # seat 3
        env.step(Action.ALL_IN)  # seat 3 goes all in
        env.step(Action.ALL_IN)  # seat 0 ALL_IN
        env.step(Action.ALL_IN)  # seat 1 small blind ALL_IN
        env.step(Action.CALL)  # seat 2 big blind ALL_IN

        if env.winner_index[0] == 0:
            assert env.stage == Stage.PREFLOP  # new hand started, because several players left the reason for this
            # behaviour is the side-pot
            assert env.players[0].stack == 174  # 100(main pot) + 75(1.side pot) - new small blind (1) because seat 1
            # or 2 has dealer-button = 174
            assert env.players[3].stack == 0  # seat 3 has smallest stack and seat 0 win already pot so stack = 0

            if env.winner_index[1] == 1:
                assert env.players[1].stack == 98  # 100 (start stack) - 25 (main pot) -25 (.side pot) + 50 (2.side pot
                # main Pot) - big blind (2) =  73
                assert env.players[2].stack == 0  # lose all by seat 3 and 1
            elif env.winner_index[1] == 2:
                assert env.players[2].stack == 98  # 100 (start stack) - 25 (main pot) -25 (.side pot) + 20 (2.side pot
                # main Pot) - big blind (2) =  73
                assert env.players[1].stack == 0  # lose all by seat 3 and 2
            else:
                assert False  # Only 4 players created in env
            winner_index_checked[0] = True  # same case second winner seat 1 or 2

        elif env.winner_index[0] == 1:
            assert env.stage == Stage.SHOWDOWN
            assert env.players[1].stack == 275
            assert env.players[0].stack == 0
            assert env.players[2].stack == 0
            assert env.players[3].stack == 0
            winner_index_checked[1] = True  # same case with index 1

        elif env.winner_index[0] == 2:
            assert env.stage == Stage.SHOWDOWN
            assert env.players[2].stack == 275
            assert env.players[1].stack == 0
            assert env.players[0].stack == 0
            assert env.players[3].stack == 0
            winner_index_checked[1] = True  # same case with index 1

        elif env.winner_index[0] == 3:
            assert env.stage == Stage.PREFLOP  # new hand started, because several players left the reason for this
            # behaviour is the side-pot
            if env.winner_index[1] == 0:
                assert env.players[0].stack == 73  # 50 (start stack) - 25 (1.main pot) + 50 (1. side pot) - new
                # big blind (2)= 73
                if env.winner_index[2] == 1:
                    assert env.players[1].stack == 100  # 100 (start stack) - 25 (1.side_pot) + 25 (2.side pot) = 100
                    assert env.players[3].stack == 99  # main pot (100) - new small blind (2) = 99
                    assert env.players[2].stack == 0  # lose every pot
                    winner_index_checked[2] = True  # same case with index 2
                elif env.winner_index[2] == 2:
                    assert env.players[2].stack == 100  # 100 (start stack) - 25 (1.side_pot) + 25 (2.side pot) = 100
                    assert env.players[3].stack == 99  # main pot (100) - new small blind (2) = 99
                    assert env.players[1].stack == 0  # lose every pot
                    winner_index_checked[2] = True  # same case with index 2
                else:
                    assert False  # Only 4 players created in env

            if env.winner_index[1] == 1:
                assert env.players[1].stack == 173  # 100(start stack) + 175(side pot)- 100(main Pot) - new big
                # blind(2) = 173
                assert env.players[2].stack == 0  # lose all by seat 3 and 1
                assert env.players[0].stack == 0  # lose all by seat 3 and 1
                winner_index_checked[3] = True  # same case with index 3
            elif env.winner_index[1] == 2:
                assert env.players[2].stack == 173  # 100 (start stack) + 175 (side pot) - 100(main Pot)- new big
                # blind(2) = 173
                assert env.players[1].stack == 0  # lose all by seat 3 and 2
                assert env.players[0].stack == 0  # lose all by seat 3 and 2
                winner_index_checked[3] = True  # same case with index 3
        else:
            assert False  # Only 4 players created in env


def test_three_side_pots_check_everytime_smallest_stack_winning_pot():
    """Test three side pots everytime smallest stack wins the main pot or side pot"""
    cases_tested_successful = np.array([False, False])
    while cases_tested_successful.sum() != 2:
        env = _create_env(5)  # bet small blind and big blind
        env.players[0].stack = 60  # seat 0
        env.players[3].stack = 20  # seat 3
        env.players[4].stack = 40  # seat 4
        env.step(Action.ALL_IN)  # seat 3 goes all in
        env.step(Action.ALL_IN)  # seat 4 ALL_IN
        env.step(Action.ALL_IN)  # seat 0 ALL_IN
        env.step(Action.ALL_IN)  # seat 1 small blind ALL_IN
        env.step(Action.CALL)  # seat 2 big blind ALL_IN

        if env.winner_index[0] == 3:
            assert env.stage == Stage.PREFLOP  # new hand started, because several players left the reason for this
            # behaviour is the side-pot
            assert env.players[3].stack == 99  # 5 * 20 - small blind (1 because dealer is 1 position before) = 99

            if env.winner_index[1] == 4:
                assert env.players[4].stack == 78  # 4 * 20 - big blind = 78
                if env.winner_index[2] == 0:
                    assert env.players[0].stack == 60  # 3 * 20 = 60
                    if env.winner_index[3] == 1:
                        assert env.players[1].stack == 80  # 2 * 40 = 80
                        cases_tested_successful[0] = True
                    if env.winner_index[3] == 2:
                        assert env.players[2].stack == 80  # 2 * 40 = 80
                        cases_tested_successful[1] = True


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
