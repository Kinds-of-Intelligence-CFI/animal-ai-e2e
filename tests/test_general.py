from shared import run_behaviour_in_aai, forwards_action, nothing_action
import os

"""
Tests that the basic behaviour of the AI works - i.e. it can move forward and stop.
"""
def test_basic_success():
    run_behaviour_in_aai(
        os.path.join(".", "testConfigs", "testUnmergedArenas.yml"),
        0.8,
        lambda _ : forwards_action
    )

def test_basic_fail():
    run_behaviour_in_aai(
        os.path.join(".", "testConfigs", "testUnmergedArenas.yml"),
        -1,
        lambda _ : nothing_action,
    )
