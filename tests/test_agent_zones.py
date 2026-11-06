from shared import get_aai_env
import numpy as np
import os
from mlagents_envs.base_env import ActionTuple

"""
Tests for agent zones: operations attached to an agent with a radius, which run on any other agent
that comes within it (see the Multi-Agent Guide, "Agent zones").

Every config has two agents on one behavior. Row k is Agent item k (see test_multi_agent.py), so
row 0 is the agent carrying the zone ("mother" or "predator") and row 1 is the agent walking into
it ("infant" or "prey").
"""

REWARD_CONFIG = os.path.join(".", "testConfigs", "testAgentZone_reward.yml")
END_EPISODE_CONFIG = os.path.join(".", "testConfigs", "testAgentZone_endEpisode.yml")
WALL_CONFIG = os.path.join(".", "testConfigs", "testAgentZone_wall.yml")
SPAWN_CONFIG = os.path.join(".", "testConfigs", "testAgentZone_spawn.yml")

OWNER, VISITOR = 0, 1

FORWARDS = [1, 0]
NOTHING = [0, 0]
# The owner stays still, the visitor walks forwards (towards the owner, in every config)
ACTIONS = ActionTuple(discrete=np.array([NOTHING, FORWARDS], dtype=np.int32))

# Both agents start on x = 20, so this is the distance between them
def _separation(env, steps) -> float:
    positions = [obs["position"] for obs in env.get_obs_dicts(steps.obs)]
    return float(np.linalg.norm(positions[OWNER] - positions[VISITOR]))


def _run_two_agents(config: str, max_steps: int, stop_when=None):
    """
    Steps the arena with ACTIONS until the episode ends, `stop_when(rewards, separation)` returns
    True, or `max_steps` have been taken. Returns each row's cumulative reward, the last separation
    between the agents, and whether the episode ended.
    """
    behavior, dec, term, env = get_aai_env(config)
    try:
        assert len(dec) == 2, f"Expected 2 agents to request decisions, got {len(dec)}"
        rewards = np.zeros(2)
        separation = _separation(env, dec)
        ended = False
        for _ in range(max_steps):
            env.set_actions(behavior, ACTIONS)
            env.step()
            dec, term = env.get_steps(behavior)
            if len(term) > 0:
                assert len(term) == 2, f"Both agents' episodes should end together, but only {len(term)} ended"
                rewards += term.reward
                ended = True
                break
            rewards += dec.reward
            separation = _separation(env, dec)
            if stop_when is not None and stop_when(rewards, separation):
                break
        return rewards, separation, ended
    finally:
        env.close()


def test_agent_in_zone_is_rewarded_every_step_but_the_owner_is_not():
    rewards, separation, ended = _run_two_agents(
        REWARD_CONFIG,
        max_steps=300,
        stop_when=lambda rewards, _: rewards[VISITOR] > 1.0,
    )
    assert not ended, "The episode should not have ended"
    assert separation < 4.5 + 0.5, (
        f"The infant should have reached the mother's zone (radius 4), but is {separation}m away"
    )
    assert rewards[VISITOR] > 1.0, (
        f"The infant should be rewarded for every step near the mother, but its reward is {rewards[VISITOR]}"
    )
    assert rewards[OWNER] < 0, (
        f"The mother carries the zone so should only pay the time penalty, but her reward is {rewards[OWNER]}"
    )


def test_agent_outside_zone_is_not_rewarded():
    # Stop as soon as the infant is within 1m of the zone's edge (radius 4 + body 0.5)
    rewards, separation, _ = _run_two_agents(
        REWARD_CONFIG,
        max_steps=300,
        stop_when=lambda _, separation: separation < 4.5 + 1.0,
    )
    assert separation < 4.5 + 1.0, f"The infant should have walked towards the mother, but is {separation}m away"
    assert rewards[VISITOR] < 0, (
        f"The infant should only have paid the time penalty before reaching the zone, but its reward is {rewards[VISITOR]}"
    )


def test_zone_can_end_the_episode_of_the_agent_that_touches_it():
    time_penalty_budget = 0.3
    rewards, _, ended = _run_two_agents(END_EPISODE_CONFIG, max_steps=300)
    assert ended, "Touching the predator should have ended the episode"
    assert abs(rewards[VISITOR] - (-1)) < time_penalty_budget, (
        f"The prey should get the endEpisode reward of -1 (plus a small time penalty), got {rewards[VISITOR]}"
    )
    assert -time_penalty_budget < rewards[OWNER] <= 0, (
        f"The predator should only pay the time penalty, got {rewards[OWNER]}"
    )


def test_zone_is_blocked_by_a_wall():
    # The wall is 4m from the mother and the zone reaches 6m, so the infant ends up inside the
    # radius but on the other side of the wall. Walk for long enough to be sure it got there and
    # would have been rewarded without the wall.
    rewards, separation, ended = _run_two_agents(WALL_CONFIG, max_steps=250)
    assert not ended, "The episode should not have ended"
    assert separation < 6.5, (
        f"The infant should be within the zone's radius, against the wall, but is {separation}m from the mother"
    )
    assert rewards[VISITOR] < 0, (
        f"The wall should block the zone, so the infant should only pay the time penalty, but its reward is {rewards[VISITOR]}"
    )


def test_zone_can_spawn_an_object_when_another_agent_comes_close():
    rewards, _, ended = _run_two_agents(SPAWN_CONFIG, max_steps=300)
    assert ended, "The infant should have collected the goal the mother's zone spawned, ending the episode"
    assert rewards[VISITOR] > 0.5, (
        f"The infant should have collected the spawned GoodGoal (+1), got {rewards[VISITOR]}"
    )
