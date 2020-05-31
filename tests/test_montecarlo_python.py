"""Tests for python based equity calculator."""

import logging
import time

import numpy as np

from tools import montecarlo_python

simulator = montecarlo_python.MonteCarlo()

log = logging.getLogger(__name__)


def _runner(simulation, my_cards, cards_on_table, players, expected_results, opponent_range=1.0):
    max_runs = 15000  # maximum number of montecarlo runs
    test_runs = 5  # make several testruns to get standard deviation of winning probability
    secs = 1  # cut simulation short if amount of seconds are exceeded

    total_result = []
    for _ in range(test_runs):
        start_time = time.time() + secs
        simulation.run_montecarlo(my_cards, cards_on_table, players, 1, maxRuns=max_runs,
                                  timeout=start_time, ghost_cards='', opponent_range=opponent_range)
        equity = simulation.equity
        total_result.append(equity * 100)
        log.info("--- %s seconds ---" % (time.time() - start_time))

        for keys, values in simulation.winTypesDict:
            log.info(keys + ": " + (str(np.round(values * 100, 2))))
        log.info("Equity: " + str(np.round(equity * 100, 2)))
        assert abs(sum(list(simulation.winnerCardTypeList.values())) - equity) < 0.0001

    stdev = np.std(total_result)
    avg = np.mean(total_result)

    log.info("Mean: " + str(avg))
    log.info("Stdev: " + str(stdev))

    assert abs(avg - expected_results) < 3
    assert abs(stdev) < 3


def test_montecarlo1():
    """Montecarlo test"""
    my_cards = [['3H', '3S']]
    cards_on_table = ['8S', '4S', 'QH', '8C', '4H']
    expected_results = 40.2
    players = 2
    _runner(simulator, my_cards, cards_on_table, players, expected_results)


def test_montecarlo2():
    """Montecarlo test"""
    my_cards = [['8H', '8D']]
    cards_on_table = ['QH', '7H', '9H', 'JH', 'TH']
    expected_results = 95.6
    players = 2
    _runner(simulator, my_cards, cards_on_table, players, expected_results)


def test_montecarlo3():
    """Montecarlo test"""
    my_cards = [['AS', 'KS']]
    cards_on_table = []
    expected_results = 49.9 + 1.9
    players = 3
    _runner(simulator, my_cards, cards_on_table, players, expected_results)


def test_montecarlo4():
    """Montecarlo test"""
    my_cards = [['AS', 'KS']]
    cards_on_table = []
    expected_results = 66.1 + 1.6
    players = 2
    _runner(simulator, my_cards, cards_on_table, players, expected_results)


def test_montecarlo5():
    """Montecarlo test"""
    my_cards = [['8S', 'TS']]
    cards_on_table = ['8H', 'KS', '9S', 'TH', 'KH']
    expected_results = 71.5 + 5.9
    players = 2
    _runner(simulator, my_cards, cards_on_table, players, expected_results)


def test_montecarlo6():
    """Montecarlo test"""
    my_cards = [['8S', 'TS']]
    cards_on_table = ['2S', '3S', '4S', 'KS', 'AS']
    expected_results = 87
    players = 2
    _runner(simulator, my_cards, cards_on_table, players, expected_results)


def test_montecarlo7():
    """Montecarlo test"""
    my_cards = [['8S', '2S']]
    cards_on_table = ['5S', '3S', '4S', 'KS', 'AS']
    expected_results = 100
    players = 2
    _runner(simulator, my_cards, cards_on_table, players, expected_results)


def test_montecarlo8():
    """Montecarlo test"""
    my_cards = [['8S', 'TS']]
    cards_on_table = []
    expected_results = 22.6 + 2.9
    players = 5
    _runner(simulator, my_cards, cards_on_table, players, expected_results)


def test_montecarlo8b():
    """Montecarlo test"""
    my_cards = [['2C', 'QS']]
    cards_on_table = []
    expected_results = 49.6  # 45 win and 4 tie
    players = 2
    _runner(simulator, my_cards, cards_on_table, players, expected_results)


def test_montecarlo9():
    """Montecarlo test"""
    my_cards = [['7H', '7S']]
    cards_on_table = ['7C', '8C', '8S', 'AC', 'AH']
    expected_results = 83
    players = 2
    _runner(simulator, my_cards, cards_on_table, players, expected_results)


def test_montecarlo10():
    """Montecarlo test"""
    my_cards = [['3S', 'QH']]
    cards_on_table = ['2C', '5H', '7C']
    expected_results = 30.9 + 2.2
    players = 2
    _runner(simulator, my_cards, cards_on_table, players, expected_results)


def test_montecarlo11():
    """Montecarlo test"""
    my_cards = [['5C', 'JS']]
    cards_on_table = []
    expected_results = 23
    players = 4
    _runner(simulator, my_cards, cards_on_table, players, expected_results)


def test_montecarlo12():
    """Montecarlo test"""
    my_cards = [['TC', 'TH']]
    cards_on_table = ['4D', 'QD', 'KC']
    expected_results = 66.7 + 0.38
    players = 2
    _runner(simulator, my_cards, cards_on_table, players, expected_results)


def test_montecarlo13():
    """Montecarlo test"""
    my_cards = [['JH', 'QS']]
    cards_on_table = ['5C', 'JD', 'AS', 'KS', 'QD']
    expected_results = 77
    players = 2
    _runner(simulator, my_cards, cards_on_table, players, expected_results)


def test_montecarlo14():
    """Montecarlo test"""
    my_cards = [['2H', '8S']]
    cards_on_table = ['AC', 'AD', 'AS', 'KS', 'KD']
    expected_results = 95
    players = 2
    _runner(simulator, my_cards, cards_on_table, players, expected_results)


def test_montecarlo15():
    """Montecarlo test"""
    my_cards = [['KD', 'KS']]
    cards_on_table = ['4D', '6S', '9C', '9S', 'TC']
    expected_results = 88
    players = 2
    _runner(simulator, my_cards, cards_on_table, players, expected_results)


def test_montecarlo16():
    """Montecarlo test"""
    my_cards = [['5H', 'KD']]
    cards_on_table = ['KH', 'JS', '2C', 'QS']
    expected_results = 75.6 + 3.6
    players = 2
    _runner(simulator, my_cards, cards_on_table, players, expected_results)


def test_montecarlo17():
    """Montecarlo test"""
    my_cards = [['JD', 'JS']]
    cards_on_table = ['8C', 'TC', 'JC', '5H', 'QC']
    expected_results = 26.1
    players = 3
    _runner(simulator, my_cards, cards_on_table, players, expected_results)


def test_montecarlo19():
    """Montecarlo test"""
    my_cards = [['TD', '7D']]
    cards_on_table = ['8D', 'QD', '7C', '5D', '6D']
    expected_results = 87
    players = 2
    _runner(simulator, my_cards, cards_on_table, players, expected_results)


def test_montecarlo20():
    """Montecarlo test"""
    my_cards = [['KS', 'KC']]
    cards_on_table = ['3D', '9H', 'AS', '7S', 'QH']
    opponent_range = 0.25
    expected_results = 12.8
    players = 3
    _runner(simulator, my_cards, cards_on_table, players, expected_results, opponent_range=opponent_range)


def test_montecarlo21():
    """Montecarlo test"""
    my_cards = [{'AKO', 'AA'}]
    cards_on_table = ['3D', '9H', 'AS', '7S', 'QH']
    opponent_range = 0.25
    expected_results = 77.8
    players = 3
    _runner(simulator, my_cards, cards_on_table, players, expected_results, opponent_range=opponent_range)
