"""Groupier functions"""
import logging
from enum import Enum

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from gym import Env

from gym_env.rendering import PygletWindow, WHITE, RED, GREEN, BLUE
from tools.hand_evaluator import get_winner
from tools.helper import flatten
from tools.montecarlo_python import get_equity

__author__ = 'Nicolas Dickreuter'
log = logging.getLogger(__name__)


class CommunityData:
    """Data available to everybody"""

    def __init__(self, num_players):
        """data"""
        self.current_player_position = [False] * num_players  # ix[0] = dealer
        self.stage = [False] * 4  # one hot: preflop, flop, turn, river
        self.community_pot = None
        self.current_round_pot = None
        self.active_players = [False] * num_players  # one hot encoded, 0 = dealer
        self.big_blind = 0
        self.small_blind = 0


class StageData:
    """Preflop, flop, turn and river"""

    def __init__(self, num_players):
        """data"""
        self.calls = [False] * num_players  # ix[0] = dealer
        self.raises = [False] * num_players  # ix[0] = dealer
        self.min_call_at_action = [0] * num_players  # ix[0] = dealer
        self.contribution = [0] * num_players  # ix[0] = dealer
        self.stack_at_action = [0] * num_players  # ix[0] = dealer
        self.community_pot_at_action = [0] * num_players  # ix[0] = dealer


class PlayerData:
    "Player specific information"

    def __init__(self):
        """data"""
        self.position = None
        self.equity_to_river_alive = 0
        self.equity_to_river_2plr = 0
        self.equity_to_river_3plr = 0
        self.stack = None


class Action(Enum):
    """Allowed actions"""

    FOLD = 0
    CHECK = 1
    CALL = 2
    RAISE_3BB = 3
    RAISE_HAlF_POT = 4
    RAISE_POT = 5
    RAISE_2POT = 6
    ALL_IN = 7
    SMALL_BLIND = 8
    BIG_BLIND = 9


class Stage(Enum):
    """Allowed actions"""

    PREFLOP = 0
    FLOP = 1
    TURN = 2
    RIVER = 3
    END_HIDDEN = 4
    SHOWDOWN = 5


