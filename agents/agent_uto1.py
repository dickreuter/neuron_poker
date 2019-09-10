"""UTO1 player"""
import random

from gym_env.env import Action
from gym_env.env import Stage
from tools.deuces.deuces import Card as Evcard, Evaluator as Ev, lookup as L

autoplay = True  # play automatically if played against keras-rl


class Player:
    """Mandatory class with the player methods"""

    def __init__(self, name='Uto1',
                 min_call_equity=0.56, min_bet_equity=0.66, min_call_equity_allin=0.6592,
                 max_vip=0.26):
        """Initiaization of an agent"""
        self.autoplay = True
        self.equity_alive = 0
        self.name = name
        self.min_call_equity = min_call_equity
        self.min_bet_equity = min_bet_equity
        self.min_call_equity_allin = min_call_equity_allin
        self.position_modifier = 0.05
        self.max_vip = max_vip
        self.number_of_hands = 0
        self.number_of_entries = 0
        self.vip_warning = False


    def action(self, action_space, observation, info):  # pylint: disable=no-self-use
        """Mandatory method that calculates the move based on the observation array and the action space."""
        _ = observation
        equity_alive = info['player_data']['equity_to_river_alive']
        my_position = info['player_data']['position']
        stack = info['player_data']['stack_amount'] #number
        dealer_position = info['community_data']['dealer_position']
        # active_players = info['community_data']['active_players']
        min_call = info['community_data']['min_call']
        big_blind = info['community_data']['big_blind']
        stage = info['community_data']['game_stage']
        first_decision = info['player_data']['first_decision']
        rank = 0

        if stage != Stage.PREFLOP:
            rank = self.get_deuces_rank(info)

        rank = self.get_rank_pos_modifier(my_position, dealer_position, rank)
        equity_alive = self.get_equity_pos_modifier(my_position, dealer_position, equity_alive)

        increment1 = .1
        increment2 = .11
        action = Action.FOLD

        if first_decision:
            if self.number_of_entries > 10:
                self.vip_warning = (self.number_of_entries / self.number_of_hands) > self.max_vip
            self.number_of_hands += 1
            # do not you volunteer in the pot too often? be more pesymistic
            if self.vip_warning:
                equity_alive *= 1 - (3 * self.position_modifier)

        if stage == Stage.PREFLOP:
            if equity_alive > self.min_bet_equity + increment2 \
                    and (equity_alive >= 0.7754) \
                    and Action.ALL_IN in action_space:
                action = Action.ALL_IN

            elif equity_alive > self.min_bet_equity + increment1:
                if random.randint(1, 101) <= 8 and Action.ALL_IN in action_space:
                    action = Action.ALL_IN
                elif Action.RAISE_2POT in action_space:
                    action = Action.RAISE_2POT

            elif equity_alive > self.min_bet_equity and Action.RAISE_POT in action_space:
                action = Action.RAISE_POT

            elif equity_alive > self.min_bet_equity - increment1 and Action.RAISE_HALF_POT in action_space:
                action = Action.RAISE_HALF_POT

            elif equity_alive > self.min_call_equity and Action.CALL in action_space \
                    and ((equity_alive > self.min_call_equity_allin and min_call >= stack) or (
                    min_call < stack / 2 or min_call <= big_blind * 4)):
                action = Action.CALL

            elif Action.CHECK in action_space:
                action = Action.CHECK

            else:
                action = Action.FOLD

            if first_decision and action != Action.FOLD:
                self.number_of_entries += 1

        else:
            if equity_alive > self.min_bet_equity + increment2 \
                    and (rank <= 4000 or equity_alive >= 0.7754) \
                    and Action.ALL_IN in action_space:
                action = Action.ALL_IN

            elif equity_alive > self.min_bet_equity + increment1:
                if random.randint(1, 101) <= 8 and Action.ALL_IN in action_space:
                    action = Action.ALL_IN
                elif Action.RAISE_2POT in action_space:
                    action = Action.RAISE_2POT

            elif equity_alive > self.min_bet_equity and Action.RAISE_POT in action_space:
                action = Action.RAISE_POT

            elif equity_alive > self.min_bet_equity - increment1 and Action.RAISE_HALF_POT in action_space:
                action = Action.RAISE_HALF_POT

            elif equity_alive > self.min_call_equity and Action.CALL in action_space \
                    and (rank <= L.LookupTable.MAX_PAIR) \
                    and ((equity_alive > self.min_call_equity_allin and min_call >= stack) or (
                    min_call < stack / 2 or min_call <= big_blind * 4)):
                action = Action.CALL

            elif Action.CHECK in action_space:
                action = Action.CHECK

            else:
                action = Action.FOLD

        return action

    def get_rank_pos_modifier(self, my_position, dealer_position, rank):
        # it is always easier to play as a dealer...
        if my_position == dealer_position:
            rank *= 1 - (2 * self.position_modifier)
        elif dealer_position - 1 % 6 == my_position:
            rank *= 1 - (1 * self.position_modifier)
        # and more difficult to be the first one
        elif dealer_position + 1 % 6 == my_position:
            rank *= 1 + (2 * self.position_modifier)
        elif dealer_position + 2 % 6 == my_position:
            rank *= 1 + (1 * self.position_modifier)
        return rank

    def get_equity_pos_modifier(self, my_position, dealer_position, equity_alive):
        # it is always easier to play as a dealer...
        if my_position == dealer_position:
            equity_alive *= 1 + (2 * self.position_modifier)
        elif dealer_position - 1 % 6 == my_position:
            equity_alive *= 1 + (1 * self.position_modifier)
        # and more difficult to be the first one
        elif dealer_position + 1 % 6 == my_position:
            equity_alive *= 1 - (2 * self.position_modifier)
        elif dealer_position + 2 % 6 == my_position:
            equity_alive *= 1 - (1 * self.position_modifier)
        return equity_alive

    @staticmethod
    def get_deuces_rank(info):
        evaluator = Ev()
        if info['community_data']['game_stage'].value == 1:
            table_cards = [Evcard.new(info['community_data']['table_cards'][0]),
                           Evcard.new(info['community_data']['table_cards'][1]),
                           Evcard.new(info['community_data']['table_cards'][2])]
        elif info['community_data']['game_stage'].value == 2:
            table_cards = [Evcard.new(info['community_data']['table_cards'][0]),
                           Evcard.new(info['community_data']['table_cards'][1]),
                           Evcard.new(info['community_data']['table_cards'][2]),
                           Evcard.new(info['community_data']['table_cards'][3])]
        else:
            table_cards = [Evcard.new(info['community_data']['table_cards'][0]),
                           Evcard.new(info['community_data']['table_cards'][1]),
                           Evcard.new(info['community_data']['table_cards'][2]),
                           Evcard.new(info['community_data']['table_cards'][3]),
                           Evcard.new(info['community_data']['table_cards'][4])]
        hand_cards = [Evcard.new(info['player_data']['hand'][0]), Evcard.new(info['player_data']['hand'][1])]
        return evaluator.evaluate(hand_cards, table_cards)
