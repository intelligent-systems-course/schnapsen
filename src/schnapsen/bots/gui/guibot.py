from __future__ import annotations

from dataclasses import dataclass
from json import dumps
from threading import Event, Thread
from types import TracebackType
from typing import Optional, Type, cast

from flask import Flask, abort, render_template, request

from schnapsen.deck import Card, Rank, Suit
from schnapsen.game import (Bot, GamePhase, Marriage, Move, PlayerPerspective,
                            RegularMove, RegularTrick, TrumpExchange)


@dataclass
class _StateExchange:
    bot: Bot
    browser_game_started: bool
    is_state_ready: Event
    is_move_ready: Event
    state: Optional[PlayerPerspective]
    leader_move: Optional[Move]
    browser_move: Optional[Move]
    is_game_over: bool = False
    won: bool = False
    """The value of this variable is only valid once is_game_over has been set to True."""


class SchnapsenServer:

    def __enter__(self) -> SchnapsenServer:
        return self

    def __exit__(self,
                 exctype: Optional[Type[BaseException]],
                 excinst: Optional[BaseException],
                 exctb: Optional[TracebackType]
                 ) -> bool:
        if excinst:
            print("Closing the server, because an Exception was raised")
            # by returning False, we indicate that the exception was not handled.
            return False
        print("Server closed")
        return True

    def __init__(self, host_name: str = "0.0.0.0", port: int = 8080) -> None:
        """Creates and starts the schnapsen server"""
        self.__host_name = host_name
        self.__port = port
        self.__bots: dict[str, _StateExchange] = {}

        app = Flask(__name__, template_folder='template')
        app.config.update(
            PROPAGATE_EXCEPTIONS=True
        )
        self.__setup_routes(app)
        self.__process = Thread(target=app.run, kwargs={"host": host_name, "port": port, "use_reloader": False, "debug": True})
        print(f"Starting the server on {self.__host_name}:{self.__port}")
        self.__process.start()

    def make_gui_bot(self, name: str) -> Bot:
        """Create a GUIBot to be used in a game.
        You have to make sure that the names are unique!!

        Args:
            name (str): the name of this GUIBot

        Returns:
            Bot: The newly created Bot, ready for playing a single game.
        """
        assert not self._has_bot(name), "A GUI bot with this name has been created before. The names must be unique."
        bot = GUIBot(self, name)
        self.__bots[name] = _StateExchange(bot=bot, browser_game_started=False, is_state_ready=Event(), is_move_ready=Event(), state=None, leader_move=None, browser_move=None)
        return bot

    def _has_bot(self, name: str) -> bool:
        return name in self.__bots

    def _post_final_state(self, botname: str, won: bool, perspective: PlayerPerspective) -> None:
        state_exchange = self.__bots[botname]
        state_exchange.state = perspective
        state_exchange.won = won
        state_exchange.is_game_over = True
        state_exchange.is_state_ready.set()

    def _get_move(self, botname: str, perspective: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        state_exchange = self.__bots[botname]
        state_exchange.is_move_ready.clear()
        state_exchange.state = perspective
        state_exchange.leader_move = leader_move
        state_exchange.is_state_ready.set()
        # we now wait for the browser to make the move
        state_exchange.is_move_ready.wait()
        move = state_exchange.browser_move
        assert move is not None
        return move

    def __sendmove(self, botname: str) -> str:
        data = cast(tuple[Optional[int], Optional[int]], request.get_json(force=True))
        old_move: tuple[Optional[int], Optional[int]] = (data[0], data[1])
        move = _Old_GUI_Compatibility.convert_move(old_move)

        state_exchange = self.__bots[botname]
        state_exchange.browser_move = move
        state_exchange.is_state_ready.clear()
        state_exchange.is_move_ready.set()
        return self.__generate(botname=botname)

    def __generate(self, botname: str) -> str:
        state_exchange = self.__bots[botname]
        state_exchange.is_state_ready.wait()

        state = state_exchange.state
        assert state  # cannot be None, because we waited for it.
        leader_move = state_exchange.leader_move
        json = _Old_GUI_Compatibility.player_game_state_to_json(perspective=state, leader_move=leader_move, game_over=state_exchange.is_game_over, won=state_exchange.won)
        return json

    def __setup_routes(self, app: Flask) -> None:
        app.route('/', methods=['GET'])(self._index)
        app.route('/game/<botname>', methods=['GET'])(self.__game)
        app.route('/generate/<botname>', methods=['GET'])(self.__generate)
        app.route('/sendmove/<botname>', methods=['POST'])(self.__sendmove)

    def _index(self) -> str:
        bots = [(botname, state.browser_game_started) for botname, state in self.__bots.items()]
        return render_template("gamechooser.html", bots=bots)

    def __game(self, botname: str) -> str:
        if self.__bots[botname].browser_game_started:
            abort(409, "This game has already started")

        self.__bots[botname].browser_game_started = True
        return render_template("index_interactive.html", botname=botname)


class GUIBot(Bot):
    """The GUIBot is the interface between the server and the schnapsen platform.
    When asked for a move, it makes sure the perspective gets shown in the browser and captures the move played.
    """

    def __init__(self, server: SchnapsenServer, name: str) -> None:
        """Create a GUIBot. It is not normal to do this yourself. The normal way to do this is by creating a schnapsen server and then call its
        make_gui_bot method. Otherwise the server won't be properly aware of this GUIBot.

        Args:
            server (SchnapsenServer): The schnapsen server to which this bot has already been registered
            name (str): The name of this GUI bot
        """
        super().__init__(name)
        self.name = name
        self.server = server

    def get_move(self, perspective: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        return self.server._get_move(self.name, perspective, leader_move)

    def notify_game_end(self, won: bool, perspective: PlayerPerspective) -> None:
        self.server._post_final_state(self.name, won, perspective)


class _Old_GUI_Compatibility:

    old_engine_order = [
        Card.ACE_CLUBS,
        Card.TEN_CLUBS,
        Card.KING_CLUBS,
        Card.QUEEN_CLUBS,
        Card.JACK_CLUBS,

        Card.ACE_DIAMONDS,
        Card.TEN_DIAMONDS,
        Card.KING_DIAMONDS,
        Card.QUEEN_DIAMONDS,
        Card.JACK_DIAMONDS,

        Card.ACE_HEARTS,
        Card.TEN_HEARTS,
        Card.KING_HEARTS,
        Card.QUEEN_HEARTS,
        Card.JACK_HEARTS,

        Card.ACE_SPADES,
        Card.TEN_SPADES,
        Card.KING_SPADES,
        Card.QUEEN_SPADES,
        Card.JACK_SPADES
    ]

    @staticmethod
    def convert_move(old_move: tuple[Optional[int], Optional[int]]) -> Move:
        if not old_move[1]:
            assert old_move[0] is not None, "In the old engine, all moves with the second part not set must be Regular moves"
            return RegularMove(_Old_GUI_Compatibility.old_engine_order[old_move[0]])
        if not old_move[0]:
            assert old_move[1] is not None, "In the old endinge, all moves with the first part not set must be Trump exchanges"
            return TrumpExchange(_Old_GUI_Compatibility.old_engine_order[old_move[1]])
        assert old_move[0] and old_move[1]
        if _Old_GUI_Compatibility.old_engine_order[old_move[0]].rank == Rank.KING:
            # swap
            old_move = (old_move[1], old_move[0])
        assert old_move[0] is not None and old_move[1] is not None
        return Marriage(queen_card=_Old_GUI_Compatibility.old_engine_order[old_move[0]], king_card=_Old_GUI_Compatibility.old_engine_order[old_move[1]])

    @staticmethod
    def player_game_state_to_json(perspective: PlayerPerspective, leader_move: Optional[Move], game_over: bool, won: bool) -> str:

        # Deck.convert_to_json
        # return {"card_state":self.__card_state, "p1_perspective":self.__p1_perspective,
        # "p2_perspective":self.__p2_perspective, "trick":self.__trick,
        # "previous_trick":self.__previous_trick, "stock":self.__stock,
        # "trump_suit":self.__trump_suit, "signature":self.__signature}

        # We do not add p2_perspective since it is never used on the client side, we also do not have the information for it
        # We do not incluide the trick explicitly. This anyway gets conveted into P1D and P2D in  card_state, so we do it at once
        # We leave out stock, because it can be derived from card_state
        #

        hand = perspective.get_hand()
        talon_size = perspective.get_talon_size()
        trump_card = perspective.get_trump_card()
        trump_suit = perspective.get_trump_suit()
        won_cards = perspective.get_won_cards()
        opponent_won_cards = perspective.get_opponent_won_cards()

        opponent_known_cards = perspective.get_known_cards_of_opponent_hand()

        partial_move_cards = leader_move.cards if leader_move else []
        if leader_move:
            if leader_move.is_regular_move():
                partial_move_down = leader_move.as_regular_move().card
            else:
                assert leader_move.is_marriage()
                partial_move_down = leader_move.as_marriage().underlying_regular_move().card
        else:
            partial_move_down = None

        card_state: list[str] = ["None"] * 20
        p1_perspective: list[str] = ["None"] * 20

        invisible_on_stack = talon_size - 1

        for index, card in enumerate(_Old_GUI_Compatibility.old_engine_order):
            this_card_state: Optional[str] = None
            this_p1_perspective: Optional[str] = None
            if card in hand:
                this_card_state = this_p1_perspective = 'P1H'
            elif card in won_cards:
                this_card_state = this_p1_perspective = 'P1W'
            elif card in opponent_known_cards:
                this_card_state = this_p1_perspective = 'P2H'
            elif card in opponent_won_cards:
                this_card_state = this_p1_perspective = 'P2W'
            elif card == trump_card:
                this_card_state = this_p1_perspective = 'S'
            # correct for the current partial move
            if card == partial_move_down:
                # This is the card which the opponent played
                this_card_state = this_p1_perspective = 'P2D'
            elif card in partial_move_cards:
                # it was in the partial move, but not down, so we know the card is now in the opponent hand
                this_card_state = this_p1_perspective = 'P2H'

            if not this_card_state:
                # This card is invisible to p1, and either on the stack or the opponents hand.
                this_p1_perspective = 'U'
                # we first add to the stack
                if invisible_on_stack > 0:
                    this_card_state = 'S'
                    invisible_on_stack -= 1
                else:
                    this_card_state = 'P2H'

            assert this_card_state
            assert this_p1_perspective

            card_state[index] = this_card_state
            p1_perspective[index] = this_p1_perspective

        assert not any(map(lambda x: x == "None", card_state))
        assert not any(map(lambda x: x == "None", p1_perspective))

        #

        # previous trick
        old_shape_previous_trick: list[int] = [-1, -1]
        history = perspective.get_game_history()
        if len(history) > 1:
            previous_trick = history[-2][1]
            assert previous_trick  # The history has at least length 2, so this trick cannot be None

            if previous_trick.is_trump_exchange():
                # ignore because the old platform does not deal with this.
                pass
            else:
                previous_regular_trick = cast(RegularTrick, previous_trick)
                # we only care about the cards which will go, not marriage
                if previous_regular_trick.leader_move.is_regular_move():
                    leadercard = previous_regular_trick.leader_move.as_regular_move().card
                elif previous_regular_trick.leader_move.is_marriage():
                    leadercard = previous_regular_trick.leader_move.as_marriage().queen_card
                followercard = previous_regular_trick.follower_move.card

                old_shape_previous_trick[0] = _Old_GUI_Compatibility.old_engine_order.index(leadercard)
                old_shape_previous_trick[1] = _Old_GUI_Compatibility.old_engine_order.index(followercard)

        # trump suit
        old_trump_suit: str
        if trump_suit == Suit.CLUBS:
            old_trump_suit = 'C'
        elif trump_suit == Suit.DIAMONDS:
            old_trump_suit = 'D'
        elif trump_suit == Suit.HEARTS:
            old_trump_suit = 'H'
        elif trump_suit == Suit.SPADES:
            old_trump_suit = 'S'
        else:
            raise AssertionError("Control flow must never reach here")

        stock = [index for index, value in enumerate(card_state) if value == 'S']
        # make sure the trump sets at the front

        if trump_card:
            old_trump_card_number = _Old_GUI_Compatibility.old_engine_order.index(trump_card)
            stock.remove(old_trump_card_number)
            stock.insert(0, old_trump_card_number)

        deck = {
            "card_state": card_state,
            "p1_perspective": p1_perspective,
            "previous_trick": old_shape_previous_trick,
            "trump_suit": old_trump_suit,
            "stock": stock
        }

        # mimcking the old one, leaving some thigns out
        # return dumps({"deck":self.__deck.convert_to_json(), "moves":self.moves(), "finished":self.finished(), "phase":self.__phase,
        # "leads_turn":self.__leads_turn, "player1s_turn":self.__player1s_turn, "p1_points":self.__p1_points, "p2_points":self.__p2_points,
        # "p1_pending_points":self.__p1_pending_points, "p2_pending_points":self.__p2_pending_points, "signature":self.__signature, "revoked":self.__revoked})

        # TODO implement with legal moves
        moves: list[tuple[Optional[int], Optional[int]]] = []
        if not game_over:
            for move in perspective.valid_moves():
                if move.is_trump_exchange():
                    trump_move = cast(TrumpExchange, move)
                    moves.append((None, _Old_GUI_Compatibility.old_engine_order.index(trump_move.jack)))
                elif move.is_marriage():
                    marriage_move = cast(Marriage, move)
                    moves.append((_Old_GUI_Compatibility.old_engine_order.index(marriage_move.queen_card), _Old_GUI_Compatibility.old_engine_order.index(marriage_move.king_card)))
                else:
                    # regular move
                    regular_move = cast(RegularMove, move)
                    moves.append((_Old_GUI_Compatibility.old_engine_order.index(regular_move.card), None))

        finished = game_over
        phase = 1 if perspective.get_phase() == GamePhase.ONE else 2
        leads_turn = perspective.am_i_leader()
        # it is always the turn of the browser player!
        player1s_turn = True
        p1_points = perspective.get_my_score().direct_points
        p2_points = perspective.get_opponent_score().direct_points
        p1_pending = perspective.get_my_score().pending_points
        p2_pending = perspective.get_opponent_score().pending_points

        # TODO We removed the revoked indication. There is no comparable thing on the new platform.

        old_state = {"deck": deck, "moves": moves, "finished": finished, "won": won, "phase": phase,
                     "leads_turn": leads_turn, "player1s_turn": player1s_turn, "p1_points": p1_points, "p2_points": p2_points,
                     "p1_pending_points": p1_pending, "p2_pending_points": p2_pending}

        return dumps(old_state)
