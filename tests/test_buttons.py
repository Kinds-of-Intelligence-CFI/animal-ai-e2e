from shared import (
    run_behaviour_in_aai,
    forwards_action,
    nothing_action,
    backwards_action,
)
import os

"""
Tests that the button works
"""


def test_button_basic():
    run_behaviour_in_aai(
        os.path.join(".", "testConfigs", "testButtons.yml"),
        0.8,
        lambda r: backwards_action if r < -0.2 else forwards_action,
        watch=True,
    )


def test_button_legacy():
    run_behaviour_in_aai(
        os.path.join(".", "testConfigs", "testButtonsLegacy.yml"),
        0.8,
        lambda r: backwards_action if r < -0.2 else forwards_action,
        watch=True,
    )
