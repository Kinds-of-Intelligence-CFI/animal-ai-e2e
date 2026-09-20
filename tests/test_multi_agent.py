from shared import TOTAL_RAYS, get_aai_env
import numpy as np
import os
import time
from animalai.raycastparser import RayCastObjects, RayCastParser
from mlagents_envs.base_env import ActionTuple
from PIL import Image

"""
Tests for arenas with more than one agent.

Agents are identified by where they spawned rather than by row: ML-Agents returns one row per agent,
ordered by agent_id, and doesn't promise that follows the order of the Agent items in the YAML.

TODO: Add a test that agents on different teams (`teams: [1]` on an Agent item) get separate
behaviors, `AnimalAI?team=0` and `AnimalAI?team=1`.
"""

CONFIG = os.path.join(".", "testConfigs", "testMultiAgent.yml")

# Spawn points (x, z) from the config. Agent 0 faces +x, agent 1 faces -x, so they face each other.
AGENT_0_SPAWN = np.array([10.0, 20.0])
AGENT_1_SPAWN = np.array([30.0, 20.0])
SPAWN_TOLERANCE = 0.5

# parse() returns each object's ray distances left to right, so the middle ray is in the centre
MIDDLE_RAY = (TOTAL_RAYS - 1) // 2

MAX_STEPS = 150


def _obs_by_agent(env, steps) -> dict:
    """agent_id -> that agent's observation dictionary (camera, rays, health, velocity, position)."""
    return dict(zip(steps.agent_id, env.get_obs_dicts(steps.obs)))


def _horizontal_positions(env, steps) -> dict:
    """agent_id -> (x, z) world position."""
    return {agent_id: obs["position"][[0, 2]] for agent_id, obs in _obs_by_agent(env, steps).items()}


def _identify_agents(env, steps) -> tuple:
    """Returns (agent 0's id, agent 1's id), matched by distance to their spawn points."""
    positions = _horizontal_positions(env, steps)
    agent_0 = min(positions, key=lambda i: np.linalg.norm(positions[i] - AGENT_0_SPAWN))
    agent_1 = min(positions, key=lambda i: np.linalg.norm(positions[i] - AGENT_1_SPAWN))
    assert agent_0 != agent_1, f"Could not tell the agents apart by position: {positions}"
    return agent_0, agent_1


def _actions(steps, action_by_agent: dict) -> np.ndarray:
    """One discrete action row per agent, in the order of steps.agent_id."""
    return np.array([action_by_agent[agent_id] for agent_id in steps.agent_id], dtype=np.int32)


FORWARDS = [1, 0]
BACKWARDS = [2, 0]
NOTHING = [0, 0]


def _save_camera_views(env, steps, agent_names: dict) -> None:
    """Saves each agent's camera observation as a PNG, so what every agent sees can be inspected."""
    dump_dir = "multi_agent_watch"
    os.makedirs(dump_dir, exist_ok=True)
    for agent_id, obs in _obs_by_agent(env, steps).items():
        frame = obs["camera"]
        # Unity outputs (C, H, W) in [0, 1]; Image expects (H, W, C) bytes
        image = Image.fromarray(np.array(np.transpose(frame, (1, 2, 0)) * 255, dtype=np.uint8))
        path = os.path.join(dump_dir, f"{agent_names[agent_id]}_first_frame.png")
        image.save(path)
        print(f"Saved {path}")


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
        # 1. Both agents exist, share one behavior, and spawned where the config put them
        assert list(env.behavior_specs.keys()) == [
            "AnimalAI?team=0"
        ], f"Expected one shared behavior, got {list(env.behavior_specs.keys())}"
        assert len(dec) == 2, f"Expected 2 agents to request decisions, got {len(dec)}"
        assert len(set(dec.agent_id)) == 2, f"Expected 2 distinct agent ids, got {dec.agent_id}"

        agent_0, agent_1 = _identify_agents(env, dec)
        positions = _horizontal_positions(env, dec)
        for agent_id, spawn in ((agent_0, AGENT_0_SPAWN), (agent_1, AGENT_1_SPAWN)):
            assert (
                np.linalg.norm(positions[agent_id] - spawn) < SPAWN_TOLERANCE
            ), f"Agent {agent_id} is at {positions[agent_id]}, expected its spawn point {spawn}"

        if watch:
            _save_camera_views(env, dec, {agent_0: "agent_0", agent_1: "agent_1"})

        # 2. Each agent's middle ray hits the other agent
        parser = RayCastParser([RayCastObjects.AGENT], TOTAL_RAYS)
        for agent_id, obs in _obs_by_agent(env, dec).items():
            agent_distances = parser.parse(obs["rays"])[0]
            assert (
                agent_distances[MIDDLE_RAY] > 0
            ), f"Agent {agent_id}'s middle ray should see the other agent, got {agent_distances}"

        # 3. Actions reach the right agent: agent 0 reverses (towards the goal behind it) while
        # agent 1 stays still. 4. When agent 0 collects the goal, both agents' episodes end in
        # the same step.
        start = _horizontal_positions(env, dec)
        last_positions = start
        rewards = {agent_0: 0.0, agent_1: 0.0}
        action_by_agent = {agent_0: BACKWARDS, agent_1: NOTHING}
        for _ in range(MAX_STEPS):
            env.set_actions(behavior, ActionTuple(discrete=_actions(dec, action_by_agent)))
            env.step()
            dec, term = env.get_steps(behavior)
            if len(term) > 0:
                # Any decision steps now belong to the next episode
                break
            for agent_id, reward in zip(dec.agent_id, dec.reward):
                rewards[agent_id] += reward
            last_positions = _horizontal_positions(env, dec)

        assert len(term) > 0, f"The episode didn't end within {MAX_STEPS} steps"

        agent_0_moved = np.linalg.norm(last_positions[agent_0] - start[agent_0])
        agent_1_moved = np.linalg.norm(last_positions[agent_1] - start[agent_1])
        assert agent_0_moved > 0.5, f"Agent 0 was told to reverse but only moved {agent_0_moved}m"
        assert agent_1_moved < 0.1, f"Agent 1 was told to stay still but moved {agent_1_moved}m"

        assert set(term.agent_id) == {
            agent_0,
            agent_1,
        }, f"Both agents' episodes should end in the same step, but only {term.agent_id} ended"
        for agent_id, reward in zip(term.agent_id, term.reward):
            rewards[agent_id] += reward
        assert rewards[agent_0] > 0.5, f"Agent 0 collected the goal but its reward is {rewards[agent_0]}"
        assert rewards[agent_1] < 0, f"Agent 1 only paid the time penalty but its reward is {rewards[agent_1]}"
    finally:
        if watch:
            time.sleep(3)  # Leave the window up long enough to see the end of the episode
        env.close()
