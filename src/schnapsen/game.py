from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from random import Random
from typing import Iterable, List, Optional, Tuple, Union, cast, Any
from .deck import CardCollection, OrderedCardCollection, Card, Rank, Suit


class Bot(ABC):

    @abstractmethod
    def get_move(self, state: 'PlayerGameState') -> 'Move':
        pass


class Move(ABC):
    """
    A single move during a game. There are several concreate moves possible. They are classes inheriting from this class.

    Attributes:
        cards: list(Card) The cards played in this move

    """

    def is_marriage(self) -> bool:
        return False

    def is_trump_exchange(self) -> bool:
        return False

    def __getattribute__(self, __name: str) -> Any:
        if __name == "cards":
            # We call the method to compute the card list
            return object.__getattribute__(self, "_cards")()
        return object.__getattribute__(self, __name)

    @abstractmethod
    def _cards(self) -> Iterable[Card]:
        pass


@dataclass(frozen=True)
class Trump_Exchange(Move):
    jack: Card

    def __post_init__(self) -> None:
        assert self.jack.rank is Rank.JACK

    def is_trump_exchange(self) -> bool:
        return True

    def _cards(self) -> Iterable[Card]:
        return [self.jack]

    def __repr__(self) -> str:
        return f"Trump_Exchange(jack={self.jack})"


@dataclass(frozen=True)
class RegularMove(Move):
    card: Card

    def _cards(self) -> Iterable[Card]:
        return [self.card]

    @staticmethod
    def from_cards(cards: Iterable[Card]) -> Iterable[Move]:
        return [RegularMove(card) for card in cards]

    def __repr__(self) -> str:
        return f"RegularMove(card={self.card})"


@dataclass(frozen=True)
class Marriage(Move):
    queen_card: Card
    king_card: Card
    suit: Suit = field(init=False, repr=False, hash=False)

    def __post_init__(self) -> None:
        assert self.queen_card.rank is Rank.QUEEN
        assert self.king_card.rank is Rank.KING
        assert self.queen_card.suit == self.king_card.suit
        object.__setattr__(self, "suit", self.queen_card.suit)

    def is_marriage(self) -> bool:
        return True

    def as_regular_move(self) -> RegularMove:
        # TODO this limits you to only have the queen to play after a marriage, while in general you would ahve a choice
        return RegularMove(self.queen_card)

    def _cards(self) -> Iterable[Card]:
        return [self.queen_card, self.king_card]

    def __repr__(self) -> str:
        return f"Marriage(queen_card={self.queen_card}, king_card={self.king_card})"


class Hand(CardCollection):
    def __init__(self, cards: Iterable[Card], max_size: int = 5) -> None:
        self.max_size = max_size
        cards = list(cards)
        assert len(cards) <= max_size, f"The number of cards {len(cards)} is larger than the maximum number fo allowed cards {max_size}"
        self.cards = cards

    def remove(self, card: Card) -> None:
        """Remove one occurence of the card from this hand"""
        try:
            self.cards.remove(card)
        except ValueError:
            raise Exception(f"Trying to remove a card from the hand which is not in the hand. Hand is {self.cards}, trying to remove {card}")

    def add(self, card: Card) -> None:
        assert len(self.cards) < self.max_size, "Adding one more card to the hand will cause a hand with too many cards"
        self.cards.append(card)

    def has_cards(self, cards: Iterable[Card]) -> bool:
        return all([card in self.cards for card in cards])

    def copy(self) -> 'Hand':
        return Hand(list(self.cards), max_size=self.max_size)

    def is_empty(self) -> bool:
        return len(self.cards) == 0

    def get_cards(self) -> Iterable[Card]:
        return list(self.cards)

    def filter_suit(self, suit: Suit) -> Iterable[Card]:
        """Returns an Iterable with in it all cards which have the provided suit"""
        results = [card for card in self.cards if card.suit is suit]
        return results

    def filter_rank(self, rank: Rank) -> Iterable[Card]:
        """Returns an Iterable with in it all cards which have the provided rank"""
        results = [card for card in self.cards if card.rank is rank]
        return results

    def __repr__(self) -> str:
        return f"Hand(cards={self.cards}, max_size={self.max_size})"

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

    def __init__(self, cards: Iterable[Card], trump_suit: Optional[Suit] = None) -> None:
        """The cards of the Talon. The last card is the bottommost card. The first one is the top card (which will be taken is a card is drawn)
            The Trump card is at the bottom of the Talon.
        """
        if cards:
            trump_card_suit = list(cards)[-1].suit
            assert not trump_suit or trump_card_suit == trump_suit, "If the trump suit is specified, and there are cards on the talon, the suit must be the same!"
            self.__trump_suit = trump_card_suit
        else:
            assert trump_suit
            self.__trump_suit = trump_suit

        super().__init__(cards)

    def copy(self) -> 'Talon':
        return Talon(self._cards, self.__trump_suit)

    def trump_exchange(self, new_trump: Card) -> Card:
        """ perfom a trump-jack exchange. The card to be put as the trump card must be a Jack of the same suit.
        As a result, this Talon changed: the old trump is removed and the new_trump is at the bottom of the Talon"""
        assert new_trump.rank is Rank.JACK
        assert len(self._cards) >= 2
        assert new_trump.suit is self._cards[-1].suit
        old_trump = self._cards.pop(len(self._cards) - 1)
        self._cards.append(new_trump)

