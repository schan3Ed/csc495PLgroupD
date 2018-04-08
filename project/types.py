import * from base
class Card(o):
    __init__(self, name, suit, rank, func=None):
        self.func = func or lambda: None
        self.name = str(name)
        self.suit = str(suit)
        self.rank = str(rank)