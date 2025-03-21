from shared import (
    run_behaviour_in_aai,
    forwards_action,
    nothing_action,
    backwards_action,
)
import os

"""
Tests that the basic behaviour of the AI works - i.e. it can move forward and stop.
"""


def test_basic_success():
    run_behaviour_in_aai(
        os.path.join(".", "testConfigs", "testUnmergedArenas.yml"),
        0.8,
        lambda _: forwards_action,
    )


def test_basic_fail():
    run_behaviour_in_aai(
        os.path.join(".", "testConfigs", "testUnmergedArenas.yml"),
        -1,
        lambda _: nothing_action,
    )


def test_multi_reward():
    stage = 0

    def multi_reward_behaviour(reward: float):
        nonlocal stage
        # Stage 0: Experiment has started and agent is approaching the multi goal
        # Stage 1: Agent has retrieved the multi goal, going forwards a bit to check it was removed
        # Stage 2: Agent is going backwards to check that the reward was removed
        # Stage 3: Agent is going forwards to get the final goal
        stage_thresholds = [(0, True), (0.95, False), (0.9, False), (-2, False)]
        threshold, increment_if_above = stage_thresholds[stage]
        if increment_if_above:
            if reward > threshold:
                stage += 1
        else:
            if reward < threshold:
                stage += 1
        return forwards_action if stage in [0, 1, 3] else backwards_action

    run_behaviour_in_aai(
        os.path.join(".", "testConfigs", "testMultiReward.yml"),
        1.8200004,
        multi_reward_behaviour,
    )
