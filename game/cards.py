import time
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
        return [self.colour.value, self.count, self.fill.value, self.shape.value]

    def __repr__(self):
        return f"Card({self.colour.name}, {self.count}, {self.fill.name}, {self.shape.name})"


def find_matches(cards):
    print("Finding Matches...")
    start = time.perf_counter()

    card_map = {}
    card_map_names = {}
    card_vecs = []
    seen = set()

    for card in cards.items():
        card_map[card[0]] = tuple(card[1].to_vec())
        card_map_names[tuple(card[1].to_vec())] = card[0]
        card_vecs.append(tuple(card[1].to_vec()))

    n = len(card_vecs)
    for i in range(n):
        for j in range(i + 1, n):
            a = card_vecs[i]
            b = card_vecs[j]
            c = tuple(((-a[k] - b[k]) % 3) for k in range(4))

            if c in card_map_names:
                card_names = sorted(
                    [card_map_names[a], card_map_names[b], card_map_names[c]]
                )
                new_set = tuple(card_names)
                if new_set not in seen:
                    seen.add(new_set)

    elapsed = time.perf_counter() - start
    print(f"Found {len(seen)} matches in {elapsed:.2f} seconds.")
    return seen
