from .state import State


# TODO: parameterize
def achieves(state: State) -> bool:
    return state.pots[1].oil_volume == 4
