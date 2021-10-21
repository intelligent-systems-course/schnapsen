from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from random import Random
from typing import Callable, Iterable, List, Mapping, Optional, Tuple, Union, cast
from .deck import CardCollection, OrderedCardCollection, Card, Rank, Suit


class Move(ABC):

    def is_marriage(self) -> bool:
        return False

    def is_trump_exchange(self) -> bool:
        return False

    @abstractmethod
    def cards(self) -> Iterable[Card]:
        raise NotImplementedError()


@dataclass(frozen=True)
class Trump_Exchange(Move):
    jack: Card

    def _post_init__(self) -> None:
        assert self.jack.rank is Rank.JACK
        self.suit = self.jack.suit

    def is_trump_exchange(self) -> bool:
        return True

    def cards(self) -> Iterable[Card]:
        return [self.jack]


@dataclass(frozen=True)
class RegularMove(Move):
    card: Card

    def cards(self) -> Iterable[Card]:
        return [self.card]

    @staticmethod
    def from_cards(cards: Iterable[Card]) -> Iterable[Move]:
        return [RegularMove(card) for card in cards]


@dataclass(frozen=True)
class Marriage(Move):
    queen_card: Card
    king_card: Card

    def __post_init__(self) -> None:
        assert self.queen_card.rank is Rank.QUEEN
        assert self.king_card.rank is Rank.KING
        assert self.queen_card.suit == self.king_card.suit
        self.suit = self.queen_card.suit

    def is_marriage(self) -> bool:
        return True

    def as_regular_move(self) -> RegularMove:
        # TODO this limits you to only have the queen to play after a marriage, while in general you would ahve a choice
        return RegularMove(self.queen_card)

    def cards(self) -> Iterable[Card]:
        return [self.queen_card, self.king_card]


class Hand(CardCollection):
    def __init__(self, cards: Iterable[Card], max_size: int = 5) -> None:
        self.max_size = max_size
        cards = list(cards)
        assert len(cards) <= max_size, f"The number of cards {len(cards)} is larger than the maximum number fo allowed cards {max_size}"
        self.cards = cards

    def remove(self, card: Card) -> None:
        try:
            self.cards.remove(card)
        except ValueError:
            raise Exception(f"Trying to play a card fromt he hand which is not in the hand. Hand is {self.cards}, trying to play {card}")

    def add(self, card: Card) -> None:
        assert len(self.cards) < self.max_size, "Adding one more card to the hand will cause a hand with too many cards"
        self.cards.append(card)

    def has_cards(self, cards: Iterable[Card]) -> bool:
        return all([card in self.cards for card in cards])

    def copy(self) -> 'Hand':
        return Hand(list(self.cards))

    def is_empty(self) -> bool:
        return len(self.cards) == 0

    def get_cards(self) -> Iterable[Card]:
        return list(self.cards)

# Do we need this???
# class HandWithoutDuplicates(Hand):
#     def __init__(self, cards: Iterable[Card], max_size: int = 5) -> None:
#         assert len(set(cards)) == len(list(cards)), "A HandWithoutDuplicates was initialized with a set of cards containing duplicates"
#         super().__init__(cards, max_size=max_size)

#     def add(self, card: Card) -> None:
#         assert card not in self.cards, "Adding a card to a hand, but there is already such a a card"
#         super().add(card)

#     def copy(self) -> 'HandWithoutDuplicates':
#         return HandWithoutDuplicates(self.cards, self.max_size)


class Talon(OrderedCardCollection):

    def __init__(self, cards: Iterable[Card]) -> None:
        """The cards of the Talon. The last card is the bottommost card. The first one is the top card (which will be taken is a card is drawn)
            The Trump card is at the bottom of the Talon.
        """
        super().__init__(cards)

    def copy(self) -> 'Talon':
        return Talon(self._cards)

    def trump_exchange(self, new_trump: Card) -> Card:
        """ perfom a trump-jack exchange. The card to be put as the trump card must be a Jack of the same suit.
        As a result, this Talon changed: the old trump is removed and the new_trump is at the bottom of the Talon"""
        assert new_trump.rank is Rank.JACK
        assert len(self._cards) >= 2
        assert new_trump.suit is self._cards[0].suit
        old_trump = self._cards.pop(len(self._cards) - 1)
        self._cards.append(new_trump)
        return old_trump

    def draw_cards(self, amount: int) -> Iterable[Card]:
        """Draw a card from this Talon. This does not change the talon, btu rather returns a talon with the change applied and the card drawn"""
        assert len(self._cards) >= amount, f"There are only {len(self._cards)} on the Talon, but {amount} cards are requested"
        draw = self._cards[:amount]
        self._cards = self._cards[amount:]
        return draw