# question: wouldn t this put the new trump at the top of the deck ?
# and also remove the card at the top too

        return old_trump

    def draw_cards(self, amount: int) -> Iterable[Card]:
        """Draw a card from this Talon. This does not change the talon, btu rather returns a talon with the change applied and the card drawn"""
        assert len(self._cards) >= amount, f"There are only {len(self._cards)} on the Talon, but {amount} cards are requested"
        draw = self._cards[:amount]
        self._cards = self._cards[amount:]
        return draw

    def trump_suit(self) -> Suit:
        return self.__trump_suit

    def __repr__(self) -> str:
        return f"Talon(cards={self._cards}, trump_suit={self.__trump_suit})"


@dataclass(frozen=True)
class PartialTrick:
    trump_exchange: Optional[Trump_Exchange]
    leader_move: Union[RegularMove, Marriage]

    def __repr__(self) -> str:
        return f"PartialTrick(trump_exchange={self.trump_exchange}, leader_move={self.leader_move})"


@dataclass(frozen=True)
class Trick(PartialTrick):
    follower_move: RegularMove

    def __repr__(self) -> str:
        return f"Trick(trump_exchange={self.trump_exchange}, leader_move={self.leader_move}, follower_move={self.follower_move})"


@dataclass(frozen=True)
class Score:
    direct_points: int = 0
    pending_points: int = 0

    def __add__(self, other: 'Score') -> 'Score':
        total_direct_points = self.direct_points + other.direct_points
        total_pending_points = self.pending_points + other.pending_points
        return Score(total_direct_points, total_pending_points)

    def copy(self) -> 'Score':
        return Score(direct_points=self.direct_points, pending_points=self.pending_points)

    def redeem_pending_points(self) -> 'Score':
        return Score(direct_points=self.direct_points + self.pending_points, pending_points=0)

    def __repr__(self) -> str:
        return f"Score(direct_points={self.direct_points}, pending_points={self.pending_points})"


class GamePhase(Enum):
    ONE = 1
    TWO = 2


@dataclass
class BotState:
    """A bot with its implementation and current state in a game"""

    implementation: Bot
    hand: Hand
    bot_id: str
    score: Score = field(default_factory=Score)
    won_cards: List[Card] = field(default_factory=list)

    def get_move(self, state: 'PlayerGameState') -> Move:
        move = self.implementation.get_move(state)
        assert self.hand.has_cards(move.cards), \
            f"Tried to play a move for which the player does not have the cards. Played {move.cards}, but has {self.hand}"
        return move

    def copy(self) -> 'BotState':
        new_bot = BotState(
            implementation=self.implementation,
            hand=self.hand.copy(),
            score=self.score.copy(),
            won_cards=list(self.won_cards),
            bot_id=self.bot_id
        )
        return new_bot

    def __repr__(self) -> str:
        return f"BotState(implementation={self.implementation}, hand={self.hand}, "\
               f"bot_id={self.bot_id}, score={self.score}, won_cards={self.won_cards})"


