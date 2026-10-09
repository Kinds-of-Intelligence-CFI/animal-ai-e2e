from shared import TOTAL_RAYS, get_aai_env
import numpy as np
import os
import time
from animalai.raycastparser import RayCastObjects, RayCastParser
from mlagents_envs.base_env import ActionTuple
from PIL import Image

"""
Tests for arenas with more than one agent.

ML-Agents returns one row per agent, and Animal-AI keeps the rows in the order of the Agent items in the
YAML, so row k is agent k (the agent_ids themselves change when an agent sits out an arena, so the tests
don't use them to identify agents). The row-order test checks that promise across arenas where agents sit
out and come back, and the teams test checks it holds within each team's behavior; the other tests rely
on it.
"""

CONFIG = os.path.join(".", "testConfigs", "testMultiAgent.yml")
ROW_ORDER_CONFIG = os.path.join(".", "testConfigs", "testAgentRowOrder.yml")
TEAMS_CONFIG = os.path.join(".", "testConfigs", "testAgentTeams.yml")

# Spawn points (x, z) from the config. Agent 0 faces +x, agent 1 faces -x, so they face each other.
AGENT_0_SPAWN = np.array([10.0, 20.0])
AGENT_1_SPAWN = np.array([30.0, 20.0])
SPAWN_TOLERANCE = 0.5

# parse() returns each object's ray distances left to right, so the middle ray is in the centre
MIDDLE_RAY = (TOTAL_RAYS - 1) // 2

MAX_STEPS = 150


def _horizontal_positions(env, steps) -> list:
    """Each agent's (x, z) world position, in row (YAML) order."""
    return [obs["position"][[0, 2]] for obs in env.get_obs_dicts(steps.obs)]


FORWARDS = [1, 0]
BACKWARDS = [2, 0]
NOTHING = [0, 0]


def _save_camera_views(env, steps) -> None:
    """Saves each agent's camera observation as a PNG, so what every agent sees can be inspected."""
    dump_dir = "multi_agent_watch"
    os.makedirs(dump_dir, exist_ok=True)
    for k, obs in enumerate(env.get_obs_dicts(steps.obs)):
        frame = obs["camera"]
        # Unity outputs (C, H, W) in [0, 1]; Image expects (H, W, C) bytes
        image = Image.fromarray(np.array(np.transpose(frame, (1, 2, 0)) * 255, dtype=np.uint8))
        path = os.path.join(dump_dir, f"agent_{k}_first_frame.png")
        image.save(path)
        print(f"Saved {path}")


def _yaml_indices(env, steps) -> list:
    """Each row's Agent item index, from its spawn position (agent k spawns at x = 4 + 6k)."""
    return [round((obs["position"][0] - 4) / 6) for obs in env.get_obs_dicts(steps.obs)]


def _reset_to_next_arena(env, behaviors) -> dict:
    """Resets (Unity moves to the next arena) and returns each behavior's decision steps.

    When agents sit out the new arena, the first batch after the reset only holds their terminal rows; the
    remaining agents' rows arrive on the next step.
    """
    env.reset()
    decisions = {behavior: env.get_steps(behavior)[0] for behavior in behaviors}
    if any(len(steps) == 0 for steps in decisions.values()):
        env.step()
        decisions = {behavior: env.get_steps(behavior)[0] for behavior in behaviors}
    return decisions


def test_rows_follow_yaml_agent_order_as_agents_sit_out_and_return():
    behavior, dec, _, env = get_aai_env(ROW_ORDER_CONFIG)
    try:
        ids_by_arena = []
        for arena, agent_count in enumerate((3, 1, 2, 4)):
            if arena > 0:
                dec = _reset_to_next_arena(env, [behavior])[behavior]
            assert _yaml_indices(env, dec) == list(range(agent_count)), (
                f"Arena {arena}: rows should be Agent items 0..{agent_count - 1} in YAML order, "
                f"got {_yaml_indices(env, dec)} (agent_ids {list(dec.agent_id)})"
            )
            ids_by_arena.append(list(dec.agent_id))

        # Agent 0 never sits out, so it keeps its agent_id; agent 1 sat out arena 1, so it came back with a new one
        assert len({ids[0] for ids in ids_by_arena}) == 1, f"Agent 0's agent_id changed: {ids_by_arena}"
        assert ids_by_arena[2][1] != ids_by_arena[0][1], f"Agent 1 kept its agent_id after sitting out: {ids_by_arena}"
    finally:
        env.close()