@dataclass(frozen=True)
class PartialTrick:
    trump_exchange: Optional[Trump_Exchange]
    first_move: Union[RegularMove, Marriage]


@dataclass(frozen=True)
class Trick(PartialTrick):
    second_move: RegularMove


@dataclass
class Score:
    direct_points: int = 0
    pending_points: int = 0

    def __add__(self, other: 'Score') -> 'Score':
        total_direct_points = self.direct_points + other.direct_points
        total_pending_points = self.pending_points + other.pending_points
        return Score(total_direct_points, total_pending_points)

    def copy(self) -> 'Score':
        return Score(direct_points=self.direct_points, pending_points=self.pending_points)


class GamePhase(Enum):
    ONE = 1
    TWO = 2


@dataclass
class Bot:
    """A bot with its implementation and current state in a game"""

    implementation: Callable[['PlayerGameState'], Move]
    hand: Hand
    score: Score
    won_cards: OrderedCardCollection = OrderedCardCollection()

    def get_move(self, state: 'PlayerGameState') -> Move:
        move = self.implementation(state)
        assert self.hand.has_cards(move.cards()), \
            f"Tried to play a move for which the player does not have the cards. Played {move.cards}, but has {self.hand}"
        return move

    def copy(self) -> 'Bot':
        new_bot = Bot(
            implementation=self.implementation,
            hand=self.hand.copy(),
            score=self.score.copy(),
            won_cards=OrderedCardCollection(self.won_cards.get_cards()))
        return new_bot


@dataclass
class GameState:
    leader: Bot
    follower: Bot
    trump_suit: Suit
    talon: Talon
    previous: 'GameState'
    # TODO it might be that we have to include the ongoing trick here, such that a bot can implement things like rdeep easily
    # ongoing_trick: PartialTrick

    def copy_for_next(self) -> 'GameState':
        """Make a copy of the gamestate"""

        leader = self.leader.copy()
        follower = self.follower.copy()

        new_state = GameState(leader=leader, follower=follower, trump_suit=self.trump_suit, talon=self.talon.copy(), previous=self)
        return new_state


class PlayerGameState(ABC):
    def __init__(self, state: 'GameState', ) -> None:
        self.__game_state = state

    @abstractmethod
    def valid_moves(self) -> Iterable[Move]:
        pass

    def get_opponent_card(self) -> Optional[Move]:
        raise NotImplementedError()

    def get_game_history(self):
        pass

    @abstractmethod
    def get_hand(self) -> Hand:
        pass

    @abstractmethod
    def get_my_score() -> Score:
        raise NotImplementedError()

    @abstractmethod
    def get_opponent_score(self) -> Score:
        raise NotImplementedError()

    def get_trump_suit(self) -> Suit:
        return self.__game_state.trump_suit

    def get_talon_size(self) -> int:
        return self.__game_state.talon.size()

    def get_phase(self) -> GamePhase:
        return self.__game_state.game_phase

    def make_assumption() -> 'GameState':
        """
                Takes the current imperfect information state and makes a
                random guess as to the states of the unknown cards.

        This also takes into account cards seen earlier during marriages played by the opponent, as well as potential trump jack exchanges

                :return: A perfect information state object.
                """
        raise NotImplementedError()


class LeaderGameState(PlayerGameState):
    # player_hand: Hand
    # opponent_hand: Optional[Hand]
    # on_table: PartialTrick
    # trump: Card
    # talon: InvisibleTalon
    #    def __init__(self, state: 'GameState', ) -> None:
    def __init__(self, state: 'GameState') -> None:
        super().__init__(state)

    def valid_moves(self) -> Iterable[Move]:
        return self.__game_state.get_legal_leader_moves()

    # TODO check the following implementation
    def get_hand(self) -> Hand:
        return self.__game_state.leader.hand.copy()


class FollowerGameState(PlayerGameState):
    def __init__(self, state: 'GameState', partial_trick: PartialTrick) -> None:
        super().__init__(state)
        self.partial_trick = partial_trick

    def valid_moves(self) -> Iterable[Move]:
        return self.__game_state.get_legal_follower_moves(self.partial_trick)

    def get_hand(self) -> Hand:
        return self.__game_state.follower.hand.copy()