class HoldemTable(Env):
    """Pokergame environment"""

    def __init__(self, num_of_players=6, initial_stacks=100, small_blind=1, big_blind=2, render=False):
        """The table needs to be initialized once at the beginning"""
        self.num_of_players = num_of_players
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.render_switch = render
        self.players = []
        self.table_cards = None
        self.dealer_pos = None
        self.player_status = []  # one hot encoded
        self.current_player = None
        self.player_cycle = None  # cycle iterator
        self.stage = None
        self.last_player_pot = None
        self.viewer = None
        self.player_max_win = None  # used for side pots
        self.second_round = False
        self.last_caller = None
        self.last_raiser = None
        self.raisers = []
        self.callers = []
        self.played_in_round = None
        self.min_call = None
        self.community_data = None
        self.player_data = None
        self.stage_data = None
        self.deck = None
        self.winner_ix = None
        self.initial_stacks = initial_stacks

        # pots
        self.community_pot = 0
        self.current_round_pot = 9
        self.player_pots = None  # individual player pots

        self.observation = None
        self.reward = None
        self.info = None
        self.done = False
        self.funds_history = None
        self.array_everything = None

    def reset(self):
        """Reset after game over."""
        self.observation = None
        self.reward = None
        self.info = None
        self.done = False
        self.funds_history = pd.DataFrame()
        for player in self.players:
            player.stack = self.initial_stacks

        self.dealer_pos = 0
        self.player_cycle = PlayerCycle(self.players, dealer_idx=-1, max_steps_after_raiser=len(self.players))
        self._start_new_hand()
        self._get_environment()

        # auto play for agents where autoplay is set
        if hasattr(self.current_player, 'agent_obj') and not self.done:
            self.step()

        return self.array_everything

    def step(self, action=None):  # pylint: disable=arguments-differ
        """
        Next player makes a move and a new environment is observed.

        Args:
            action: Used for testing only. Needs to be of Action type

        """
        self.observation_space = self.array_everything.shape

        if not action:
            if not hasattr(self.current_player.agent_obj, 'autoplay'):
                # only player shell, external model required to by calling step method
                # todo: reward should be for last played action of external model
                return self.array_everything, self.reward, self.done, self.info
            action = self.current_player.agent_obj.action(self.action_space, self.observation)
        self._process_decision(action)

        self._next_player()

        if self.stage in [Stage.END_HIDDEN, Stage.SHOWDOWN]:
            self._end_hand()
            self._start_new_hand()

        self.player_cycle.update_alive()
        self._get_environment()

        # auto play for agents where autoplay is set
        if hasattr(self.current_player, 'agent_obj') and not self.done:
            self.step()

        return self.observation, self.reward, self.done, self.info

    def _get_environment(self):
        """Observe the environment"""
        if not self.done:
            self._get_legal_moves()

        self.observation = None
        self.reward = None
        self.info = None

        self.community_data = CommunityData(len(self.players))
        self.community_data.community_pot = self.community_pot
        self.community_data.current_round_pot = self.current_round_pot
        self.community_data.small_blind = self.small_blind
        self.community_data.big_blind = self.big_blind
        self.community_data.stage[np.minimum(self.stage.value, 3)] = 1
        # self.cummunity_data.active_players

        self.player_data = PlayerData()
        self.player_data.stack = [player.stack for player in self.players]

        if not self.current_player:  # game over
            self.current_player = self.players[self.winner_ix]

        self.player_data.position = self.current_player.seat
        self.current_player.equity_alive = get_equity(self.current_player.cards, self.table_cards,
                                                      sum(self.player_cycle.alive))
        self.player_data.equity_to_river_alive = self.current_player.equity_alive

        arr1 = np.array(list(flatten(self.player_data.__dict__.values())))
        arr2 = np.array(list(flatten(self.community_data.__dict__.values())))
        arr3 = np.array([list(flatten(sd.__dict__.values())) for sd in self.stage_data]).flatten()

        self.array_everything = np.concatenate([arr1, arr2, arr3]).flatten()

        self.observation = {'array_everything': self.array_everything,
                            'player_data': self.player_data,
                            'community_data': self.community_data,
                            'stage_data': self.stage_data
                            }
        self._get_legal_moves()

        self.reward = self.current_player.stack + self.player_data.equity_to_river_alive * self.community_pot

        if self.render_switch:
            self.render()

    def _process_decision(self, action):  # pylint: disable=too-many-statements
        """Process the decisions that have been made by an agent."""
        if action not in [Action.SMALL_BLIND, Action.BIG_BLIND]:
            assert action in set(self.action_space), "Illegal decision"

        if action == Action.FOLD:
            self.player_cycle.deactivate_current()
            self.player_cycle.mark_folder()
            log.info(f"Seat {self.current_player.seat}: {action} - Remaining stack: {self.current_player.stack}, "
                     f"Round pot: {self.current_round_pot}, Community pot: {self.community_pot}, "
                     f"player pot: {self.player_pots[self.current_player.seat]}")
            return

        if action == Action.CALL:
            contribution = min(self.last_player_pot - self.player_pots[self.current_player.seat],
                               self.current_player.stack)
            self.callers.append(self.current_player.seat)
            self.last_caller = self.current_player.seat

        # verify the player has enough in his stack
        elif action == Action.CHECK:
            contribution = 0
            self.player_cycle.mark_checker()

        elif action == Action.RAISE_3BB:
            contribution = (self.community_pot + self.big_blind) * 3
            self.raisers.append(self.current_player.seat)

        elif action == Action.RAISE_HAlF_POT:
            contribution = (self.community_pot + self.current_round_pot) / 2
            self.raisers.append(self.current_player.seat)

        elif action == Action.RAISE_POT:
            contribution = (self.community_pot + self.current_round_pot)
            self.raisers.append(self.current_player.seat)

        elif action == Action.RAISE_2POT:
            contribution = (self.community_pot + self.current_round_pot) * 2
            self.raisers.append(self.current_player.seat)

        elif action == Action.ALL_IN:
            contribution = self.current_player.stack
            self.raisers.append(self.current_player.seat)

        elif action == Action.SMALL_BLIND:
            contribution = np.minimum(self.small_blind, self.current_player.stack)
            self.last_raiser = self.current_player.seat

        elif action == Action.BIG_BLIND:
            contribution = np.minimum(self.big_blind, self.current_player.stack)
            self.last_raiser = self.current_player.seat
            self.player_cycle.mark_bb()
        else:
            raise RuntimeError("Illegal action.")

        if contribution > self.min_call:
            self.player_cycle.mark_raiser()
            self.last_raiser = self.current_player.seat

        self.current_player.stack -= contribution
        self.player_pots[self.current_player.seat] += contribution
        self.current_round_pot += contribution
        self.last_player_pot = self.player_pots[self.current_player.seat]

        if self.current_player.stack == 0 and contribution > 0:
            self.player_cycle.mark_out_of_cash_but_contributed()

        self.min_call = max(self.min_call, contribution)

        self.current_player.actions.append(action)
        self.current_player.last_action_in_stage = action.name
        self.current_player.temp_stack.append(self.current_player.stack)

        self.player_max_win[self.current_player.seat] += contribution  # side pot

        pos = self.player_cycle.idx
        rnd = self.stage.value + self.second_round
        self.stage_data[rnd].calls[pos] = action == Action.CALL
        self.stage_data[rnd].raises[pos] = action in [Action.RAISE_2POT, Action.RAISE_HAlF_POT, Action.RAISE_POT]
        self.stage_data[rnd].min_call_at_action[pos] = self.min_call
        self.stage_data[rnd].community_pot_at_action[pos] = self.community_pot
        self.stage_data[rnd].contribution[pos] = contribution
        self.stage_data[rnd].stack_at_action[pos] = self.current_player.stack

        log.info(f"Seat {self.current_player.seat}: {action} - Remaining stack: {self.current_player.stack}, "
                 f"Round pot: {self.current_round_pot}, Community pot: {self.community_pot}, "
                 f"player pot: {self.player_pots[self.current_player.seat]}")

    def _start_new_hand(self):
        """Deal new cards to players and reset table states."""
        self._save_funds_history()

        if self._check_game_over():
            return

        log.info("")
        log.info("++++++++++++++++++")
        log.info("Starting new hand.")
        log.info("++++++++++++++++++")
        self.table_cards = []
        self._create_card_deck()
        self.stage = Stage.PREFLOP

        # preflop round1,2, flop>: round 1,2, turn etc...
        self.stage_data = [StageData(len(self.players)) for _ in range(8)]

        # pots
        self.community_pot = 0
        self.current_round_pot = 0
        self.player_pots = [0] * len(self.players)
        self.player_max_win = [0] * len(self.players)
        self.last_player_pot = 0
        self.played_in_round = 0

        for player in self.players:
            player.cards = []

        self._next_dealer()

        self._distribute_cards()
        self._initiate_round()

    def _save_funds_history(self):
        """Keep track of player funds history"""
        funds_dict = {i: player.stack for i, player in enumerate(self.players)}
        self.funds_history = pd.concat([self.funds_history, pd.DataFrame(funds_dict, index=[0])])

    def _check_game_over(self):
        """Check if only one player has money left"""
        player_alive = []
        self.player_cycle.new_hand_reset()

        for idx, player in enumerate(self.players):
            if player.stack > 0:
                player_alive.append(True)
            else:
                self.player_status.append(False)
                self.player_cycle.deactivate_player(idx)

        remaining_players = sum(player_alive)
        if remaining_players < 2:
            self._game_over()
            return True
        return False

    def _game_over(self):
        """End of an episode."""
        log.info("Game over.")
        self.done = True
        player_names = [f"{i} - {player.name}" for i, player in enumerate(self.players)]
        self.funds_history.columns = player_names
        self.funds_history.reset_index(drop=True).plot()
        log.info(self.funds_history)
        plt.show()

    def _initiate_round(self):
        """A new round (flop, turn, river) is initiated"""
        self.last_caller = None
        self.last_raiser = None
        self.raisers = []
        self.callers = []
        self.min_call = 0
        for player in self.players:
            player.last_action_in_stage = ''
        self.player_cycle.new_round_reset()

        if self.stage == Stage.PREFLOP:
            log.info("")
            log.info("===Round: Stage: PREFLOP")
            # max steps total will be adjusted again at bb
            self.player_cycle.max_steps_total = len(self.players) * 2 + 2

            self._next_player()
            self._process_decision(Action.SMALL_BLIND)
            self._next_player()
            self._process_decision(Action.BIG_BLIND)
            self._next_player()

        elif self.stage in [Stage.FLOP, Stage.TURN, Stage.RIVER]:
            self.player_cycle.max_steps_total = len(self.players) * 2

            self._next_player()

        elif self.stage == Stage.SHOWDOWN:
            log.info("Showdown")

        else:
            raise RuntimeError()

    def add_player(self, agent):
        """Add a player to the table. Has to happen at the very beginning"""
        player = PlayerShell(stack_size=self.initial_stacks, name=agent.name)
        player.agent_obj = agent
        player.seat = len(self.players)  # assign next seat number to player
        player.stack = self.initial_stacks
        self.players.append(player)
        self.player_status = [True] * len(self.players)
        self.player_pots = [0] * len(self.players)

    def _end_round(self):
        """End of preflop, flop, turn or river"""
        self._close_round()
        if self.stage == Stage.PREFLOP:
            self.stage = Stage.FLOP
            self._distribute_cards_to_table(3)

        elif self.stage == Stage.FLOP:
            self.stage = Stage.TURN
            self._distribute_cards_to_table(1)

        elif self.stage == Stage.TURN:
            self.stage = Stage.RIVER
            self._distribute_cards_to_table(1)

        elif self.stage == Stage.RIVER:
            self.stage = Stage.SHOWDOWN

        log.info("--------------------------------")
        log.info(f"===ROUND: {self.stage} ===")
        self._clean_up_pots()

    def _clean_up_pots(self):
        self.community_pot += self.current_round_pot
        self.current_round_pot = 0
        self.player_pots = [0] * len(self.players)

    def _end_hand(self):
        self._clean_up_pots()
        self.winner_ix = self._get_winner()
        self._award_winner(self.winner_ix)

    def _get_winner(self):
        """Determine which player has won the hand"""
        potential_winners = self.player_cycle.get_potential_winners()

        potential_winner_idx = [i for i, potential_winner in enumerate(potential_winners) if potential_winner]
        if sum(potential_winners) == 1:
            winner_ix = [i for i, active in enumerate(potential_winners) if active][0]
            winning_card_type = 'Only remaining player in round'

        else:
            assert self.stage == Stage.SHOWDOWN
            remaining_player_winner_ix, winning_card_type = get_winner([player.cards
                                                                        for ix, player in enumerate(self.players) if
                                                                        potential_winners[ix]],
                                                                       self.table_cards)
            winner_ix = potential_winner_idx[remaining_player_winner_ix]
        log.info(f"Player {winner_ix} won: {winning_card_type}")
        return winner_ix

    def _award_winner(self, winner_ix):
        """Hand the pot to the winner and handle side pots"""
        max_win_per_player_for_winner = self.player_max_win[winner_ix]
        total_winnings = sum(np.minimum(max_win_per_player_for_winner, self.player_max_win))
        remains = np.maximum(0, np.array(self.player_max_win) - max_win_per_player_for_winner)  # to be returned

        self.players[winner_ix].stack += total_winnings
        self.winner_ix = winner_ix
        if total_winnings < sum(self.player_max_win):
            log.info("Returning side pots")
            for i, player in enumerate(self.players):
                player.stack += remains[i]

    def _next_dealer(self):
        self.dealer_pos = self.player_cycle.next_dealer().seat

    def _next_player(self):
        """Move to the next player"""
        self.current_player = self.player_cycle.next_player()
        if not self.current_player:
            if sum(self.player_cycle.alive) < 2:
                log.info("Only one player remaining in round")
                self.stage = Stage.END_HIDDEN

            else:
                log.info("End round - no current player returned")
                self._end_round()
                self._initiate_round()

        elif self.current_player == 'max_steps_total' or self.current_player == 'max_steps_after_raiser':
            log.debug(self.current_player)
            log.info("End of round ")
            self._end_round()
            return

    def _get_legal_moves(self):
        """Determine what moves are allowed in the current state"""
        self.action_space = []
        if self.current_round_pot == 0:
            self.action_space.append(Action.CHECK)
        else:
            self.action_space.append(Action.CALL)
            self.action_space.append(Action.FOLD)

        if self.player_cycle.is_raising_allowed():
            if self.current_player.stack >= 3 * self.big_blind >= self.min_call:
                self.action_space.append(Action.RAISE_3BB)

            if self.current_player.stack >= ((self.community_pot + self.current_round_pot) / 2) >= self.min_call:
                self.action_space.append(Action.RAISE_HAlF_POT)

            if self.current_player.stack >= (self.community_pot + self.current_round_pot) >= self.min_call:
                self.action_space.append(Action.RAISE_POT)

            if self.current_player.stack >= ((self.community_pot + self.current_round_pot) * 2) >= self.min_call:
                self.action_space.append(Action.RAISE_2POT)

            if self.current_player.stack > 0:
                self.action_space.append(Action.ALL_IN)

        log.debug(f"Community+current round pot pot: {self.community_pot + self.current_round_pot}")

    def _close_round(self):
        """put player_pots into community pots"""
        self.community_pot += sum(self.player_pots)
        self.player_pots = [0] * len(self.players)
        self.played_in_round = 0

    def _create_card_deck(self):
        values = "23456789TJQKA"
        suites = "CDHS"
        self.deck = []  # contains cards in the deck
        _ = [self.deck.append(x + y) for x in values for y in suites]

    def _distribute_cards(self):
        log.info(f"Dealer is at position {self.dealer_pos}")
        for player in self.players:
            player.cards = []
            if player.stack <= 0:
                continue
            for _ in range(2):
                card = np.random.randint(0, len(self.deck))
                player.cards.append(self.deck.pop(card))
            log.info(f"Player {player.seat} got {player.cards} and ${player.stack}")

    def _distribute_cards_to_table(self, amount_of_cards):
        for _ in range(amount_of_cards):
            card = np.random.randint(0, len(self.deck))
            self.table_cards.append(self.deck.pop(card))
        log.info(f"Cards on table: {self.table_cards}")

    def render(self, mode='human'):
        """Render the current state"""
        screen_width = 600
        screen_height = 400
        table_radius = 200
        face_radius = 10

        if self.viewer is None:
            self.viewer = PygletWindow(screen_width + 50, screen_height + 50)
        self.viewer.reset()
        self.viewer.circle(screen_width / 2, screen_height / 2, table_radius, color=BLUE,
                           thickness=0)

        for i in range(len(self.players)):
            degrees = i * (360 / len(self.players))
            radian = (degrees * (np.pi / 180))
            x = (face_radius + table_radius) * np.cos(radian) + screen_width / 2
            y = (face_radius + table_radius) * np.sin(radian) + screen_height / 2
            if self.player_cycle.alive[i]:
                color = GREEN
            else:
                color = RED
            self.viewer.circle(x, y, face_radius, color=color, thickness=2)

            try:
                if i == self.current_player.seat:
                    self.viewer.rectangle(x - 60, y, 150, -50, (255, 0, 0, 10))
            except AttributeError:
                pass
            self.viewer.text(f"{self.players[i].name}", x - 60, y - 15,
                             font_size=10,
                             color=WHITE)
            self.viewer.text(f"Player {self.players[i].seat}: {self.players[i].cards}", x - 60, y,
                             font_size=10,
                             color=WHITE)
            equity_alive = int(round(float(self.players[i].equity_alive) * 100))

            self.viewer.text(f"${self.players[i].stack} (EQ: {equity_alive}%)", x - 60, y + 15, font_size=10,
                             color=WHITE)
            try:
                self.viewer.text(self.players[i].last_action_in_stage, x - 60, y + 30, font_size=10, color=WHITE)
            except IndexError:
                pass
            x_inner = (-face_radius + table_radius - 60) * np.cos(radian) + screen_width / 2
            y_inner = (-face_radius + table_radius - 60) * np.sin(radian) + screen_height / 2
            self.viewer.text(f"${self.player_pots[i]}", x_inner, y_inner, font_size=10, color=WHITE)
            self.viewer.text(f"{self.table_cards}", screen_width / 2 - 40, screen_height / 2, font_size=10,
                             color=WHITE)
            self.viewer.text(f"${self.community_pot}", screen_width / 2 - 15, screen_height / 2 + 30, font_size=10,
                             color=WHITE)
            self.viewer.text(f"${self.current_round_pot}", screen_width / 2 - 15, screen_height / 2 + 50,
                             font_size=10,
                             color=WHITE)

            x_button = (-face_radius + table_radius - 20) * np.cos(radian) + screen_width / 2
            y_button = (-face_radius + table_radius - 20) * np.sin(radian) + screen_height / 2
            try:
                if i == self.player_cycle.dealer_idx:
                    self.viewer.circle(x_button, y_button, 5, color=BLUE, thickness=2)
            except AttributeError:
                pass

        self.viewer.update()


