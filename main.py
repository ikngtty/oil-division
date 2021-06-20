import itertools
import logging


class Pot:
    def __init__(self, capacity, oil_volume):
        assert capacity >= 0
        assert oil_volume >= 0
        assert oil_volume <= capacity

        self.oil_volume = oil_volume
        self.capacity = capacity

    def __str__(self):
        return "■" * self.oil_volume + "□" * self.space

    @property
    def space(self):
        return self.capacity - self.oil_volume

    def add_oil(self, oil_volume_to_add):
        oil_volume = self.oil_volume + oil_volume_to_add
        assert oil_volume >= 0
        assert oil_volume <= self.capacity

        return Pot(self.capacity, oil_volume)


# TODO: parameterize
class Rule:
    INITIAL_POTS = [Pot(3, 0), Pot(5, 0), Pot(10, 10)]
    POT_COUNT = len(INITIAL_POTS)


class State:
    @classmethod
    def count(cls):
        count = 1
        for pot in Rule.INITIAL_POTS:
            count *= pot.capacity + 1
        return count

    @classmethod
    def initial(cls):
        return cls(Rule.INITIAL_POTS)

    def __init__(self, pots):
        assert len(pots) == len(Rule.INITIAL_POTS)
        for pot, initial_pot in zip(pots, Rule.INITIAL_POTS):
            assert pot.capacity == initial_pot.capacity

        self.pots = pots

    def __str__(self):
        return "\n".join(str(pot) for pot in self.pots)

    def __eq__(self, other):
        return self.state_index == other.state_index

    @property
    def state_index(self):
        index = 0
        base = 1
        for pot in self.pots:
            index += base * pot.oil_volume
            base *= pot.capacity
        return index


# TODO: parameterize
def achieves(state):
    return state.pots[1].oil_volume == 4


class OilMoveAction:
    def __init__(self, source_pot_index, dest_pot_index):
        assert source_pot_index >= 0
        assert source_pot_index < Rule.POT_COUNT
        assert dest_pot_index >= 0
        assert dest_pot_index < Rule.POT_COUNT

        self.source_pot_index = source_pot_index
        self.dest_pot_index = dest_pot_index

    def __call__(self, state):
        source_pot = state.pots[self.source_pot_index]
        dest_pot = state.pots[self.dest_pot_index]

        move_oil_volume = min(source_pot.oil_volume, dest_pot.space)

        oil_moved_pots = state.pots.copy()
        oil_moved_pots[self.source_pot_index] = source_pot.add_oil(-1 * move_oil_volume)
        oil_moved_pots[self.dest_pot_index] = dest_pot.add_oil(move_oil_volume)
        return State(oil_moved_pots)

    def __str__(self):
        return f"{self.source_pot_index}->{self.dest_pot_index}"


def available_actions():
    actions = []
    for source_pot_index in range(Rule.POT_COUNT):
        for dest_pot_index in range(Rule.POT_COUNT):
            if dest_pot_index == source_pot_index:
                continue
            actions.append(OilMoveAction(source_pot_index, dest_pot_index))
    return actions


class Development:
    @classmethod
    def initial(cls):
        return cls(State.initial(), [])

    def __init__(self, final_state, action_history):
        self.final_state = final_state
        self.action_history = action_history

    def __str__(self):
        action_history_str = (
            "[" + ", ".join(str(action) for action in self.action_history) + "]"
        )
        final_state_str = str(self.final_state)
        return action_history_str + "\n" + final_state_str

    def to_detailed_str(self):
        lines = []
        state = State.initial()
        lines.append(str(state))
        for action in self.action_history:
            lines.append(str(action))
            state = action(state)
            lines.append(str(state))
        return "\n".join(lines)

    def apply(self, action):
        final_state = action(self.final_state)
        action_history = self.action_history.copy()
        action_history.append(action)
        return Development(final_state, action_history)

    def next_developments(self):
        developments = (self.apply(action) for action in available_actions())
        return [d for d in developments if d.final_state != self.final_state]


def search():
    devs = [None] * State.count()

    initial_dev = Development.initial()
    logging.debug(initial_dev)
    if achieves(initial_dev.final_state):
        return initial_dev
    devs[initial_dev.final_state.state_index] = initial_dev

    searched_devs = [initial_dev]
    while len(searched_devs) > 0:
        source_devs = searched_devs
        searched_devs = []

        for dev in itertools.chain.from_iterable(
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


if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)
    achieved_development = search()
    if achieved_development:
        print(achieved_development.to_detailed_str())
    else:
        print("Not Found")
