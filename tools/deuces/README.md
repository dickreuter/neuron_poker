Deuces
========

A pure Python poker hand evaluation library

    [ 2 ❤ ] , [ 2 ♠ ]
    
## Installation

```
$ pip install deuces
```

## Implementation notes

Deuces, originally written for the MIT Pokerbots Competition, is lightweight and fast. All lookups are done with bit arithmetic and dictionary lookups. That said, Deuces won't beat a C implemenation (~250k eval/s) but it is useful for situations where Python is required or where bots are allocated reasonable thinking time (human time scale).

Deuces handles 5, 6, and 7 card hand lookups. The 6 and 7 card lookups are done by combinatorially evaluating the 5 card choices, but later releases may have dedicated and faster algorithms for these. 

I also have lookup tables for 2 card rollouts, which is particularly handy in evaluating Texas Hold'em preflop pot equity, but they are forthcoming as well. 

See my blog for an explanation of how the library works and how the lookup table generation is done:
http://willdrevo.com/ (haven't posted yet)

## Usage

Deuces is easy to set up and use. 

```python
>>> from deuces import Card
>>> card = Card.new('Qh')
```

Card objects are represented as integers to keep Deuces performant and lightweight. 

Now let's create the board and an example Texas Hold'em hand:

```python
>>> board = [
>>>     Card.new('Ah'),
>>>     Card.new('Kd'),
>>>     Card.new('Jc')
>>> ]
>>> hand = [
>>>    Card.new('Qs'),
>>>    Card.new('Th')
>>> ]
```

Pretty print card integers to the terminal: 

    >>> Card.print_pretty_cards(board + hand)
      [ A ❤ ] , [ K ♦ ] , [ J ♣ ] , [ Q ♠ ] , [ T ❤ ] 

If you have [`termacolor`](http://pypi.python.org/pypi/termcolor) installed, they will be colored as well. 

Otherwise move straight to evaluating your hand strength:
```python
>>> from deuces import Evaluator
>>> evaluator = Evaluator()
>>> print evaluator.evaluate(board, hand)
1600
```

Hand strength is valued on a scale of 1 to 7462, where 1 is a Royal Flush and 7462 is unsuited 7-5-4-3-2, as there are only 7642 distinctly ranked hands in poker. Once again, refer to my blog post for a more mathematically complete explanation of why this is so. 

If you want to deal out cards randomly from a deck, you can also do that with Deuces:
```python
>>> from deuces import Deck
>>> deck = Deck()
>>> board = deck.draw(5)
>>> player1_hand = deck.draw(2)
>>> player2_hand = deck.draw(2)
```
and print them:

    >>> Card.print_pretty_cards(board)
      [ 4 ♣ ] , [ A ♠ ] , [ 5 ♦ ] , [ K ♣ ] , [ 2 ♠ ]
    >>> Card.print_pretty_cards(player1_hand)
      [ 6 ♣ ] , [ 7 ❤ ] 
    >>> Card.print_pretty_cards(player2_hand)
      [ A ♣ ] , [ 3 ❤ ] 

Let's evaluate both hands strength, and then bin them into classes, one for each hand type (High Card, Pair, etc)
```python
>>> p1_score = evaluator.evaluate(board, player1_hand)
>>> p2_score = evaluator.evaluate(board, player2_hand)
>>> p1_class = evaluator.get_rank_class(p1_score)
>>> p2_class = evaluator.get_rank_class(p2_score)
```
or get a human-friendly string to describe the score,

    >>> print "Player 1 hand rank = %d (%s)\n" % (p1_score, evaluator.class_to_string(p1_class))
    Player 1 hand rank = 6330 (High Card)

    >>> print "Player 2 hand rank = %d (%s)\n" % (p2_score, evaluator.class_to_string(p2_class))
    Player 2 hand rank = 1609 (Straight)

or, coolest of all, get a blow-by-blow analysis of the stages of the game with relation to hand strength:

    >>> hands = [player1_hand, player2_hand]
    >>> evaluator.hand_summary(board, hands)

    ========== FLOP ==========
    Player 1 hand = High Card, percentage rank among all hands = 0.893192
    Player 2 hand = Pair, percentage rank among all hands = 0.474672
    Player 2 hand is currently winning.

    ========== TURN ==========
    Player 1 hand = High Card, percentage rank among all hands = 0.848298
    Player 2 hand = Pair, percentage rank among all hands = 0.452292
    Player 2 hand is currently winning.

    ========== RIVER ==========
    Player 1 hand = High Card, percentage rank among all hands = 0.848298
    Player 2 hand = Straight, percentage rank among all hands = 0.215626

    ========== HAND OVER ==========
    Player 2 is the winner with a Straight

And that's Deuces, yo. 

## Performance

Just how fast is Deuces? Check out `performance` folder for a couple of tests comparing Deuces to other pure Python hand evaluators.

Here are the results evaluating 10,000 random 5, 6, and 7 card boards:

    5 card evaluation:
    [*] Pokerhand-eval: Evaluations per second = 83.577580
    [*] Deuces: Evaluations per second = 235722.458889
    [*] SpecialK: Evaluations per second = 376833.177604

    6 card evaluation:
    [*] Pokerhand-eval: Evaluations per second = 55.519042
    [*] Deuces: Evaluations per second = 45677.395466
    [*] SpecialK: N/A

    7 card evaluation:
    [*] Pokerhand-eval: Evaluations per second = 51.529784
    [*] Deuces: Evaluations per second = 15220.969303
    [*] SpecialK: Evaluations per second = 142698.833384

Compared to [`pokerhand-eval`](https://github.com/aliang/pokerhand-eval), Deuces is 2400x faster on 5 card evaluation, and drops to 300x faster on 7 card evaluation.

However, [`SpecialKEval`](https://github.com/SpecialK/SpecialKEval/) reigns supreme, with an impressive nearly 400k evals / sec (a factor of ~1.7 improvement over Deuces) for 5 cards, and an impressive 140k /sec on 7 cards (factor of 10). 

For poker hand evaluation in Python, if you desire a cleaner user interface and more readable and adaptable code, I recommend Deuces, because if you *really* need speed, you should be using C anyway. The extra 10x on 7 cards with SpecialK won't get you much more in terms of Monte Carlo simulations, and SpecialK's 5 card evals are within a factor of 2 of Deuces's evals/s. 

For C/C++, I'd recommand [`pokerstove`](https://github.com/andrewprock/pokerstove), as its hyperoptimized C++ Boost routines can do 10+ million evals/s. 

## License

Copyright (c) 2013 Will Drevo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