class PlayerCycle:
    """Handle the circularity of the Table."""

    def __init__(self, lst, start_idx=0, dealer_idx=0, max_steps_total=None,
                 last_raiser_step=None, max_steps_after_raiser=None):
        """Cycle over a list"""
        self.lst = lst
        self.start_idx = start_idx
        self.size = len(lst)
        self.max_steps_total = max_steps_total
        self.last_raiser_step = last_raiser_step
        self.max_steps_after_raiser = max_steps_after_raiser
        self.last_raiser = None
        self.counter = 0
        self.second_round = False
        self.idx = 0
        self.dealer_idx = dealer_idx
        self.can_still_make_moves_in_this_hand = []  # if the player can still play in this round
        self.alive = [True] * len(self.lst)  # if the player can still play in the following rounds
        self.out_of_cash_but_contributed = [False] * len(self.lst)
        self.new_hand_reset()
        self.checkers = 0
        self.folder = None

    def new_hand_reset(self):
        """Reset state if a new hand is dealt"""
        self.idx = self.start_idx
        self.can_still_make_moves_in_this_hand = [True] * len(self.lst)
        self.out_of_cash_but_contributed = [False] * len(self.lst)
        self.folder = [False] * len(self.lst)
        self.counter = 0

    def new_round_reset(self):
        """Reset the state for the next stage: flop, turn or river"""
        self.counter = 0
        self.second_round = False
        self.idx = self.dealer_idx
        self.last_raiser_step = len(self.lst)
        self.checkers = 0

    def next_player(self, step=1):
        """Switch to the next player in the round."""
        if sum(np.array(self.can_still_make_moves_in_this_hand) + np.array(self.out_of_cash_but_contributed)) < 2:
            log.debug("Only one player remaining")
            return False  # only one player remains

        self.idx += step
        self.counter += step
        self.idx %= len(self.lst)
        if self.counter > len(self.lst):
            self.second_round = True
        if self.max_steps_total and (self.counter >= self.max_steps_total):
            log.debug("Max steps total has been reached")
            return False

        raiser_reference = self.last_raiser if self.last_raiser else 0
        if self.max_steps_after_raiser and (self.counter > self.max_steps_after_raiser + raiser_reference):
            log.debug("max steps after raiser has been reached")
            return False

        if self.checkers == sum(self.alive):
            log.debug("All players checked")
            return False

        while True:
            if self.can_still_make_moves_in_this_hand[self.idx]:
                break
            else:
                self.idx += 1
                self.counter += 1
                self.idx %= len(self.lst)
                if self.max_steps_total and self.counter >= self.max_steps_total:
                    log.debug("Max steps total has been reached after jumping some folders")
                    return False

        self.update_alive()
        return self.lst[self.idx]

    def next_dealer(self):
        """Move the dealer to the next player that's still in the round."""
        self.dealer_idx += 1
        self.dealer_idx %= len(self.lst)

        while True:
            if self.can_still_make_moves_in_this_hand[self.dealer_idx]:
                break
            else:
                self.dealer_idx += 1
                self.dealer_idx %= len(self.lst)

        return self.lst[self.dealer_idx]

    def set_idx(self, idx):
        """Set the index to a specific player"""
        self.idx = idx

    def deactivate_player(self, idx):
        """Deactivate a pleyr if he has folded or is out of cash."""
        assert self.can_still_make_moves_in_this_hand[idx], "Already deactivated"
        self.can_still_make_moves_in_this_hand[idx] = False

    def deactivate_current(self):
        """Deactivate the current player if he has folded or is out of cash."""
        assert self.can_still_make_moves_in_this_hand[self.idx], "Already deactivated"
        self.can_still_make_moves_in_this_hand[self.idx] = False

    def mark_folder(self):
        """Mark a player as no longer eligible to win cash from the current hand"""
        self.folder[self.idx] = True

    def mark_raiser(self):
        """Mark a raise for the current player."""
        self.last_raiser = self.counter

    def mark_checker(self):
        """Counter the number of checks in the round"""
        self.checkers += 1

    def mark_out_of_cash_but_contributed(self):
        """Mark current player as a raiser or caller, but is out of cash."""
        self.out_of_cash_but_contributed[self.idx] = True
        self.deactivate_current()

    def mark_bb(self):
        """Ensure bb can raise"""
        self.last_raiser_step = self.counter + len(self.lst)
        self.max_steps_total = self.counter + len(self.lst) * 2

    def is_raising_allowed(self):
        """Check if raising is still allowed at this position"""
        return self.counter <= self.last_raiser_step

    def update_alive(self):
        """Update the alive property"""
        self.alive = np.array(self.can_still_make_moves_in_this_hand) + \
                     np.array(self.out_of_cash_but_contributed)

    def get_potential_winners(self):
        """Players eligible to win the pot"""
        potential_winners = np.logical_and(np.logical_or(np.array(self.can_still_make_moves_in_this_hand),
                                                         np.array(self.out_of_cash_but_contributed)),
                                           np.logical_not(np.array(self.folder)))
        return potential_winners


class PlayerShell:
    """Player shell"""

    def __init__(self, stack_size, name):
        """Initiaization of an agent"""
        self.stack = stack_size
        self.seat = None
        self.equity_alive = 0
        self.actions = []
        self.last_action_in_stage = ''
        self.temp_stack = []
        self.name = name
        self.agent_obj = None
