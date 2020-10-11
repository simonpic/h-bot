from enum import Enum
from random import shuffle


def load_cards():
    cards = []
    for suit in Suit:
        for card_number in range(1, 14):
            cards.append(Card(card_number, suit))
    shuffle(cards)
    return cards


class Suit(Enum):
    SPADE = 'pique'
    DIAMOND = 'carreau'
    CLUB = 'trefle'
    HEART = 'coeur'


class Card:
    def __init__(self, number, suit):
        self.number = number
        self.suit = suit

    def isRed(self):
        return self.suit == Suit.DIAMOND or self.suit == Suit.HEART

    def isBlack(self):
        return self.suit == Suit.SPADE or self.suit == Suit.CLUB