class DeckGenerator(ABC):
    @abstractmethod
    def get_initial_deck(self) -> OrderedCardCollection:
        pass

    @classmethod
    def shuffle_deck(self, deck: OrderedCardCollection, rng: Random) -> OrderedCardCollection:
        the_cards = deck.get_cards()
        rng.shuffle(the_cards)
        return OrderedCardCollection(the_cards)


class SchnapsenDeckGenerator(DeckGenerator):

    @classmethod
    def get_initial_deck(self) -> OrderedCardCollection:
        deck = OrderedCardCollection()
        for suit in Suit:
            for rank in [Rank.JACK, Rank.QUEEN, Rank.KING, Rank.TEN, Rank.ACE]:
                deck._cards.append(Card.get_card(rank, suit))
        return deck


class HandGenerator(ABC):
    @abstractmethod
    def generateHands(self, cards: OrderedCardCollection) -> Tuple[OrderedCardCollection, Hand, Hand]:
        pass


class SchnapsenHandGenerator(HandGenerator):
    @classmethod
    def generateHands(self, cards: OrderedCardCollection) -> Tuple[OrderedCardCollection, Hand, Hand]:
        the_cards = list(cards.get_cards())
        hand1 = [the_cards[i] for i in range(0, 10, 2)]
        hand2 = [the_cards[i] for i in range(1, 11, 2)]
        rest = the_cards[10:]
        return (hand1, hand2, rest)


class TrickPlayer(ABC):
    @abstractmethod
    def play_trick(self, game_state: GameState) -> GameState:
        pass


class SchnapsenTrickPlayer(TrickPlayer):

    # TODO this code needs an overhaul. It is just copied here from the old Gamestate class.
    def game_phase(self) -> GamePhase:
        if self.talon.is_empty():
            return GamePhase.TWO
        else:
            return GamePhase.ONE

    def play_trump_exchange(self, trump_exhange: Trump_Exchange) -> None:
        assert trump_exhange.suit is self.trump_suit, \
            f"A trump exchange can only be done with a Jack of the same suit as the current trump. Got a {trump_exhange.jack} while the  Trump card is a {self.trump_suit}"
        # apply the changes in the gamestate
        self.leader.hand.remove(trump_exhange.jack)
        old_trump = self.talon.trump_exchange(trump_exhange.jack)
        self.leader.hand.add(old_trump)

    def _play_marriage(self, marriage_move: Marriage) -> None:
        if marriage_move.suit is self.trump_suit:
            self.leader.score += self.scorer.royal_marriage()
        else:
            self.leader.score += self.scorer.marriage()

    def play_trick(self, game_state: 'GameState') -> 'GameState':
        mutable_game_state = self.copy_for_next()
        # calling a static method to ensure no accidental modiciation of self
        GameState._play_trick(mutable_game_state)
        return mutable_game_state

    # TODO : it might be that this has to be split in two: first the leader, then the follower.

    @staticmethod
    def get_leader_move(game_state: 'GameState') -> PartialTrick:
        assert not game_state.game_ended()
        leader_game_state = LeaderGameState(game_state)
        # ask first players move
        leader_move = game_state.leader.get_move(leader_game_state)
        if leader_move not in game_state.get_legal_leader_moves():
            raise Exception("Leader played an illegal move")
        if leader_move.is_trump_exchange():
            trump_exchange: Trump_Exchange = cast(Trump_Exchange, leader_move)
            game_state.play_trump_exchange(trump_exchange)
            # ask first players move again, as the exchange is not a real move
            leader_move = game_state.leader.get_move(leader_game_state)
            if leader_move not in game_state.get_legal_leader_moves():
                raise Exception("Leader played an illegal move")
        else:
            trump_exchange = None
        if leader_move.is_marriage():
            # record score, keep in mind the royal marriage
            marriage_move: Marriage = cast(Marriage, leader_move)
            game_state._play_marriage(marriage_move=marriage_move)
            leader_move = marriage_move.as_regular_move()
        # normal play continues, follower's turn

        partial_trick = PartialTrick(trump_exchange=trump_exchange, first_move=leader_move)
        return partial_trick

    @staticmethod
    def get_follower_move(game_state: 'GameState', partial_trick: PartialTrick) -> Move:
        follower_game_state = FollowerGameState(game_state, partial_trick)
        follower_move = game_state.follower.get_move(follower_game_state)
        if follower_move not in game_state.get_legal_follower_moves(partial_trick):
            raise Exception("Follower played an illegal move")
        return follower_move

    @staticmethod
    def _play_trick(game_state: 'GameState') -> None:
        partial_trick = SchnapsenTrickPlayer.get_leader_move(game_state)
        follower_move = SchnapsenTrickPlayer.get_follower_move(game_state, partial_trick)

        if partial_trick.first_move.is_marriage():
            regular_leader_move: RegularMove = cast(Marriage, partial_trick.first_move).as_regular_move()
        else:
            regular_leader_move = partial_trick.first_move
        regular_follower_move = cast(RegularMove, follower_move)
        trick = Trick(regular_leader_move, regular_follower_move)
        game_state.leader, game_state.follower = game_state.scorer.score(trick, game_state.leader, game_state.follower, game_state.trump_suit)

        # important: the winner takes the first card of the talon, the loser the second one.
        # this also ensures that the loser of the last trick of the first phase gets the face up trump
        if not game_state.talon.is_empty:
            drawn = iter(game_state.talon.draw_cards(2))
            game_state.leader.hand.add(next(drawn))
            game_state.follower.hand.add(next(drawn))

    def game_ended(self) -> bool:
        return self.talon.is_empty() and self.bot1.hand.is_empty() and self.bot2.hand.is_empty()


