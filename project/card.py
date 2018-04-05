import * from base
class Card(o):
    __init__(self, name, suit, rank, func=None):
        self.func = func or lambda: None
        self.name = ''
        self.suit=''
        self.rank=''