from unittest import TestCase

from schnapsen.deck import (
    Suit,
    Rank,
    Card,
    _CardCache,
    CardCollection,
    OrderedCardCollection,
)


class CardTest(TestCase):
    def test_ranks(self) -> None:
        self.assertEqual(Rank(1), Rank.ACE)
        self.assertEqual(Rank(2), Rank.TWO)
        self.assertEqual(Rank(3), Rank.THREE)
        self.assertEqual(Rank(4), Rank.FOUR)
        self.assertEqual(Rank(5), Rank.FIVE)
        self.assertEqual(Rank(6), Rank.SIX)
        self.assertEqual(Rank(7), Rank.SEVEN)
        self.assertEqual(Rank(8), Rank.EIGHT)
        self.assertEqual(Rank(9), Rank.NINE)
        self.assertEqual(Rank(10), Rank.TEN)
        self.assertEqual(Rank(11), Rank.JACK)
        self.assertEqual(Rank(12), Rank.QUEEN)
        self.assertEqual(Rank(13), Rank.KING)

    def test_cards(self) -> None:
        # unicodes for the cards
        EXPECTED_BYTES = [
            [240, 159, 130, 177],
            [240, 159, 130, 178],
            [240, 159, 130, 179],
            [240, 159, 130, 180],
            [240, 159, 130, 181],
            [240, 159, 130, 182],
            [240, 159, 130, 183],
            [240, 159, 130, 184],
            [240, 159, 130, 185],
            [240, 159, 130, 186],
            [240, 159, 130, 187],
            [240, 159, 130, 189],
            [240, 159, 130, 190],
            [240, 159, 131, 145],
            [240, 159, 131, 146],
            [240, 159, 131, 147],
            [240, 159, 131, 148],
            [240, 159, 131, 149],
            [240, 159, 131, 150],
            [240, 159, 131, 151],
            [240, 159, 131, 152],
            [240, 159, 131, 153],
            [240, 159, 131, 154],
            [240, 159, 131, 155],
            [240, 159, 131, 157],
            [240, 159, 131, 158],
            [240, 159, 130, 161],
            [240, 159, 130, 162],
            [240, 159, 130, 163],
            [240, 159, 130, 164],
            [240, 159, 130, 165],
            [240, 159, 130, 166],
            [240, 159, 130, 167],
            [240, 159, 130, 168],
            [240, 159, 130, 169],
            [240, 159, 130, 170],
            [240, 159, 130, 171],
            [240, 159, 130, 173],
            [240, 159, 130, 174],
            [240, 159, 131, 129],
            [240, 159, 131, 130],
            [240, 159, 131, 131],
            [240, 159, 131, 132],
            [240, 159, 131, 133],
            [240, 159, 131, 134],
            [240, 159, 131, 135],
            [240, 159, 131, 136],
            [240, 159, 131, 137],
            [240, 159, 131, 138],
            [240, 159, 131, 139],
            [240, 159, 131, 141],
            [240, 159, 131, 142],
        ]

        for idx, member_name in enumerate(Card._member_names_):
            foo = getattr(Card, member_name)
            self.assertEqual(foo.rank, getattr(Rank, member_name.split("_")[0]))
            self.assertEqual(foo.suit, getattr(Suit, member_name.split("_")[1]))
            self.assertEqual(list(foo.character.encode()), EXPECTED_BYTES[idx])

        for suit in range(1, 5):
            for rank in range(1, 14):
                card = Card.get_card(Rank(rank), Suit(suit))
                self.assertEqual(card.suit, Suit(suit))
                self.assertEqual(card.rank, Rank(rank))

    def test_OrderedCardCollection(self) -> None:
        foo = OrderedCardCollection()
        self.assertTrue(foo.is_empty())
        self.assertEqual(len(foo), 0)

        foo = OrderedCardCollection([Card.ACE_CLUBS])
        self.assertFalse(foo.is_empty())
        self.assertEqual(len(foo), 1)

        cards = [Card.ACE_CLUBS, Card.FOUR_DIAMONDS, Card.QUEEN_HEARTS]

        foo = OrderedCardCollection(cards)

        for idx, card in enumerate(foo):
            self.assertEqual(card, cards[idx])
            self.assertTrue(foo.__contains__(card))

        self.assertEqual(foo.filter_suit(Suit.CLUBS)[0], Card.ACE_CLUBS)
        self.assertEqual(foo.filter_suit(Suit.DIAMONDS)[0], Card.FOUR_DIAMONDS)
        self.assertEqual(foo.filter_suit(Suit.HEARTS)[0], Card.QUEEN_HEARTS)

        self.assertEqual(foo.filter_rank(Rank.ACE)[0], Card.ACE_CLUBS)
        self.assertEqual(foo.filter_rank(Rank.FOUR)[0], Card.FOUR_DIAMONDS)
        self.assertEqual(foo.filter_rank(Rank.QUEEN)[0], Card.QUEEN_HEARTS)
