from enum import Enum

class Colour(Enum):
    RED = 0
    GREEN = 1
    PURPLE = 2

class Fill(Enum):
    OPEN = 0
    STRIPED = 1
    SOLID = 2

class Shape(Enum):
    DIAMOND = 0
    OVAL = 1
    SQUIGGLE = 2

class Card:
    def __init__(self, colour, count, fill, shape):
        self.colour = colour
        self.count = count
        self.fill = fill
        self.shape = shape

    def to_vec(self):
        return [self.colour, self.count, self.fill, self.shape]
    
    def __repr__(self):
        return f"Card({self.colour.name}, {self.count}, {self.fill.name}, {self.shape.name})"


def find_matches(cards):
    for card in cards.values():
        print(card)
    pass