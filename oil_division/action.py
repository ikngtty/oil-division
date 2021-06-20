from dataclasses import dataclass
from typing import Callable, List

from .state import Rule, State

Action = Callable[[State], State]


@dataclass(frozen=True)
class OilMoveAction:
    source_pot_index: int
    dest_pot_index: int

    def __post_init__(self) -> None:
        assert self.source_pot_index >= 0
        assert self.source_pot_index < Rule.POT_COUNT
        assert self.dest_pot_index >= 0
        assert self.dest_pot_index < Rule.POT_COUNT

    def __call__(self, state: State) -> State:
        source_pot = state.pots[self.source_pot_index]
        dest_pot = state.pots[self.dest_pot_index]

        move_oil_volume = min(source_pot.oil_volume, dest_pot.space)

        oil_moved_pots = list(state.pots)
        oil_moved_pots[self.source_pot_index] = source_pot.add_oil(-1 * move_oil_volume)
        oil_moved_pots[self.dest_pot_index] = dest_pot.add_oil(move_oil_volume)
        return State(tuple(oil_moved_pots))

    def __str__(self) -> str:
        return f"{self.source_pot_index}->{self.dest_pot_index}"


def available_actions() -> List[Action]:
    actions: List[Action] = []
    for source_pot_index in range(Rule.POT_COUNT):
        for dest_pot_index in range(Rule.POT_COUNT):
            if dest_pot_index == source_pot_index:
                continue
            actions.append(OilMoveAction(source_pot_index, dest_pot_index))
    return actions