@dataclass
class GameState:
    leader: BotState
    follower: BotState
    trump_suit: Suit = field(init=False)
    talon: Talon
    previous: Optional['GameState']
    played_trick: Optional[Trick] = None
    # TODO it might be that we have to include the ongoing trick here, such that a bot can implement things like rdeep easily
    # ongoing_trick: PartialTrick
    # TODO it is probably a good idea to keep the seen cards here

    def __post_init__(self) -> None:
        self.trump_suit = self.talon.trump_suit()

    def copy_for_next(self) -> 'GameState':
        """Make a copy of the gamestate"""

        leader = self.leader.copy()
        follower = self.follower.copy()
        # We intentionally do no initialize played_trick
        new_state = GameState(leader=leader, follower=follower, talon=self.talon.copy(), previous=self)
        return new_state

    def game_phase(self) -> GamePhase:
        if self.talon.is_empty():
            return GamePhase.TWO
        else:
            return GamePhase.ONE

    def all_cards_played(self) -> bool:
        return self.leader.hand.is_empty() and self.follower.hand.is_empty() and self.talon.is_empty()

    def __repr__(self) -> str:
        return f"GameState(leader={self.leader}, follower={self.follower}, "\
               f"talon={self.talon}, previous={self.previous}, "\
               f"played_trick={self.played_trick})"


