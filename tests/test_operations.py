from shared import (
    run_behaviour_in_aai,
    forwards_action,
    nothing_action,
    backwards_action,
)
import os


# Go through the datazone and collect a reward
def test_toggle_basic_datazone():
    run_behaviour_in_aai(
        os.path.join(".", "testConfigs", "testDatazone_spawnobject.yml"),
        0.8,
        lambda _: forwards_action,
    )


# Go through the datazone once to spawn the reward, again to despawn
def test_toggle_twice_datazone():
    run_behaviour_in_aai(
        os.path.join(".", "testConfigs", "testDatazone_spawnobject_despawnobject.yml"),
        -1.3,
        lambda r: (
            (forwards_action if r < -0.175 else backwards_action)
            if r < -0.1
            else forwards_action
        ),
        watch=True,
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


# Go through the datazone and get frozen on the way
def test_datazone_freezeAgent():
    run_behaviour_in_aai(
        os.path.join(".", "testConfigs", "testDatazone_freezeAgent.yml"),
        0.327,
        lambda _: forwards_action,
    )
