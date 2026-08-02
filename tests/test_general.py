from shared import (
    get_aai_env,
    run_behaviour_in_aai,
    forwards_action,
    nothing_action,
    backwards_action,
)
import numpy as np
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


# The agent's freeze (frozenAgentDelays) must not leak from one arena into the next.
# In arena 0 the agent is frozen for longer than the arena lasts and the episode is
# ended, mid-freeze, by a GoodGoal dropped onto it. Arena 1 freezes the agent only
# briefly, so the agent must be able to move again and reach its goal.
def test_should_not_stay_frozen_in_next_arena_if_episode_ends_while_frozen():
    # The goal takes ~15 steps to fall onto the agent. This budget must stay below arena
    # 0's frozenAgentDelays (3s == 30 steps) so that the episode is guaranteed to end
    # while the agent is still frozen, which is the case under test.
    ARENA_0_MAX_STEPS = 25
    ARENA_1_MAX_STEPS = 100  # frozenAgentDelays: [0.2] is ~2 steps, then ~5m to travel
    MOVED_DISTANCE = 0.5

    config = os.path.join(".", "testConfigs", "testFrozenAgentAcrossArenas.yml")
    behavior, dec, term, env = get_aai_env(config)

    def position():
        return np.array(env.get_obs_dict(dec.obs)["position"])

    try:
        # Arena 0: the agent is frozen, so it should not move while we wait for the
        # falling goal to end the episode.
        frozen_position = position()
        steps = 0
        while len(term) == 0 and steps < ARENA_0_MAX_STEPS:
            env.set_actions(behavior, forwards_action)
            env.step()
            dec, term = env.get_steps(behavior)
            steps += 1
            if len(dec) > 0:
                assert (
                    np.linalg.norm(position() - frozen_position) < MOVED_DISTANCE
                ), "Agent moved in the first arena despite frozenAgentDelays being set"
        assert (
            len(term) > 0
        ), f"First arena did not end within {ARENA_0_MAX_STEPS} steps, so the freeze was never interrupted"

        # Arena 1: the short freeze should expire and the agent should get moving again
        env.step()
        dec, term = env.get_steps(behavior)
        start_position = position()
        moved = False
        for _ in range(ARENA_1_MAX_STEPS):
            env.set_actions(behavior, forwards_action)
            env.step()
            dec, term = env.get_steps(behavior)
            if len(term) > 0:
                moved = True  # Reaching the goal is only possible by moving
                break
            if np.linalg.norm(position() - start_position) > MOVED_DISTANCE:
                moved = True
                break
        assert (
            moved
        ), f"Agent never moved in the second arena within {ARENA_1_MAX_STEPS} steps - the freeze from the first arena persisted across the episode boundary"
    finally:
        env.close()
