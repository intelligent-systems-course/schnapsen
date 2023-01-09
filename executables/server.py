from schnapsen.bots.gui import SchnapsenServer
from schnapsen.bots.rand import RandBot
from schnapsen.game import SchnapsenGamePlayEngine
import random

if __name__ == "__main__":
    engine = SchnapsenGamePlayEngine()
    with SchnapsenServer() as s:
        bot1 = RandBot(12)
        bot2 = s.make_gui_bot(name="mybot2")
        # bot1 = s.make_gui_bot(name="mybot1")
        engine.play_game(bot1, bot2, random.Random(100))
