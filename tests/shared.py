import sys
import os
LOCAL_PY_ENV_PATH = "LOCAL_PY_ENV_PATH"
AAI_EXE_PATH = "AAI_EXE_PATH"
if LOCAL_PY_ENV_PATH in os.environ:
    sys.path.insert(0, os.environ[LOCAL_PY_ENV_PATH])
from animalai.environment import AnimalAIEnvironment
import sys
import math
import time
import numpy as np
from mlagents_envs.base_env import ActionTuple, DecisionSteps, TerminalSteps
from typing import Callable, Optional
import pickle
from PIL import Image

# TODO: reloading the AAI environment takes up most the time - share between tests?

try:
    env_path = os.environ[AAI_EXE_PATH]
except KeyError:
    raise EnvironmentError(f"Environment variable '{AAI_EXE_PATH}' not set")
print(f"Using env_path: {env_path}")

def get_aai_env(
        configuration_file: str,
        no_graphics: bool = True,
        use_Camera: bool  = False,
        seed: int = int(time.time()),
        timescale: int = 10
        ) -> tuple[str, DecisionSteps, TerminalSteps, AnimalAIEnvironment]:
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
        log_folder = r".",
        timescale=timescale,
        resolution = 512
    )
    behavior = list(env.behavior_specs.keys())[0] # Get the first behavior name
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

def run_behaviour_in_aai(
        configuration_file: str,
        expected_reward: float,
        secondary_behaviour: Callable[[float], ActionTuple],
        primary_behaviour: Optional[ActionTuple] = None,
        watch: bool = False
        ) -> None:
    behavior, dec, term, env = get_aai_env(configuration_file) if not watch else get_aai_env(configuration_file, no_graphics=False, use_Camera=True, timescale=1)
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
    try:
        assert abs(episode_Reward - expected_reward) < 0.2, f"Unexpected episode reward, got {episode_Reward} but expected {expected_reward}"
    finally:
        env.close()

def run_screenshot_test(
        config: str,
        expected_screenshot_path: str,
        update_screenshot: bool = False,
        test_name: str = ""
):
    _, dec, _, env = get_aai_env(
        config,
        False,
        True,
        1234
    )
    try:
        camera_output = env.get_obs_dict(dec.obs)['camera']
        if update_screenshot:
            # Warning! If we e.g. add an item to the crowded arena config we may need to update this config
            with open(expected_screenshot_path, 'wb') as file:
                pickle.dump(camera_output, file)
    finally:
        env.close()
    with open(expected_screenshot_path, 'rb') as file:
            # Deserialize and load the object from the file
            expected_camera_output = pickle.load(file)
    try:
        np.testing.assert_array_equal(expected_camera_output, camera_output)
    except AssertionError as e:
        scale_image = lambda image : np.array(image * 255, dtype=np.uint8)
        expected_camera_output_scaled = scale_image(expected_camera_output)
        camera_output_scaled = scale_image(camera_output)
        expected_camera_output_image = Image.fromarray(expected_camera_output_scaled)
        camera_output_image = Image.fromarray(camera_output_scaled)
        difference_image = Image.fromarray(expected_camera_output_scaled - camera_output_scaled)
        expected_camera_output_image.save(f"Expected_{test_name}.png")
        camera_output_image.save(f"Observed_{test_name}.png")
        difference_image.save(f"Difference_{test_name}.png")
        raise e
