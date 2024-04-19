from animalai.environment import AnimalAIEnvironment
import sys
import math
import time
import numpy as np
from mlagents_envs.base_env import ActionTuple, DecisionSteps, TerminalSteps
from typing import Callable, Optional

env_path = r"C:\Users\talkt\Documents\Cambridge\MultiArenaEpisodes\animalAIUnity\AnimalAI.exe"

def get_aai_env(configuration_file: str) -> tuple[str, DecisionSteps, TerminalSteps, AnimalAIEnvironment]:
    totalRays = 9
    env = AnimalAIEnvironment(
        file_name=env_path,
        arenas_configurations=configuration_file,
        seed=int(time.time()),
        play=False,
        useCamera=False, #The Braitenberg agent works with raycasts
        useRayCasts=True,
        raysPerSide=int((totalRays-1)/2),
        rayMaxDegrees = 30,
        inference=True,
        log_folder = r"C:\Users\talkt\Documents\Cambridge\MultiArenaEpisodes\multiArenaEpisodes",
        timescale=10
    )
    behavior = list(env.behavior_specs.keys())[0] # by default should be AnimalAI?team=0
    env.step() # Need to make a first step in order to get an observation.
    dec, term = env.get_steps(behavior)
    return behavior, dec, term, env

forwards_action = ActionTuple(
            continuous=np.zeros((1, 0)),
            discrete=np.array([[1, 0]], dtype=np.int32),
        )

backwards_action = ActionTuple(
                continuous=np.zeros((1, 0)),
                discrete=np.array([[2, 0]], dtype=np.int32),
            )

nothing_action = ActionTuple(
            continuous=np.zeros((1, 0)),
            discrete=np.array([[0, 0]], dtype=np.int32),
        )

def run_behaviour_in_aai(configuration_file: str, expected_reward: float, secondary_behaviour: Callable[[float], ActionTuple], primary_behaviour: Optional[ActionTuple] = None) -> None:
    behavior, dec, term, env = get_aai_env(configuration_file)
    if primary_behaviour is not None:
        while len(term) == 0:
            env.set_actions(behavior, primary_behaviour)
            env.step()
            dec, term = env.get_steps(behavior)
        env.step() # Need to make a first step in order to get an observation.
        dec, term = env.get_steps(behavior)
    done = False
    episodeReward = 0
    while not done:
        if len(dec.reward) > 0:
            episodeReward += dec.reward

        if len(term) > 0:
            episodeReward += term.reward
            done = True
            break

        env.set_actions(behavior, secondary_behaviour(episodeReward))
        env.step()
        dec, term = env.get_steps(behavior)
    print(f"Episode reward: {episodeReward}")
    assert abs(episodeReward - expected_reward) < 0.2

    env.close()

def test_should_not_merge_if_merge_flag_not_included():
    run_behaviour_in_aai(
        r".\testConfigs\testUnmergedArenas.yml",
        0.8,
        lambda _ : forwards_action,
    )

def test_should_merge_if_merge_flag_included():
    run_behaviour_in_aai(
        r".\testConfigs\testMergedArenas.yml",
        1.6,
        lambda r : backwards_action if r > 0 else forwards_action,
    )

def test_should_skip_next_merged_arena_if_fails_from_lava():
    run_behaviour_in_aai(
        r".\testConfigs\testFailArenas.yml",
        0.895,
        lambda _ : forwards_action,
        forwards_action
    )

def test_should_skip_next_merged_arena_if_fails_from_timeout():
    run_behaviour_in_aai(
        r".\testConfigs\testFailArenas.yml",
        0.895,
        lambda _ : forwards_action,
        nothing_action
    )

# TODO: reloading the AAI environment takes up most the time - share between tests?
if __name__ == "__main__":
    # If we don't include MergeNextArena things work as usual
    test_should_not_merge_if_merge_flag_not_included()
    # If we include MergeNextArena both arenas are included in the episode
    test_should_merge_if_merge_flag_included()
    # Failure scenarios should not roll into a merged arena
    test_should_skip_next_merged_arena_if_fails_from_lava()
    test_should_skip_next_merged_arena_if_fails_from_timeout()
