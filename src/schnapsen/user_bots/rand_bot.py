import schnapsen.api
from schnapsen.api import Card, PlayerGameState


@schnapsen.api.Bot(bot_name="Random bot", bot_id="rand")
class RandBot():
    def __init__(self, seed: int) -> None:
        pass

    def get_move(self, state: PlayerGameState) -> Card:
        pass

    # # alternative

    # def get_first_move(self, state: FirstMoveState):
    #     pass

    # def get_second_move(self, state: SecondMoveState):
    #     pass

    # # or even

    # def get_first_move_phase_one(self, state: FirstMoveState):
    #     pass

    # def get_second_move_phase_one(self, state: SecondMoveState):
    #     pass

    # def get_first_move_phase_two(self, state: FirstMoveState):
    #     pass

    # def get_second_move_phase_two(self, state: SecondMoveState):
    #     pass