def test_each_team_gets_its_own_behavior_with_rows_in_yaml_order():
    _, _, _, env = get_aai_env(TEAMS_CONFIG)
    try:
        team_0, team_1 = "AnimalAI?team=0", "AnimalAI?team=1"
        assert sorted(env.behavior_specs) == [team_0, team_1], (
            f"Expected one behavior per team, got {list(env.behavior_specs)}"
        )
        # Even Agent items are on team 0, odd ones on team 1. Agents 2 and 3 sit out arena 1, and the reset
        # into arena 2 brings them back in the same step as it creates agents 4 and 5
        expected_by_arena = (
            {team_0: [0, 2], team_1: [1, 3]},
            {team_0: [0], team_1: [1]},
            {team_0: [0, 2, 4], team_1: [1, 3, 5]},
        )
        for arena, expected in enumerate(expected_by_arena):
            if arena == 0:
                decisions = {behavior: env.get_steps(behavior)[0] for behavior in expected}
            else:
                decisions = _reset_to_next_arena(env, expected)
            rows = {behavior: _yaml_indices(env, steps) for behavior, steps in decisions.items()}
            assert rows == expected, (
                f"Arena {arena}: each team's rows should be its Agent items in YAML order, got {rows}"
            )
    finally:
        env.close()


def test_two_agents_spawn_see_each_other_act_independently_and_end_the_episode_together():
    run_two_agent_test()


def run_two_agent_test(watch: bool = False) -> None:
    """
    With watch=True the environment runs in real time with graphics, and each agent's first camera frame
    is saved under multi_agent_watch/ (the window only shows the primary agent's view).
    """
    behavior, dec, term, env = (
        get_aai_env(CONFIG)
        if not watch
        else get_aai_env(CONFIG, no_graphics=False, use_Camera=True, timescale=1)
    )
    try:
        # 1. Both agents exist, share one behavior, and spawned where the config put them. Row k is the
        # k-th Agent item, so this also checks the rows are in YAML order.
        assert list(env.behavior_specs.keys()) == [
            "AnimalAI?team=0"
        ], f"Expected one shared behavior, got {list(env.behavior_specs.keys())}"
        assert len(dec) == 2, f"Expected 2 agents to request decisions, got {len(dec)}"

        positions = _horizontal_positions(env, dec)
        for k, spawn in enumerate((AGENT_0_SPAWN, AGENT_1_SPAWN)):
            assert (
                np.linalg.norm(positions[k] - spawn) < SPAWN_TOLERANCE
            ), f"Row {k} is at {positions[k]}, expected agent {k}'s spawn point {spawn}"

        if watch:
            _save_camera_views(env, dec)

        # 2. Each agent's middle ray hits the other agent
        parser = RayCastParser([RayCastObjects.AGENT], TOTAL_RAYS)
        for k, obs in enumerate(env.get_obs_dicts(dec.obs)):
            agent_distances = parser.parse(obs["rays"])[0]
            assert (
                agent_distances[MIDDLE_RAY] > 0
            ), f"Agent {k}'s middle ray should see the other agent, got {agent_distances}"

        # 3. Actions reach the right agent: agent 0 reverses (towards the goal behind it) while
        # agent 1 stays still. 4. When agent 0 collects the goal, both agents' episodes end in
        # the same step.
        start = _horizontal_positions(env, dec)
        last_positions = start
        rewards = np.zeros(2)
        actions = np.array([BACKWARDS, NOTHING], dtype=np.int32)  # one row per agent, in row order
        for _ in range(MAX_STEPS):
            env.set_actions(behavior, ActionTuple(discrete=actions))
            env.step()
            dec, term = env.get_steps(behavior)
            if len(term) > 0:
                # Any decision steps now belong to the next episode
                break
            rewards += dec.reward
            last_positions = _horizontal_positions(env, dec)

        assert len(term) > 0, f"The episode didn't end within {MAX_STEPS} steps"

        agent_0_moved = np.linalg.norm(last_positions[0] - start[0])
        agent_1_moved = np.linalg.norm(last_positions[1] - start[1])
        assert agent_0_moved > 0.5, f"Agent 0 was told to reverse but only moved {agent_0_moved}m"
        assert agent_1_moved < 0.1, f"Agent 1 was told to stay still but moved {agent_1_moved}m"

        assert len(term) == 2, f"Both agents' episodes should end in the same step, but only {len(term)} ended"
        rewards += term.reward
        assert rewards[0] > 0.5, f"Agent 0 collected the goal but its reward is {rewards[0]}"
        assert rewards[1] < 0, f"Agent 1 only paid the time penalty but its reward is {rewards[1]}"
    finally:
        if watch:
            time.sleep(3)  # Leave the window up long enough to see the end of the episode
        env.close()
