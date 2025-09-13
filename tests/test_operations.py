from shared import (
    run_behaviour_in_aai,
    forwards_action,
    nothing_action,
    backwards_action,
)
import os


# Go through the datazone and collect a reward
def test_basic_datazone():
    run_behaviour_in_aai(
        os.path.join(".", "testConfigs", "testDatazone_spawnobject.yml"),
        0.8,
        lambda _: forwards_action,
    )


# Go through the datazone to end the episode
def test_datazone_endepisode():
    time_in_arena_decrement = -0.084
    operation_decrement = -0.5
    run_behaviour_in_aai(
        os.path.join(".", "testConfigs", "testDatazone_endepisode.yml"),
        time_in_arena_decrement + operation_decrement,
        lambda _: forwards_action,
    )
