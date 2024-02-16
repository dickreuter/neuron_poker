"""Texas holdem hand evaluation."""

# pylint: disable=too-many-statements, too-many-branches, too-many-locals

CARD_RANKS_ORIGINAL = '23456789TJQKA'
SUITS_ORIGINAL = 'CDHS'


def get_winner(player_hands, table_cards):
    """Determine the winning hands of multiple players"""
    player_cards_with_table_cards = []
    for player_hand in player_hands:
        player_cards_with_table_cards.append(player_hand + table_cards)

    best_hand, winner_card_type = eval_best_hand(player_cards_with_table_cards)
    best_hand_ix = (player_cards_with_table_cards.index(best_hand))
    return best_hand_ix, winner_card_type


def eval_best_hand(hands):  # evaluate which hand is best
    """Evaluate the best hand."""
    scores = [(i, _calc_score(hand)) for i, hand in enumerate(hands)]
    winner = sorted(scores, key=lambda x: x[1], reverse=True)[0][0]
    return hands[winner], scores[winner][1][-1]


def _calc_score(hand):
    """Assign a calc_score to the hand so it can be compared with other hands"""
    rcounts = {CARD_RANKS_ORIGINAL.find(r): ''.join(hand).count(r) for r, _ in hand}.items()
    score, card_ranks = zip(*sorted((cnt, rank) for rank, cnt in rcounts)[::-1])

    potential_threeofakind = score[0] == 3
    potential_twopair = score == (2, 2, 1, 1, 1)
    potential_pair = score == (2, 1, 1, 1, 1, 1)

    if score[0:2] == (3, 2) or score[0:2] == (3, 3):  # fullhouse (three of a kind and pair, or two three of a kind)
        card_ranks = (card_ranks[0], card_ranks[1])
        score = (3, 2)
    elif score[0:4] == (2, 2, 2, 1):  # special case: convert three pair to two pair
        score = (2, 2, 1)  # as three pair are not worth more than two pair
        kicker = max(card_ranks[2], card_ranks[3])  # avoid for example 11,8,6,7
        card_ranks = (card_ranks[0], card_ranks[1], kicker)
    elif score[0] == 4:  # four of a kind
        score = (4,)
        sorted_card_ranks = sorted(card_ranks, reverse=True)  # avoid for example 11,8,9
        card_ranks = (sorted_card_ranks[0], sorted_card_ranks[1])
    elif len(score) >= 5:  # high card, flush, straight and straight flush
        # straight
        if 12 in card_ranks:  # adjust if 5 high straight
            card_ranks += (-1,)
        sorted_card_ranks = sorted(card_ranks, reverse=True)  # sort again as if pairs the first rank matches the pair
        for i in range(len(sorted_card_ranks) - 4):
            straight = sorted_card_ranks[i] - sorted_card_ranks[i + 4] == 4
            if straight:
                card_ranks = (
                    sorted_card_ranks[i], sorted_card_ranks[i + 1], sorted_card_ranks[i + 2], sorted_card_ranks[i + 3],
                    sorted_card_ranks[i + 4])
                break

        # flush
        suits = [s for _, s in hand]
        flush = max(suits.count(s) for s in suits) >= 5
        if flush:
            for flush_suit in SUITS_ORIGINAL:  # get the suit of the flush
                if suits.count(flush_suit) >= 5:
                    break

            flush_hand = [k for k in hand if flush_suit in k]  # pylint: disable=undefined-loop-variable
            rcounts_flush = {CARD_RANKS_ORIGINAL.find(r): ''.join(flush_hand).count(r) for r, _ in flush_hand}.items()
            score, card_ranks = zip(*sorted((cnt, rank) for rank, cnt in rcounts_flush)[::-1])
            card_ranks = tuple(
                sorted(card_ranks, reverse=True))  # ignore original sorting where pairs had influence

            # check for straight in flush
            if 12 in card_ranks and -1 not in card_ranks:  # adjust if 5 high straight
                card_ranks += (-1,)
            for i in range(len(card_ranks) - 4):
                straight = card_ranks[i] - card_ranks[i + 4] == 4
                if straight:
                    break

        # no pair, straight, flush, or straight flush
        score = ([(1,), (3, 1, 2)], [(3, 1, 3), (5,)])[flush][straight]

    if score == (1,) and potential_threeofakind:
        score = (3, 1)
    elif score == (1,) and potential_twopair:
        score = (2, 2, 1)
    elif score == (1,) and potential_pair:
        score = (2, 1, 1)

    if score[0] == 5:
        hand_type = "StraightFlush"  # crdRanks=crdRanks[:5] # five card rule makes no difference {:5] would be incorrect
    elif score[0] == 4:
        hand_type = "FoufOfAKind"  # crdRanks=crdRanks[:2] # already implemented above
    elif score[0:2] == (3, 2):
        hand_type = "FullHouse"  # crdRanks=crdRanks[:2] # already implmeneted above
    elif score[0:3] == (3, 1, 3):
        hand_type = "Flush"
        card_ranks = card_ranks[:5]
    elif score[0:3] == (3, 1, 2):
        hand_type = "Straight"
        card_ranks = card_ranks[:5]
    elif score[0:2] == (3, 1):
        hand_type = "ThreeOfAKind"
        card_ranks = card_ranks[:3]
    elif score[0:2] == (2, 2):
        hand_type = "TwoPair"
        card_ranks = card_ranks[:3]
    elif score[0] == 2:
        hand_type = "Pair"
        card_ranks = card_ranks[:4]
    elif score[0] == 1:
        hand_type = "HighCard"
        card_ranks = card_ranks[:5]
    else:
        raise Exception('Card Type error!')  # pylint: disable=broad-exception-raised

    return score, card_ranks, hand_type
