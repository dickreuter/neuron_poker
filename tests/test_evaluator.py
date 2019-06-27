"""Test Hand evaluation."""
import logging

from tools.hand_evaluator import eval_best_hand

log = logging.getLogger(__name__)


def test_evaluator1():
    """Hand evaluator test"""
    cards = [['3H', '3S', '4H', '4S', '8S', '8C', 'QH'],
             ['KH', '6C', '4H', '4S', '8S', '8C', 'QH']]
    expected = 1
    winner, _ = eval_best_hand(cards)
    assert winner == cards[expected]


def test_evaluator2():
    """Hand evaluator test"""
    cards = [['8H', '8D', 'QH', '7H', '9H', 'JH', 'TH'],
             ['KH', '6C', 'QH', '7H', '9H', 'JH', 'TH']]
    expected = 1
    winner, _ = eval_best_hand(cards)
    assert winner == cards[expected]


def test_evaluator3():
    """Hand evaluator test"""
    cards = [['AS', 'KS', 'TS', '9S', '7S', '2H', '2H'],
             ['AS', 'KS', 'TS', '9S', '8S', '2H', '2H']]
    expected = 1
    winner, _ = eval_best_hand(cards)
    assert winner == cards[expected]


def test_evaluator4():
    """Hand evaluator test"""
    cards = [['8S', 'TS', '8H', 'KS', '9S', 'TH', 'KH'],
             ['TD', '7S', '8H', 'KS', '9S', 'TH', 'KH']]
    expected = 0
    winner, _ = eval_best_hand(cards)
    assert winner == cards[expected]


def test_evaluator5():
    """Hand evaluator test"""
    cards = [['2D', '2H', 'AS', 'AD', 'AH', '8S', '7H'],
             ['7C', '7S', '7H', 'AD', 'AS', '8S', '8H']]
    expected = 0
    winner, _ = eval_best_hand(cards)
    assert winner == cards[expected]


def test_evaluator6():
    """Hand evaluator test"""
    cards = [['7C', '7S', '7H', 'AD', 'KS', '5S', '8H'],
             ['2D', '3H', 'AS', '4D', '5H', '8S', '7H']]
    expected = 1
    winner, _ = eval_best_hand(cards)
    assert winner == cards[expected]


def test_evaluator6b():
    """Hand evaluator test"""
    cards = [['7C', '7C', 'AC', 'AC', '8C', '8S', '7H'],
             ['2C', '3C', '4C', '5C', '6C', '8S', 'KH']]
    expected = 1
    winner, _ = eval_best_hand(cards)
    assert winner == cards[expected]


def test_evaluator7():
    """Hand evaluator test"""
    cards = [['AC', 'JS', 'AS', '2D', '5H', '3S', '3H'],
             ['QD', 'JD', 'TS', '9D', '6H', '8S', 'KH'],
             ['2D', '3D', '4S', '5D', '6H', '8S', 'KH']]
    expected = 1
    winner, _ = eval_best_hand(cards)
    assert winner == cards[expected]


def test_evaluator8():
    """Hand evaluator test"""
    cards = [['7C', '5S', '3S', 'JD', '8H', '2S', 'KH'],
             ['AD', '3D', '4S', '5D', '9H', '8S', 'KH']]
    expected = 1
    winner, _ = eval_best_hand(cards)
    assert winner == cards[expected]


def test_evaluator9():
    """Hand evaluator test"""
    cards = [['2C', '2D', '4S', '4D', '4H', '8S', 'KH'],
             ['7C', '7S', '7D', '7H', '8H', '8S', 'JH']]
    expected = 1
    winner, _ = eval_best_hand(cards)
    assert winner == cards[expected]


def test_evaluator10():
    """Hand evaluator test"""
    cards = [['7C', '5S', '3S', 'JD', '8H', '2S', 'KH'],
             ['AD', '3D', '3S', '5D', '9H', '8S', 'KH']]
    expected = 1
    winner, _ = eval_best_hand(cards)
    assert winner == cards[expected]


def test_evaluator11():
    """Hand evaluator test"""
    cards = [['7H', '7S', '3S', 'JD', '8H', '2S', 'KH'],
             ['7D', '3D', '3S', '7C', '9H', '8S', 'KH']]
    expected = 1
    winner, _ = eval_best_hand(cards)
    assert winner == cards[expected]


def test_evaluator12():
    """Hand evaluator test"""
    cards = [['AS', '8H', 'TS', 'JH', '3H', '2H', 'AH'],
             ['QD', 'QH', 'TS', 'JH', '3H', '2H', 'AH']]
    expected = 1
    winner, _ = eval_best_hand(cards)
    assert winner == cards[expected]


def test_evaluator13():
    """Hand evaluator test"""
    cards = [['9S', '7H', 'KS', 'KH', 'AH', 'AS', 'AC'],
             ['8D', '2H', 'KS', 'KH', 'AH', 'AS', 'AC']]
    expected = 0
    winner, _ = eval_best_hand(cards)
    assert winner == cards[expected]
