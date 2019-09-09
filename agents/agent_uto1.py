"""UTO1 player"""
import random
from gym_env.env import Action

from tools.deuces.deuces import Card as Evcard, Evaluator as Ev, lookup as L

autoplay = True  # play automatically if played against keras-rl


class Player:
    """Mandatory class with the player methods"""

    def __init__(self, name='Uto1'):
        """Initiaization of an agent"""
        self.equity_alive = 0
        self.name = name
        self.min_call_equity = 0.56
        self.min_bet_equity = 0.66
        self.min_call_equity_allin = 0.6592

        self.autoplay = True

    def action(self, action_space, observation, info):  # pylint: disable=no-self-use
        """Mandatory method that calculates the move based on the observation array and the action space."""
        _ = observation
        equity_alive = info['player_data']['equity_to_river_alive']
        my_position = info['player_data']['position']
        stack = info['player_data']['stack_amount'] #number
        dealer_position = info['community_data']['dealer_position']
        active_players = info['community_data']['active_players']
        min_call = info['community_data']['min_call']
        stage = info['community_data']['game_stage'].value
        rank = 0

        if stage > 0:
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
            rank = evaluator.evaluate(hand_cards, table_cards)

        increment1 = .1
        increment2 = .11
        action = Action.FOLD

        if equity_alive > self.min_bet_equity + increment2\
                and ((stage > 0 and rank <= 4000) or (equity_alive >= 0.7754))\
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

        elif equity_alive > self.min_call_equity and Action.CALL in action_space\
                and ((stage > 0 and rank <= L.LookupTable.MAX_PAIR) or (stage == 0))\
                and ((equity_alive > self.min_call_equity_allin and min_call >= stack) or (min_call < stack/2)):
            action = Action.CALL

        elif Action.CHECK in action_space:
            action = Action.CHECK

        else:
            action = Action.FOLD

        return action
