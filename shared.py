from animalai.environment import AnimalAIEnvironment
import sys
import math
import time
import numpy as np
from mlagents_envs.base_env import ActionTuple, DecisionSteps, TerminalSteps
from typing import Callable, Optional
import os

# TODO: reloading the AAI environment takes up most the time - share between tests?

env_path = r"C:\Users\talkt\Documents\Cambridge\MultiArenaEpisodes\animalAIUnity\AnimalAI.exe"

def get_aai_env(configuration_file: str, no_graphics: bool = True, use_Camera: bool  = False, seed: int = int(time.time())) -> tuple[str, DecisionSteps, TerminalSteps, AnimalAIEnvironment]:
    totalRays = 9
    env = AnimalAIEnvironment(
        file_name=env_path,
        arenas_configurations=configuration_file,
        seed=seed,
        play=False,
        useCamera=use_Camera,
        no_graphics=no_graphics,
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
    episode_Reward = 0
    while not done:
        if len(dec.reward) > 0:
            episode_Reward += dec.reward

        if len(term) > 0:
            episode_Reward += term.reward
            done = True
            break

        env.set_actions(behavior, secondary_behaviour(episode_Reward))
        env.step()
        dec, term = env.get_steps(behavior)
    print(f"Episode reward: {episode_Reward}")
    assert abs(episode_Reward - expected_reward) < 0.2, f"Unexpected episode reward, got {episode_Reward} but expected {expected_reward}"

    env.close()