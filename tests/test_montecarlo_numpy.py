'''
Unittest for Montecarlosimulation. Checks if the differnt type of hands and their corresponding probability to win (equity)
is calculated correctly and within a given amount of time without a timeout
'''

import pytest
import time
import numpy as np


# pylint: skip-file

def testRun(my_cards, cards_on_table, players, expected_results, opponent_range=1):
    card_ranks_original = '23456789TJQKA'
    original_suits = 'CDHS'
    maxRuns = 15000  # maximum number of montecarlo runs
    testRuns = 5  # make several testruns to get standard deviation of winning probability
    secs = 1  # cut simulation short if amount of seconds are exceeded

    total_result = []
    for _ in range(testRuns):
        start_time = time.time() + secs
        # todo: assert equity
        print("--- %s seconds ---" % (time.time() - start_time))

    stdev = np.std(total_result)
    avg = np.mean(total_result)

    print("Mean: " + str(avg))
    print("Stdev: " + str(stdev))

    assert abs(avg - expected_results) < 2
    assert abs(stdev) - 0 < 2


@pytest.mark.skip
def test_monteCarlo():
    my_cards = [['3H', '3S']]
    cards_on_table = ['8S', '4S', 'QH', '8C', '4H']
    expected_results = 40.2
    players = 2
    testRun(my_cards, cards_on_table, players, expected_results)

    my_cards = [['8H', '8D']]
    cards_on_table = ['QH', '7H', '9H', 'JH', 'TH']
    expected_results = 95.6
    players = 2
    testRun(my_cards, cards_on_table, players, expected_results)

    my_cards = [['AS', 'KS']]
    cards_on_table = []
    expected_results = 49.9 + 1.9
    players = 3
    testRun(my_cards, cards_on_table, players, expected_results)

    my_cards = [['AS', 'KS']]
    cards_on_table = []
    expected_results = 66.1 + 1.6
    players = 2
    testRun(my_cards, cards_on_table, players, expected_results)

    my_cards = [['8S', 'TS']]
    cards_on_table = ['8H', 'KS', '9S', 'TH', 'KH']
    expected_results = 71.5 + 5.9
    players = 2
    testRun(my_cards, cards_on_table, players, expected_results)

    my_cards = [['8S', 'TS']]
    cards_on_table = ['2S', '3S', '4S', 'KS', 'AS']
    expected_results = 87
    players = 2
    testRun(my_cards, cards_on_table, players, expected_results)

    my_cards = [['8S', '2S']]
    cards_on_table = ['5S', '3S', '4S', 'KS', 'AS']
    expected_results = 100
    players = 2
    testRun(my_cards, cards_on_table, players, expected_results)

    my_cards = [['8S', 'TS']]
    cards_on_table = []
    expected_results = 22.6 + 2.9
    players = 5
    testRun(my_cards, cards_on_table, players, expected_results)

    my_cards = [['2C', 'QS']]
    cards_on_table = []
    expected_results = 49.6  # 45 win and 4 tie
    players = 2
    testRun(my_cards, cards_on_table, players, expected_results)

    my_cards = [['7H', '7S']]
    cards_on_table = ['7C', '8C', '8S', 'AC', 'AH']
    expected_results = 83
    players = 2
    testRun(my_cards, cards_on_table, players, expected_results)

    my_cards = [['3S', 'QH']]
    cards_on_table = ['2C', '5H', '7C']
    expected_results = 30.9 + 2.2
    players = 2
    testRun(my_cards, cards_on_table, players, expected_results)

    my_cards = [['5C', 'JS']]
    cards_on_table = []
    expected_results = 23
    players = 4
    testRun(my_cards, cards_on_table, players, expected_results)

    my_cards = [['TC', 'TH']]
    cards_on_table = ['4D', 'QD', 'KC']
    expected_results = 66.7 + 0.38
    players = 2
    testRun(my_cards, cards_on_table, players, expected_results)

    my_cards = [['JH', 'QS']]
    cards_on_table = ['5C', 'JD', 'AS', 'KS', 'QD']
    expected_results = 77
    players = 2
    testRun(my_cards, cards_on_table, players, expected_results)

    my_cards = [['2H', '8S']]
    cards_on_table = ['AC', 'AD', 'AS', 'KS', 'KD']
    expected_results = 95
    players = 2
    testRun(my_cards, cards_on_table, players, expected_results)

    my_cards = [['KD', 'KS']]
    cards_on_table = ['4D', '6S', '9C', '9S', 'TC']
    expected_results = 88
    players = 2
    testRun(my_cards, cards_on_table, players, expected_results)

    my_cards = [['5H', 'KD']]
    cards_on_table = ['KH', 'JS', '2C', 'QS']
    expected_results = 75.6 + 3.6
    players = 2
    testRun(my_cards, cards_on_table, players, expected_results)

    my_cards = [['JD', 'JS']]
    cards_on_table = ['8C', 'TC', 'JC', '5H', 'QC']
    expected_results = 26.1
    players = 3
    testRun(my_cards, cards_on_table, players, expected_results)

    my_cards = [['TD', '7D']]
    cards_on_table = ['8D', 'QD', '7C', '5D', '6D']
    expected_results = 87
    players = 2
    testRun(my_cards, cards_on_table, players, expected_results)

    my_cards = [['KS', 'KC']]
    cards_on_table = ['3D', '9H', 'AS', '7S', 'QH']
    opponent_range = 0.25
    expected_results = 12.8
    players = 3
    testRun(my_cards, cards_on_table, players, expected_results, opponent_range=opponent_range)

    my_cards = [{'AKO', 'AA'}]
    cards_on_table = ['3D', '9H', 'AS', '7S', 'QH']
    opponent_range = 0.25
    expected_results = 77.8
    players = 3
    testRun(my_cards, cards_on_table, players, expected_results, opponent_range=opponent_range)
