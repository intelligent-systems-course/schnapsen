from unittest import TestCase

from schnapsen.deck import (
    Suit,
    Rank,
    Card,
    OrderedCardCollection,
)


class CardTest(TestCase):

    def test_cards(self) -> None:
        # unicodes for the cards
        EXPECTED_BYTES = [
            ("ACE_HEARTS", [240, 159, 130, 177]),
            ("TWO_HEARTS", [240, 159, 130, 178]),
            ("THREE_HEARTS", [240, 159, 130, 179]),
            ("FOUR_HEARTS", [240, 159, 130, 180]),
            ("FIVE_HEARTS", [240, 159, 130, 181]),
            ("SIX_HEARTS", [240, 159, 130, 182]),
            ("SEVEN_HEARTS", [240, 159, 130, 183]),
            ("EIGHT_HEARTS", [240, 159, 130, 184]),
            ("NINE_HEARTS", [240, 159, 130, 185]),
            ("TEN_HEARTS", [240, 159, 130, 186]),
            ("JACK_HEARTS", [240, 159, 130, 187]),
            ("QUEEN_HEARTS", [240, 159, 130, 189]),
            ("KING_HEARTS", [240, 159, 130, 190]),
            ("ACE_CLUBS", [240, 159, 131, 145]),
            ("TWO_CLUBS", [240, 159, 131, 146]),
            ("THREE_CLUBS", [240, 159, 131, 147]),
            ("FOUR_CLUBS", [240, 159, 131, 148]),
            ("FIVE_CLUBS", [240, 159, 131, 149]),
            ("SIX_CLUBS", [240, 159, 131, 150]),
            ("SEVEN_CLUBS", [240, 159, 131, 151]),
            ("EIGHT_CLUBS", [240, 159, 131, 152]),
            ("NINE_CLUBS", [240, 159, 131, 153]),
            ("TEN_CLUBS", [240, 159, 131, 154]),
            ("JACK_CLUBS", [240, 159, 131, 155]),
            ("QUEEN_CLUBS", [240, 159, 131, 157]),
            ("KING_CLUBS", [240, 159, 131, 158]),
            ("ACE_SPADES", [240, 159, 130, 161]),
            ("TWO_SPADES", [240, 159, 130, 162]),
            ("THREE_SPADES", [240, 159, 130, 163]),
            ("FOUR_SPADES", [240, 159, 130, 164]),
            ("FIVE_SPADES", [240, 159, 130, 165]),
            ("SIX_SPADES", [240, 159, 130, 166]),
            ("SEVEN_SPADES", [240, 159, 130, 167]),
            ("EIGHT_SPADES", [240, 159, 130, 168]),
            ("NINE_SPADES", [240, 159, 130, 169]),
            ("TEN_SPADES", [240, 159, 130, 170]),
            ("JACK_SPADES", [240, 159, 130, 171]),
            ("QUEEN_SPADES", [240, 159, 130, 173]),
            ("KING_SPADES", [240, 159, 130, 174]),
            ("ACE_DIAMONDS", [240, 159, 131, 129]),
            ("TWO_DIAMONDS", [240, 159, 131, 130]),
            ("THREE_DIAMONDS", [240, 159, 131, 131]),
            ("FOUR_DIAMONDS", [240, 159, 131, 132]),
            ("FIVE_DIAMONDS", [240, 159, 131, 133]),
            ("SIX_DIAMONDS", [240, 159, 131, 134]),
            ("SEVEN_DIAMONDS", [240, 159, 131, 135]),
            ("EIGHT_DIAMONDS", [240, 159, 131, 136]),
            ("NINE_DIAMONDS", [240, 159, 131, 137]),
            ("TEN_DIAMONDS", [240, 159, 131, 138]),
            ("JACK_DIAMONDS", [240, 159, 131, 139]),
            ("QUEEN_DIAMONDS", [240, 159, 131, 141]),
            ("KING_DIAMONDS", [240, 159, 131, 142]),
        ]

        for card_name, expected_encoding in EXPECTED_BYTES:
            card = getattr(Card, card_name)
            self.assertEqual(card.rank, getattr(Rank, card_name.split("_")[0]))
            self.assertEqual(card.suit, getattr(Suit, card_name.split("_")[1]))
            self.assertEqual(list(card.character.encode()), expected_encoding)


class CollectionTest(TestCase):

    def test_Empty(self) -> None:
        collection = OrderedCardCollection()
        self.assertTrue(collection.is_empty())
        self.assertEqual(len(collection), 0)

    def test__one_card(self) -> None:
        collection = OrderedCardCollection([Card.ACE_CLUBS])
        self.assertFalse(collection.is_empty())
        self.assertEqual(len(collection), 1)

    card_lists = [
        [Card.ACE_CLUBS, Card.FOUR_DIAMONDS, Card.QUEEN_HEARTS],
        [Card.FOUR_DIAMONDS, Card.QUEEN_HEARTS],
        [Card.FOUR_DIAMONDS],
        # Testing with duplicates
        [Card.ACE_CLUBS, Card.ACE_CLUBS, Card.QUEEN_HEARTS],
    ]

    def test_multiple_cards(self) -> None:
        for list_with_cards in CollectionTest.card_lists:
            collection = OrderedCardCollection(list_with_cards)

            self.assertEqual(len(collection), len(list_with_cards))

            for idx, card in enumerate(collection):
                self.assertEqual(card, list_with_cards[idx])

            for card in list_with_cards:
                self.assertIn(card, collection)

    def test_filer_suit(self) -> None:
        for collection in [OrderedCardCollection(card_list) for card_list in CollectionTest.card_lists]:
            for suit in Suit:
                filtered = collection.filter_suit(suit)
                for card in filtered:
                    self.assertEqual(card.suit, suit)
                    self.assertIn(card, collection)
                removed = [removed_card for removed_card in collection if removed_card not in filtered]
                for card in removed:
                    self.assertNotEqual(card.suit, suit)
                    self.assertIn(card, collection)

    def test_filer_rank(self) -> None:
        for collection in [OrderedCardCollection(card_list) for card_list in CollectionTest.card_lists]:
            for rank in Rank:
                filtered = collection.filter_rank(rank)
                for card in filtered:
                    self.assertEqual(card.rank, rank)
                    self.assertIn(card, collection)
                removed = [removed_card for removed_card in collection if removed_card not in filtered]
                for card in removed:
                    self.assertNotEqual(card.rank, rank)
                    self.assertIn(card, collection)
