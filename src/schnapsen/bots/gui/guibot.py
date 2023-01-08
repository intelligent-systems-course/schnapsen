from schnapsen.game import Bot, PlayerGameState, PartialTrick, Move, Suit, RegularTrick, SchnapsenDeckGenerator, GamePhase, Hand
from schnapsen.deck import Card
from typing import Optional, cast, Tuple
from flask import Flask, render_template, abort
from json import dumps
from schnapsen.bots.rand import RandBot
from threading import Thread, Lock
import uuid
from dataclasses import dataclass, field

import signal
import time


class GUIBot(Bot):

    def __init__(self, name: str, server: 'SchnapsenServer') -> None:
        self.name = name
        self.server = server

    def get_move(self, state: PlayerGameState, leader_move: Optional[PartialTrick]) -> Move:
        return self.server.get_move(self.name, state, leader_move)


@dataclass
class _StateExchange:
    l: Lock
    state: PlayerGameState
    move: Move


class SchnapsenServer:

    def __enter__(self) -> 'SchnapsenServer':
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        # self.process.terminate()
        if exc_value:
            print("Closing the server, because an Exception was raised")
            # by not returning True, we indicate that the exception was not handled.
        else:
            print("Server closed")
        # self.process.terminate()
        # self.process.join()

        # print(exc_type, exc_value, exc_tb, sep="\n")

    def __init__(self, host_name="0.0.0.0", port=8080) -> None:
        """Creates and starts the schnapsen server"""
        self.host_name = host_name
        self.port = port
        self.bots: dict[str, Tuple[Bot, bool]] = {}
        app = Flask(__name__, template_folder='template')
        app.config.update(
            PROPAGATE_EXCEPTIONS=True
        )
        self._setup_routes(app)
        self.process = Thread(target=app.run, kwargs={"host": host_name, "port": port, "use_reloader": False, "debug": True})
        print(f"Starting the server on {self.host_name}:{self.port}")
        self.process.start()
    # def register(self, name: str, bot: Bot):
    #     print(f"Registering bot {name}")
    #     self.bots[name] = bot
    #     print(self.bots)

    def make_gui_bot(self, name: str) -> Bot:
        bot = GUIBot(name, self)
        self.bots[name] = (bot, False)
        return bot

    def get_move(self, botname: str, state: PlayerGameState, leader_move: Optional[PartialTrick]) -> Move:
        pass

    # def start(self):
     #
        # self.stop = False

        # def handler(signum, frame):
        #     print("\nCtrl-c was pressed, quiting the server.")
        #     self.stop = True
        #     self.process.terminate()
        #     self.process.join()
        # signal.signal(signal.SIGINT, handler)
        # while not self.stop:
        #     time.sleep(0.5)

    def _setup_routes(self, app):
        app.route('/', methods=['GET'])(self.index)
#        app.route('/startgame/<botname>/', methods=['GET'])(self.startgame)
        app.route('/game/<botname>', methods=['GET'])(self.game)
        app.route('/generate/<botname>', methods=['GET'])(self.generate)

    def index(self):
        bots = [(botname, started) for botname, (_, started) in self.bots.items()]
        return render_template("gamechooser.html", bots=bots)

    # def startgame(self, botname: str):
    #     print(f"Starting game with {botname}")
    #     bot = self.bots[botname]
    #     return redirect(f"/game/{botname}", 302)

    def game(self, botname: str):
        if self.bots[botname][1]:
            return abort(409, "This game has already started")

        self.bots[botname] = (self.bots[botname][0], True)
        return render_template("index_interactive.html", botname=botname)

    def generate(self, game_id):
        global state
        # Use 3 for marriage, 50 for exchange
        state = State.generate(id=options.seed, phase=options.phase)
        return state.convert_to_json()  # [:-1] + ', "seed": ' + str(id) + '}')


def player_game_state_to_json(state: PlayerGameState, leader_move: Optional[PartialTrick]) -> str:

    # Deck.convert_to_json
    # return {"card_state":self.__card_state, "p1_perspective":self.__p1_perspective,
    # "p2_perspective":self.__p2_perspective, "trick":self.__trick,
    # "previous_trick":self.__previous_trick, "stock":self.__stock,
    # "trump_suit":self.__trump_suit, "signature":self.__signature}

    # We do not add p2_perspective since it is never used on the client side, we also do not have the information for it
    # We do not incluide the trick explicitly. This anyway gets conveted into P1D and P2D in  card_state, so we do it at once
    # We leave out stock, because it can be derived from card_state
    #

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

    hand = state.get_hand()
    talon_size = state.get_talon_size()
    trump_card = state.get_trump_card()
    trump_suit = state.get_trump_suit()
    won_cards = state.get_won_cards()
    opponent_won_cards = state.get_opponent_won_cards()

    opponent_known_cards = state.get_known_cards_of_opponent_hand()

    partial_move_cards = leader_move.leader_move.cards if leader_move else None
    partial_move_down = leader_move.leader_move.as_regular_move().card if leader_move else None

    card_state: list[str] = ["None"] * 20
    p1_perspective: list[str] = ["None"] * 20

    invisible_on_stack = talon_size - 1

    for index, card in enumerate(old_engine_order):
        this_card_state: str
        this_p1_perspective: str
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

        card_state[index] = this_card_state
        p1_perspective[index] = this_p1_perspective

    # previous trick
    old_shape_previous_trick: list[int] = [-1, -1]
    history = state.get_game_history()
    if len(history > 1):
        previous_trick = history[-2][1]

        if previous_trick.is_trump_exchange():
            # ignore because the old platform does not deal with this.
            pass
        else:
            previous_regular_trick = cast(RegularTrick, previous_trick)
            # we only care about the cards which will go, not marriage
            leadercard = previous_regular_trick.leader_move.as_regular_move().card
            followercard = previous_regular_trick.follower_move.card

            old_shape_previous_trick[0] = old_engine_order.index(leadercard)
            old_shape_previous_trick[1] = old_engine_order.index(followercard)

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

    deck = {
        "card_state": card_state,
        "p1_perspective": p1_perspective,
        "previous_trick": old_shape_previous_trick,
        "trump_suit": old_trump_suit
    }

    # mimcking the old one, leaving some thigns out
    # return dumps({"deck":self.__deck.convert_to_json(), "moves":self.moves(), "finished":self.finished(), "phase":self.__phase,
    # "leads_turn":self.__leads_turn, "player1s_turn":self.__player1s_turn, "p1_points":self.__p1_points, "p2_points":self.__p2_points,
    # "p1_pending_points":self.__p1_pending_points, "p2_pending_points":self.__p2_pending_points, "signature":self.__signature, "revoked":self.__revoked})

    # TODO
    # moves (legalmoves)
    raise NotImplementedError()

    assert not any(map(lambda x: x == "None", card_state))
    assert not any(map(lambda x: x == "None", p1_perspective))