class MoveRequester:
    """An the logic of requesting a move from a bot.
    This logic also determines what happens in case the bot is to slow, throws an exception during operation, etc"""

    @abstractmethod
    def get_move(self, bot: Bot, state: PlayerGameState) -> Move:
        pass


class SimpleMoveRequester(MoveRequester):

    """The simplest just asks the move"""

    def get_move(self, bot: Bot, state: PlayerGameState) -> Move:
        return bot.get_move(state)


class MoveValidator(ABC):
    @abstractmethod
    def get_legal_leader_moves(self, game_state: GameState) -> Iterable[Move]:
        pass

    @abstractmethod
    def get_legal_follower_moves(self, game_state, partial_trick: PartialTrick) -> Iterable[Move]:
        pass


class SchnapsenMoveValidator(MoveValidator):

    def get_legal_leader_moves(self, game_state: GameState) -> Iterable[Move]:
        # all cards in the hand can be played
        cards_in_hand = game_state.leader.hand.get_cards()
        valid_moves: List[Move] = [RegularMove(card) for card in cards_in_hand]
        # trump exchanges
        trump_jack = Card.get_card(Rank.JACK, game_state.trump_suit)
        if trump_jack in cards_in_hand:
            valid_moves.append(Trump_Exchange(trump_jack))
        # mariages
        for card in cards_in_hand:
            if card.rank is Rank.QUEEN:
                king_card = Card.get_card(Rank.KING, card.suit)
                if king_card in cards_in_hand:
                    valid_moves.append(Marriage(card, king_card))
        return valid_moves

    def get_legal_follower_moves(self, game_state, partial_trick: PartialTrick) -> Iterable[Move]:
        hand = game_state.follower.hand
        leader_card = partial_trick.first_move.card
        if game_state.game_phase() is GamePhase.ONE:
            # no need to follow, any card in the hand is a legal move
            return RegularMove.from_cards(hand.get_cards())
        else:
            # information from https://www.pagat.com/marriage/schnaps.html
            # ## original formulation ##
            # if your opponent leads a non-trump:
            #     you must play a higher card of the same suit if you can;
            #     failing this you must play a lower card of the same suit;
            #     if you have no card of the suit that was led you must play a trump;
            #     if you have no trumps either you may play anything.
            # If your opponent leads a trump:
            #     you must play a higher trump if possible;
            #     if you have no higher trump you must play a lower trump;
            #     if you have no trumps at all you may play anything.
            # ## implemented version, realizing that the rules for trump are overlapping with the normal case ##
            # you must play a higher card of the same suit if you can
            # failing this, you must play a lower card of the same suit;
            # --new--> failing this, if the opponen did not play a trump, you must play a trump
            # failing this, you can play anything
            leader_card_score = game_state.scorer.RANK_TO_POINTS[leader_card.rank]
            # you must play a higher card of the same suit if you can;
            same_suit_cards = hand.filter(leader_card.suit)
            if same_suit_cards:
                higher_same_suit, lower_same_suit = [], []
                for card in same_suit_cards:
                    # TODO this is slightly ambigousm should this be >= ??
                    higher_same_suit.append(card) if game_state.scorer.RANK_TO_POINTS[card.rank] > leader_card_score else lower_same_suit.append(card)
                if higher_same_suit:
                    return RegularMove.from_cards(higher_same_suit)
            # failing this, you must play a lower card of the same suit;
                elif lower_same_suit:
                    return RegularMove.from_cards(lower_same_suit)
                raise AssertionError("Somethign is wrong in the logic here. There should be cards, but they are neither placed in the low, nor higher list")
            # failing this, if the opponen did not play a trump, you must play a trump
            trump_cards = hand.filter(game_state.trump_suit)
            if leader_card.suit != game_state.trump_suit and trump_cards:
                return RegularMove.from_cards(trump_cards)
            # failing this, you can play anything
            return RegularMove.from_cards(hand.get_cards())


