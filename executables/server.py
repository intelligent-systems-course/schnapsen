import argparse
import random
from schnapsen.bots import SchnapsenServer
from schnapsen.bots import RandBot, AlphaBetaBot, RdeepBot
from schnapsen.game import SchnapsenGamePlayEngine


def main(bot: str) -> None:
    """Run the GUI.

    Args
    ----
    bot: RandBot, AlphaBetaBot, RdeepBot, MLDataBot, or MLPlayingBot

    """
    engine = SchnapsenGamePlayEngine()
    with SchnapsenServer() as s:
        if bot.lower() == "randbot":
            bot1 = RandBot(12)
        elif bot.lower() in ["alphabeta", "alphabetabot"]:
            bot1 = AlphaBetaBot()
        elif bot.lower() == "rdeepbot":
            bot1 = RdeepBot(num_samples=16, depth=4, rand=random.Random(42))
        else:
            raise NotImplementedError
        bot2 = s.make_gui_bot(name="mybot2")
        # bot1 = s.make_gui_bot(name="mybot1")
        engine.play_game(bot1, bot2, random.Random(100))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GUI")
    parser.add_argument(
        "-b",
        "--bot",
        default="RandBot",
        type=str,
        help="The bot you want to play against. Possible options are RandBot, "
        "AlphaBetaBot, RdeepBot, MLDataBot, or MLPlayingBot. The default is RandBot",
    )
    args = parser.parse_args()
    config = vars(args)
    print("Arguments:")
    for k, v in config.items():
        print(f"  {k:>21} : {v}")

    main(**config)
