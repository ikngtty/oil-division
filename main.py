import itertools
import logging


class Rule:
    POT_CAPACITIES = [3, 5, 10]  # TODO: parameterize
    POT_COUNT = len(POT_CAPACITIES)


class State:
    @classmethod
    def count(cls):
        count = 1
        for capacity in Rule.POT_CAPACITIES:
            count *= capacity + 1
        return count

    # TODO: parameterize
    @classmethod
    def initial(cls):
        return cls([0, 0, 10])

    def __init__(self, oil_volumes):
        assert len(oil_volumes) == Rule.POT_COUNT
        for volume, capacity in zip(oil_volumes, Rule.POT_CAPACITIES):
            assert volume <= capacity

        self.oil_volumes = oil_volumes

    def __str__(self):
        return "\n".join(
            "■" * volume + "□" * (capacity - volume)
            for volume, capacity in zip(self.oil_volumes, Rule.POT_CAPACITIES)
        )

    def __eq__(self, other):
        return self.state_index == other.state_index

    @property
    def state_index(self):
        index = 0
        base = 1
        for volume, capacity in zip(self.oil_volumes, Rule.POT_CAPACITIES):
            index += base * volume
            base *= capacity
        return index

    def space_of_pot(self, index):
        assert index >= 0
        assert index < Rule.POT_COUNT

        return Rule.POT_CAPACITIES[index] - self.oil_volumes[index]


# TODO: parameterize
def state_is_achieved(state):
    return state.oil_volumes[1] == 4


class OilMoveAction:
    def __init__(self, source_pot_index, dest_pot_index):
        assert source_pot_index >= 0
        assert source_pot_index < Rule.POT_COUNT
        assert dest_pot_index >= 0
        assert dest_pot_index < Rule.POT_COUNT

        self.source_pot_index = source_pot_index
        self.dest_pot_index = dest_pot_index

    def __call__(self, state):
        oil_volume = state.oil_volumes[self.source_pot_index]
        space = state.space_of_pot(self.dest_pot_index)
        move_oil_volume = min(oil_volume, space)

        moved_oil_volumes = state.oil_volumes.copy()
        moved_oil_volumes[self.source_pot_index] -= move_oil_volume
        moved_oil_volumes[self.dest_pot_index] += move_oil_volume
        return State(moved_oil_volumes)

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
    if state_is_achieved(initial_dev.final_state):
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
            if state_is_achieved(dev.final_state):
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
