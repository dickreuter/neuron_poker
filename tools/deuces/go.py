from deuces import Card, Evaluator, Deck

# create a card
card = Card.new('Qh')

# create a board and hole cards
board = [
    Card.new('2h'),
    Card.new('2s'),
    Card.new('Jc')
]
hand = [
    Card.new('Qs'),
    Card.new('Th')
]

# pretty print cards to console
Card.print_pretty_cards(board + hand)

# create an evaluator
evaluator = Evaluator()

# and rank your hand
rank = evaluator.evaluate(board, hand)
print "Rank for your hand is: %d" % rank

# or for random cards or games, create a deck
print "Dealing a new hand..."
deck = Deck()
board = deck.draw(5)
player1_hand = deck.draw(2)
player2_hand = deck.draw(2)

print "The board:"
Card.print_pretty_cards(board)

print "Player 1's cards:"
Card.print_pretty_cards(player1_hand)

print "Player 2's cards:"
Card.print_pretty_cards(player2_hand)

p1_score = evaluator.evaluate(board, player1_hand)
p2_score = evaluator.evaluate(board, player2_hand)

# bin the scores into classes
p1_class = evaluator.get_rank_class(p1_score)
p2_class = evaluator.get_rank_class(p2_score)

# or get a human-friendly string to describe the score
print "Player 1 hand rank = %d (%s)" % (p1_score, evaluator.class_to_string(p1_class))
print "Player 2 hand rank = %d (%s)" % (p2_score, evaluator.class_to_string(p2_class))

# or just a summary of the entire hand
hands = [player1_hand, player2_hand]
evaluator.hand_summary(board, hands)
