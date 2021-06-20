from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Pot:
    capacity: int
    oil_volume: int

    def __post_init__(self) -> None:
        assert self.capacity >= 0
        assert self.oil_volume >= 0
        assert self.oil_volume <= self.capacity

    def __str__(self) -> str:
        return "■" * self.oil_volume + "□" * self.space

    @property
    def space(self) -> int:
        return self.capacity - self.oil_volume

    def add_oil(self, oil_volume_to_add: int) -> "Pot":
        oil_volume = self.oil_volume + oil_volume_to_add
        assert oil_volume >= 0
        assert oil_volume <= self.capacity

        return Pot(self.capacity, oil_volume)


# TODO: parameterize
class Rule:
    INITIAL_POTS = (Pot(3, 0), Pot(5, 0), Pot(10, 10))
    POT_COUNT = len(INITIAL_POTS)
    TOTAL_OIL_VOLUME = sum(pot.oil_volume for pot in INITIAL_POTS)


@dataclass(frozen=True)
class State:
    pots: Tuple[Pot, ...]

    # HACK: Impossible states, in which total oil volume is changed,
    # are included.
    @classmethod
    def count(cls) -> int:
        count = 1
        for pot in Rule.INITIAL_POTS:
            count *= pot.capacity + 1
        return count

    @classmethod
    def initial(cls) -> "State":
        return cls(Rule.INITIAL_POTS)

    def __post_init__(self) -> None:
        assert len(self.pots) == len(Rule.INITIAL_POTS)
        for pot, initial_pot in zip(self.pots, Rule.INITIAL_POTS):
            assert pot.capacity == initial_pot.capacity
        assert sum(pot.oil_volume for pot in self.pots) == Rule.TOTAL_OIL_VOLUME

    def __str__(self) -> str:
        return "\n".join(str(pot) for pot in self.pots)

    # HACK: Impossible states, in which total oil volume is changed,
    # are included.
    @property
    def state_index(self) -> int:
        index = 0
        base = 1
        for pot in self.pots:
            index += base * pot.oil_volume
            base *= pot.capacity
        return index
