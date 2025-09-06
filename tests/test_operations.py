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
