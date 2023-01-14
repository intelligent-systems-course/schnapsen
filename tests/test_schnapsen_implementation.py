from unittest import TestCase

from schnapsen.deck import OrderedCardCollection, Card, Rank, Suit
from schnapsen.game import SchnapsenDeckGenerator, SchnapsenHandGenerator
from random import Random


class DeckGenerationTest(TestCase):
    def test_scnapsen_deck_generation(self) -> None:
        deck: OrderedCardCollection = SchnapsenDeckGenerator().get_initial_deck()
        self.assertEqual(len(deck), 20, "Not the right number of cards")
        self.assertEqual(len(deck), len(set(deck.get_cards())), "Duplicates found in the cards")
        cards = set(deck.get_cards())
        for suit in Suit:
            for rank in [Rank.TEN, Rank.JACK, Rank.QUEEN, Rank.KING, Rank.ACE]:
                assert Card.get_card(rank, suit) in cards


class DealingTest (TestCase):
    def test_dealing(self) -> None:
        deck: OrderedCardCollection = SchnapsenDeckGenerator().get_initial_deck()
        shuffled_deck = SchnapsenDeckGenerator().shuffle_deck(deck, Random())
        cards = list(shuffled_deck.get_cards())

        hand1, hand2, rest = SchnapsenHandGenerator.generateHands(shuffled_deck)
        self.assertEqual(len(hand1), 5, "Hand 1 must contain 5 cards")
        self.assertEqual(len(hand2), 5, "Hand 2 must contain 5 cards")
        self.assertEqual(len(rest), 10, "There must be 10 cards left after dealing")
        for i in [0, 2, 4, 6, 8]:
            assert cards[i] in hand1
            assert cards[i + 1] in hand2
            assert cards[i] not in rest
            assert cards[i + 1] not in rest
        for i in range(10, 20):
            assert cards[i] in rest
            assert cards[i] not in hand1
            assert cards[i] not in hand2