class PlayerGameState(ABC):
    def __init__(self, state: 'GameState', engine: 'GamePlayEngine') -> None:
        self.__game_state = state
        self.__engine = engine

    @abstractmethod
    def valid_moves(self) -> List[Move]:
        """
        Get a list of all valid moves the bot can play at this point in the game.

        Design note: this could also return an Iterable[Move], but List[Move] was chosen to make the API easier to use.
        """
        pass

    def get_opponent_card(self) -> Optional[Move]:
        raise NotImplementedError()

    # TODO define what should be returned from this method
    def get_game_history(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def get_hand(self) -> Hand:
        pass

    @abstractmethod
    def get_my_score(self) -> Score:
        raise NotImplementedError()

    @abstractmethod
    def get_opponent_score(self) -> Score:
        raise NotImplementedError()

    def get_trump_suit(self) -> Suit:
        return self.__game_state.trump_suit

    def get_talon_size(self) -> int:
        return len(self.__game_state.talon)

    def get_phase(self) -> GamePhase:
        return self.__game_state.game_phase()

    @abstractmethod
    def get_opponent_hand_in_phase_two(self) -> Hand:
        raise NotImplementedError()

    def make_assumption(self) -> 'GameState':
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
    def __init__(self, state: 'GameState', engine: 'GamePlayEngine') -> None:
        super().__init__(state, engine)
        self.__game_state = state
        self.__engine = engine

    def valid_moves(self) -> List[Move]:
        moves = self.__engine.move_validator.get_legal_leader_moves(self.__engine, self.__game_state)
        return list(moves)

    # TODO check the following implementation
    def get_hand(self) -> Hand:
        return self.__game_state.leader.hand.copy()

    def get_my_score(self) -> Score:
        raise NotImplementedError()

    def get_opponent_score(self) -> Score:
        raise NotImplementedError()

    def get_opponent_hand_in_phase_two(self) -> Hand:
        assert self.get_phase() == GamePhase.TWO
        return self.__game_state.follower.hand.copy()

    def __repr__(self) -> str:
        return f"LeaderGameState(state={self.__game_state}, engine={self.__engine})"


class FollowerGameState(PlayerGameState):
    def __init__(self, state: 'GameState', engine: 'GamePlayEngine', partial_trick: PartialTrick) -> None:
        super().__init__(state, engine)
        self.__game_state = state
        self.__engine = engine
        self.partial_trick = partial_trick

    def valid_moves(self) -> List[Move]:
        return list(self.__engine.move_validator.get_legal_follower_moves(self.__engine, self.__game_state, self.partial_trick))

    def get_hand(self) -> Hand:
        return self.__game_state.follower.hand.copy()

    def get_my_score(self) -> Score:
        raise NotImplementedError()

    def get_opponent_score(self) -> Score:
        raise NotImplementedError()

    def get_opponent_hand_in_phase_two(self) -> Hand:
        assert self.get_phase() == GamePhase.TWO
        return self.__game_state.leader.hand.copy()

    def __repr__(self) -> str:
        return f"FollowerGameState(state={self.__game_state}, engine={self.__engine}, "\
               f"partial_trick={self.partial_trick})"


class DeckGenerator(ABC):
    @abstractmethod
    def get_initial_deck(self) -> OrderedCardCollection:
        pass

    @classmethod
    def shuffle_deck(self, deck: OrderedCardCollection, rng: Random) -> OrderedCardCollection:
        the_cards = list(deck.get_cards())
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
    def generateHands(self, cards: OrderedCardCollection) -> Tuple[Hand, Hand, Talon]:
        pass


class SchnapsenHandGenerator(HandGenerator):
    @classmethod
    def generateHands(self, cards: OrderedCardCollection) -> Tuple[Hand, Hand, Talon]:
        the_cards = list(cards.get_cards())
        hand1 = Hand([the_cards[i] for i in range(0, 10, 2)], max_size=5)
        hand2 = Hand([the_cards[i] for i in range(1, 11, 2)], max_size=5)
        rest = Talon(the_cards[10:])
        return (hand1, hand2, rest)


class TrickImplementer(ABC):
    @abstractmethod
    def play_trick(self, game_engine: 'GamePlayEngine', game_state: GameState) -> GameState:
        pass


class SchnapsenTrickImplementer(TrickImplementer):

    def play_trick(self, game_engine: 'GamePlayEngine', game_state: GameState) -> GameState:
        mutable_game_state = game_state.copy_for_next()
        trick = self._play_trick(game_engine, mutable_game_state)
        mutable_game_state.played_trick = trick
        return mutable_game_state

    def _play_trick(self, game_engine: 'GamePlayEngine', game_state: 'GameState') -> Trick:
        partial_trick = self.get_leader_move(game_engine, game_state)

        if partial_trick.leader_move.is_marriage():
            regular_leader_move: RegularMove = cast(Marriage, partial_trick.leader_move).as_regular_move()
        else:
            regular_leader_move = cast(RegularMove, partial_trick.leader_move)

        game_state.leader.hand.remove(regular_leader_move.card)

        follower_move = self.get_follower_move(game_engine, game_state, partial_trick)
        game_state.follower.hand.remove(follower_move.card)

        trick = Trick(trump_exchange=partial_trick.trump_exchange, leader_move=partial_trick.leader_move, follower_move=follower_move)

        game_state.leader, game_state.follower = game_engine.trick_scorer.score(trick, game_state.leader, game_state.follower, game_state.trump_suit)

        # important: the winner takes the first card of the talon, the loser the second one.
        # this also ensures that the loser of the last trick of the first phase gets the face up trump
        if not game_state.talon.is_empty():
            drawn = iter(game_state.talon.draw_cards(2))
            game_state.leader.hand.add(next(drawn))
            game_state.follower.hand.add(next(drawn))

        return trick

    def __get_one_valid_leader_move(self, game_engine: 'GamePlayEngine', game_state: 'GameState') -> Union[Trump_Exchange, Marriage, RegularMove]:
        # ask first players move trough the requester
        leader_game_state = LeaderGameState(game_state, game_engine)
        leader_move = game_engine.move_requester.get_move(game_state.leader, leader_game_state)
        if not game_engine.move_validator.is_legal_leader_move(game_engine, game_state, leader_move):
            raise Exception("Leader played an illegal move")
        return cast(Union[Trump_Exchange, Marriage, RegularMove], leader_move)

    def get_leader_move(self, game_engine: 'GamePlayEngine', game_state: 'GameState') -> PartialTrick:
        first_move: Union[Trump_Exchange, Marriage, RegularMove] = self.__get_one_valid_leader_move(game_engine, game_state)
        trump_exchange: Optional[Trump_Exchange]
        leader_move: Union[Marriage, RegularMove]
        if first_move.is_trump_exchange():
            trump_exchange = cast(Trump_Exchange, first_move)
            self.play_trump_exchange(game_state, trump_exchange)
            # ask first players move again, as the exchange is not a real move
            leader_move = cast(Union[Marriage, RegularMove], self.__get_one_valid_leader_move(game_engine, game_state))
        else:
            trump_exchange = None
            leader_move = cast(Union[Marriage, RegularMove], first_move)

        if leader_move.is_marriage():
            marriage_move: Marriage = cast(Marriage, leader_move)
            self._play_marriage(game_engine, game_state, marriage_move=marriage_move)

        partial_trick = PartialTrick(trump_exchange=trump_exchange, leader_move=leader_move)
        return partial_trick

    def play_trump_exchange(self, game_state: GameState, trump_exhange: Trump_Exchange) -> None:
        assert trump_exhange.jack.suit is game_state.trump_suit, \
            f"A trump exchange can only be done with a Jack of the same suit as the current trump. Got a {trump_exhange.jack} while the  Trump card is a {game_state.trump_suit}"
        # apply the changes in the gamestate
        game_state.leader.hand.remove(trump_exhange.jack)
        old_trump = game_state.talon.trump_exchange(trump_exhange.jack)
        game_state.leader.hand.add(old_trump)

    def _play_marriage(self, game_engine: 'GamePlayEngine', game_state: GameState, marriage_move: Marriage) -> None:
        score = game_engine.trick_scorer.marriage(marriage_move, game_state)
        game_state.leader.score += score

    def get_follower_move(self, game_engine: 'GamePlayEngine', game_state: 'GameState', partial_trick: PartialTrick) -> RegularMove:
        follower_game_state = FollowerGameState(game_state, game_engine, partial_trick)

        follower_move = game_engine.move_requester.get_move(game_state.follower, follower_game_state)
        if follower_move not in game_engine.move_validator.get_legal_follower_moves(game_engine, game_state, partial_trick):
            raise Exception("Follower played an illegal move")
        return cast(RegularMove, follower_move)


class MoveRequester:
    """An the logic of requesting a move from a bot.
    This logic also determines what happens in case the bot is to slow, throws an exception during operation, etc"""

    @abstractmethod
    def get_move(self, bot: BotState, state: PlayerGameState) -> Move:
        pass


class SimpleMoveRequester(MoveRequester):

    """The simplest just asks the move"""

    def get_move(self, bot: BotState, state: PlayerGameState) -> Move:
        return bot.get_move(state)


class MoveValidator(ABC):
    @abstractmethod
    def get_legal_leader_moves(self, game_engine: 'GamePlayEngine', game_state: GameState) -> Iterable[Move]:
        pass

    @abstractmethod
    def get_legal_follower_moves(self, game_engine: 'GamePlayEngine', game_state: GameState, partial_trick: PartialTrick) -> Iterable[Move]:
        pass

    def is_legal_leader_move(self, game_engine: 'GamePlayEngine', game_state: GameState, move: Move) -> bool:
        return move in self.get_legal_leader_moves(game_engine, game_state)


class SchnapsenMoveValidator(MoveValidator):

    def get_legal_leader_moves(self, game_engine: 'GamePlayEngine', game_state: GameState) -> Iterable[Move]:
        # all cards in the hand can be played
        cards_in_hand = game_state.leader.hand
        valid_moves: List[Move] = [RegularMove(card) for card in cards_in_hand]
        # trump exchanges
        if not game_state.talon.is_empty():
            trump_jack = Card.get_card(Rank.JACK, game_state.trump_suit)
            if trump_jack in cards_in_hand:
                valid_moves.append(Trump_Exchange(trump_jack))
        # mariages
        for card in cards_in_hand.filter_rank(Rank.QUEEN):
            king_card = Card.get_card(Rank.KING, card.suit)
            if king_card in cards_in_hand:
                valid_moves.append(Marriage(card, king_card))
        return valid_moves

    def is_legal_leader_move(self, game_engine: 'GamePlayEngine', game_state: GameState, move: Move) -> bool:
        cards_in_hand = game_state.leader.hand
        if move.is_marriage():
            marriage_move = cast(Marriage, move)
            # we do not have to check whether they are the same suit because of the implementation of Marriage
            return marriage_move.queen_card in cards_in_hand and marriage_move.king_card in cards_in_hand
        if move.is_trump_exchange():
            if game_state.talon.is_empty():
                return False
            trump_move: Trump_Exchange = cast(Trump_Exchange, move)
            return trump_move.jack in cards_in_hand
        # it has to be a regular move
        regular_move = cast(RegularMove, move)
        return regular_move.card in cards_in_hand

    def get_legal_follower_moves(self, game_engine: 'GamePlayEngine', game_state: GameState, partial_trick: PartialTrick) -> Iterable[Move]:
        hand = game_state.follower.hand
        if partial_trick.leader_move.is_marriage():
            leader_card = cast(Marriage, partial_trick.leader_move).queen_card
        else:
            leader_card = cast(RegularMove, partial_trick.leader_move).card
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
            leader_card_score = game_engine.trick_scorer.rank_to_points(leader_card.rank)
            # you must play a higher card of the same suit if you can;
            same_suit_cards = hand.filter_suit(leader_card.suit)
            if same_suit_cards:
                higher_same_suit, lower_same_suit = [], []
                for card in same_suit_cards:
                    # TODO this is slightly ambigousm should this be >= ??
                    higher_same_suit.append(card) if game_engine.trick_scorer.rank_to_points(card.rank) > leader_card_score else lower_same_suit.append(card)
                if higher_same_suit:
                    return RegularMove.from_cards(higher_same_suit)
            # failing this, you must play a lower card of the same suit;
                elif lower_same_suit:
                    return RegularMove.from_cards(lower_same_suit)
                raise AssertionError("Somethign is wrong in the logic here. There should be cards, but they are neither placed in the low, nor higher list")
            # failing this, if the opponen did not play a trump, you must play a trump
            trump_cards = hand.filter_suit(game_state.trump_suit)
            if leader_card.suit != game_state.trump_suit and trump_cards:
                return RegularMove.from_cards(trump_cards)
            # failing this, you can play anything
            return RegularMove.from_cards(hand.get_cards())


class TrickScorer(ABC):
    @abstractmethod
    def score(self, trick: Trick, leader: BotState, follower: BotState,
              trump: Suit) -> Tuple[BotState, BotState]:
        """The returned bots having the score of the trick applied, and are returned in order (new_leader, new_follower)"""
        # Note: also pending points need to be applied here.
        pass

    @abstractmethod
    def declare_winner(self, game_state: GameState) -> Optional[Tuple[BotState, int]]:
        """return a bot and the number of points if there is a winner of this game already"""
        pass

    @abstractmethod
    def rank_to_points(self, rank: Rank) -> int:
        pass

    @abstractmethod
    def marriage(self, move: Marriage, gamestate: GameState) -> 'Score':
        pass


class SchnapsenTrickScorer(TrickScorer):

    SCORES = {
        Rank.ACE: 11,
        Rank.TEN: 10,
        Rank.KING: 4,
        Rank.QUEEN: 3,
        Rank.JACK: 2,
    }

    def rank_to_points(self, rank: Rank) -> int:
        return SchnapsenTrickScorer.SCORES[rank]

    def marriage(self, move: Marriage, gamestate: GameState) -> 'Score':
        if move.suit is gamestate.trump_suit:
            # royal marriage
            return Score(pending_points=40)
        else:
            # any other marriage
            return Score(pending_points=20)

    # def score(self, leader_move: RegularMove, follower_move: RegularMove, leader: BotState, follower: BotState, trump: Suit) -> Tuple[BotState, BotState]:
    def score(self, trick: Trick, leader: BotState, follower: BotState, trump: Suit) -> Tuple[BotState, BotState]:

        if trick.leader_move.is_marriage():
            regular_leader_move: RegularMove = cast(Marriage, trick.leader_move).as_regular_move()
        else:
            regular_leader_move = cast(RegularMove, trick.leader_move)

        leader_card = regular_leader_move.card
        follower_card = trick.follower_move.card
        assert leader_card != follower_card
        leader_card_points = self.rank_to_points(leader_card.rank)
        follower_card_points = self.rank_to_points(follower_card.rank)

        if leader_card.suit is follower_card.suit:
            # same suit, either trump or not
            if leader_card_points > follower_card_points:
                leader_wins = True
            else:
                leader_wins = False
        elif leader_card.suit is trump:
            # the follower suit cannot be trumps as per the previous condition
            leader_wins = True
        elif follower_card.suit is trump:
            # the leader suit cannot be trumps because of the previous conditions
            leader_wins = False
        else:
            # the follower did not follow the suit of the leader and did not play trumps, hence the leader wins
            leader_wins = True
        winner, loser = (leader, follower) if leader_wins else (follower, leader)
        # record the win
        winner.won_cards.extend([leader_card, follower_card])
        # apply the points
        points_gained = leader_card_points + follower_card_points
        winner.score += Score(direct_points=points_gained)
        # add winner's total of direct and pending points as their new direct points
        winner.score = winner.score.redeem_pending_points()
        return winner, loser

    def declare_winner(self, game_state: GameState) -> Optional[Tuple[BotState, int]]:
        """
        Declaring a winner uses the logic from https://www.pagat.com/marriage/schnaps.html#marriages , but simplified, because we do not have closing of the Talon and no need to guess the scores.
        The following text adapted accordingly from that website.

        If a player has 66 or more points, she scores points toward game as follows:

            * one game point, if the opponent has made at least 33 points;
            * two game points, if the opponent has made fewer than 33 points, but has won at least one trick (opponent is said to be Schneider);
            * three game points, if the opponent has won no tricks (opponent is said to be Schwarz).

        If play continued to the very last trick with the talon exhausted, the player who takes the last trick wins the hand, scoring one game point, irrespective of the number of card points the players have taken.
        """
        if game_state.leader.score.direct_points >= 66:
            follower_score = game_state.follower.score.direct_points
            if follower_score == 0:
                return game_state.leader, 3
            elif follower_score >= 33:
                return game_state.leader, 1
            else:
                # second case in explaination above, 0 < score < 33
                assert follower_score < 66
                return game_state.leader, 2
        elif game_state.follower.score.direct_points >= 66:
            raise AssertionError("Would declare the follower winner, but this should never happen in the current implementation")
        elif game_state.all_cards_played():
            return game_state.leader, 1
        else:
            return None


@dataclass
class GamePlayEngine:
    deck_generator: DeckGenerator
    hand_generator: HandGenerator
    trick_implementer: TrickImplementer
    move_requester: MoveRequester
    move_validator: MoveValidator
    trick_scorer: TrickScorer

    def play_game(self, bot1: Bot, bot2: Bot, rng: Random) -> None:
        cards = self.deck_generator.get_initial_deck()
        shuffled = self.deck_generator.shuffle_deck(cards, rng)
        hand1, hand2, talon = self.hand_generator.generateHands(shuffled)

        leader_state = BotState(implementation=bot1, hand=hand1, bot_id="bot1")
        follower_state = BotState(implementation=bot2, hand=hand2, bot_id="bot2")

        game_state = GameState(
            leader=leader_state,
            follower=follower_state,
            talon=talon,
            previous=None
        )

        winner: Optional[BotState] = None
        points: int = -1
        while not winner:
            game_state = self.trick_implementer.play_trick(self, game_state)
            winner, points = self.trick_scorer.declare_winner(game_state) or (None, -1)
        winner_id = winner.bot_id
        print(f"Game ended. Winner is {winner_id} with {points} points")

        # raise NotImplementedError("This should return something reasonable")

    # TODO the idea of the following method is to be able to implementsomething like rdeep
    # we still need to figure out how to let it play from an intermediate state with only one move played

    def play_game_from_state(self, bot1: BotState, bot2: BotState, game_state: GameState) -> None:
        raise NotImplementedError()

    def __repr__(self) -> str:
        return f"GamePlayEngine(deck_generator={self.deck_generator}, "\
               f"hand_generator={self.hand_generator}, "\
               f"trick_implementer={self.trick_implementer}, "\
               f"move_requester={self.move_requester}, "\
               f"move_validator={self.move_validator}, "\
               f"trick_scorer={self.trick_scorer})"


class SchnapsenGamePlayEngine(GamePlayEngine):
    def __init__(self) -> None:
        super().__init__(
            deck_generator=SchnapsenDeckGenerator(),
            hand_generator=SchnapsenHandGenerator(),
            trick_implementer=SchnapsenTrickImplementer(),
            move_requester=SimpleMoveRequester(),
            move_validator=SchnapsenMoveValidator(),
            trick_scorer=SchnapsenTrickScorer()
        )

    def __repr__(self) -> str:
        return super().__repr__()


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
