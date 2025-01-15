import random
from schnapsen.bots import SchnapsenServer
from schnapsen.bots import RandBot
from schnapsen.game import SchnapsenGamePlayEngine


if __name__ == "__main__":
    engine = SchnapsenGamePlayEngine()
    with SchnapsenServer() as s:
        bot1 = RandBot(random.Random(12))
        # bot1 = s.make_gui_bot(name="mybot1")
        bot2 = s.make_gui_bot(name="mybot2")
        engine.play_game(bot1, bot2, random.Random(100))
