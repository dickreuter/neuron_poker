"""Enums"""
from enum import Enum


class Action(Enum):
    """Allowed actions"""

    FOLD = 0
    CHECK = 1
    CALL = 2
    RAISE_3BB = 3
    RAISE_HALF_POT = 3
    RAISE_POT = 4
    RAISE_2POT = 5
    ALL_IN = 6
    SMALL_BLIND = 7
    BIG_BLIND = 8


class Stage(Enum):
    """Allowed actions"""

    PREFLOP = 0
    FLOP = 1
    TURN = 2
    RIVER = 3
    END_HIDDEN = 4
    SHOWDOWN = 5
