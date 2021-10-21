from unittest import TestCase

from schnapsen.deck import Card, Suit


class CardTest (TestCase):

    def test_ranks(self) -> None:
        assert Card.JACK_CLUBS.suit == Suit.CLUBS
        assert Card.JACK_SPADES.suit == Suit.SPADES
        assert Card.JACK_HEARTS.suit == Suit.HEARTS
        assert Card.JACK_DIAMONDS.suit == Suit.DIAMONDS
