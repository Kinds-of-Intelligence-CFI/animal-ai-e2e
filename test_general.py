from shared import run_behaviour_in_aai, forwards_action, nothing_action, get_aai_env
import pickle
import numpy as np
import time

def test_basic_success():
    run_behaviour_in_aai(
        r".\animal-ai-e2e\testConfigs\testUnmergedArenas.yml",
        0.8,
        lambda _ : forwards_action,
    )

def test_basic_fail():
    run_behaviour_in_aai(
        r".\animal-ai-e2e\testConfigs\testUnmergedArenas.yml",
        -1,
        lambda _ : nothing_action,
    )

def test_objects_blackout_camera():
    """
    This test validates three things
    - We can load a config with many objects (if arena doesn't load we have failed this)
    - TODO: Blackout works
    - Visual inputs work (i.e. a basic screenshot test)
    """
    _, dec, _, env = get_aai_env(
        r"C:\Users\talkt\Documents\Cambridge\AAIE2E\animal-ai-e2e\testConfigs\testCrowdedArena.yml",
        False,
        True,
        1234
    )
    try:
        camera_output = env.get_obs_dict(dec.obs)['camera']
        # If we e.g. add an item to the crowded arena config we may need to update this config
        # with open(r".\animal-ai-e2e\data\datascreenshottest.pickle", 'wb') as file:
        #     pickle.dump(camera_output, file)
        with open(r".\animal-ai-e2e\data\datascreenshottest.pickle", 'rb') as file:
            # Deserialize and load the object from the file
            expected_camera_output = pickle.load(file)
        # TODO: Any easier to debug ways of doing this?
        np.testing.assert_array_equal(expected_camera_output, camera_output)
    finally:
        env.close()