import logging
from dataclasses import dataclass
from itertools import chain
from typing import Generator, List, Optional, Tuple

from .achievement import achieves
from .action import Action, available_actions
from .state import State


@dataclass(frozen=True)
class Development:
    final_state: State
    action_history: Tuple[Action, ...]

    @classmethod
    def initial(cls) -> "Development":
        return cls(State.initial(), ())

    def __post_init__(self):
        # NOTE: This assertion may be heavy specially.
        def simulated_final_state() -> State:
            state = None
            for _, state in self.replay():
                pass
            return state

        assert self.final_state == simulated_final_state()

    def __str__(self) -> str:
        action_history_str = (
            "[" + ", ".join(str(action) for action in self.action_history) + "]"
        )
        final_state_str = str(self.final_state)
        return action_history_str + "\n" + final_state_str

    def to_detailed_str(self) -> str:
        lines = []
        for action, state in self.replay():
            if action:
                lines.append(str(action))
            lines.append(str(state))
        return "\n".join(lines)

    def apply(self, action: Action) -> "Development":
        final_state = action(self.final_state)
        action_history = self.action_history + (action,)
        return Development(final_state, action_history)

    def replay(self) -> Generator[Tuple[Optional[Action], State], None, None]:
        state = State.initial()
        yield None, state
        for action in self.action_history:
            state = action(state)
            yield action, state

    def next_developments(self) -> List["Development"]:
        developments = (self.apply(action) for action in available_actions())
        return [d for d in developments if d.final_state != self.final_state]


def search() -> Optional[Development]:
    devs: List[Optional[Development]] = [None] * State.count()

    initial_dev = Development.initial()
    logging.debug(initial_dev)
    if achieves(initial_dev.final_state):
        return initial_dev
    devs[initial_dev.final_state.state_index] = initial_dev

    searched_devs = [initial_dev]
    while len(searched_devs) > 0:
        source_devs = searched_devs
        searched_devs = []

        for dev in chain.from_iterable(
            source_dev.next_developments() for source_dev in source_devs
        ):
            state_index = dev.final_state.state_index
            if devs[state_index]:
                continue

            logging.debug(dev)
            if achieves(dev.final_state):
                return dev

            devs[state_index] = dev
            searched_devs.append(dev)

    return None