class TrickScorer(ABC):
    @abstractmethod
    def score(self, t: Trick, leader: Bot, follower: Bot, trump: Suit) -> Tuple[Bot, Bot]:
        """The returned bots having the score of the trick applied, and are returned in order (new_leader, new_follower)"""
        # Note: also pending points need to be applied here.
        raise NotImplementedError("TODO")

    @abstractmethod
    def declare_winner(self) -> Optional[Bot]:
        """return a bot it there is a winner of this game already"""
        pass

    @abstractmethod
    def rank_to_points(self) -> Mapping[Suit, int]:
        pass

    @abstractmethod
    def marriage(self) -> 'Score':
        pass

    @abstractmethod
    def royal_marriage(self) -> 'Score':
        pass


class SchnapsenTrickScorer(TrickScorer):

    def rank_to_points(self) -> Mapping[Suit, int]:
        return {
            Rank.ACE: 11,
            Rank.TEN: 10,
            Rank.KING: 4,
            Rank.QUEEN: 3,
            Rank.JACK: 2,
        }

    def marriage(self) -> 'Score':
        new_score = Score(pending_points=20)
        return new_score

    def royal_marriage(self) -> 'Score':
        new_score = Score(pending_points=40)
        return new_score

    def score(self, t: Trick, leader: Bot, follower: Bot, trump: Suit) -> Tuple[Bot, Bot]:
        raise NotImplementedError()
# some code copied from the old engine
# if len(trick) != 2:
# 			raise RuntimeError("Incorrect trick format. List of length 2 needed.")
# 		if trick[0] is None or trick[1] is None:
# 			raise RuntimeError("An incomplete trick was attempted to be evaluated.")

# 		# If the two cards of the trick have the same suit
# 		if Deck.get_suit(trick[0]) == Deck.get_suit(trick[1]):

# 			# We only compare indices since the convention we defined in Deck
# 			# puts higher rank cards at lower indices, when considering the same color.
# 			return 1 if trick[0] < trick[1] else 2

# 		if Deck.get_suit(trick[0]) ==  self.__deck.get_trump_suit():
# 			return 1

# 		if Deck.get_suit(trick[1]) ==  self.__deck.get_trump_suit():
# 			return 2

    # def score(self, trick: Trick) -> Score:
    #     # score_one = trick.
    #     pass


class GamePlayEngine:
    deck_generator: DeckGenerator
    hand_generator: HandGenerator
    trick_player: TrickPlayer
    play_trick: TrickPlayer
    move_requester: MoveRequester
    move_validator: MoveValidator
    scorer: TrickScorer

    def play_game(bot1, bot2):

        raise NotImplementedError()

    # TODO the idea of the following method is to be able to implementsomething like rdeep
    # we still need to figure out how to let it play from an intermediate state with only one move played

    def play_game_from_state(bot1, bot2, GameState):
        pass

    # # TODO this is very specific to the standard schnapsen game. move out to its own class?
    # def get_legal_moves(bot: Bot, partial_trick: Optional[PartialTrick] = None)-> Iterable[Move]:
    #     """Get all legal moves. The PartialTrick is None in case this is the leader. The PartialTrick contains the Move of the leader in case this is move for the follower"""


# class FirstMovePhaseOneState:
#     player_hand: Hand
#     trump: Card
#     talon: InvisibleTalon


# class SecondMovePhaseTwoState:
#     player_hand: Hand
#     opponent_hand: Hand
#     on_table: PartialTrick
#     trump: Card


# engine = GamePlayEngine(startingDeck=MyDeck(), hand_generator = HandGenetation, play_trick = MyPlayTrick(), move_requester=Move_Requester, move_validator = MoveValidator(), scorer = ScoreThing() ),


# engine.play_game(bot1, bot 2)
