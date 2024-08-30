from shared import run_screenshot_test
from typing import Callable
import pytest
import os

# - Test blackout works

def test_objects_blackout_camera():
    """
    This test validates two things
    - We can load a config with many objects (if arena doesn't load we have failed this)
    - Visual inputs work (i.e. a basic screenshot test)
    """
    run_screenshot_test(
        r"C:\Users\talkt\Documents\Cambridge\AAI_dev\improving_screenshot_tests\animal-ai-e2e\testConfigs\testCrowdedArena.yml",
        r".\animal-ai-e2e\data\datascreenshottest.pickle",
        test_name="crowded_arena"
    )

test_configs = [
    "Wall",
    "WallTransparent",
    "Ramp",
    "CylinderTunnel",
    "LightBlock",
    "HeavyBlock",
    "UBlock",
    "LBlock",
    "JBlock",
    "HollowBox",
    "GoodGoalBounce",
    "GoodGoalMulti",
    "BadGoal",
    "BadGoalBounce",
    "BadGoalMulti",
    "GoodGoalMulti",
    "GoodGoalMultiBounce",
    "RipenGoal",
    "DecayGoal",
    "GrowGoal",
    "ShrinkGoal",
    "DecoyGoal",
    "DeathZone",
    "HotZone",
    "GoodGoal",
    "SpawnerTree",
    "SpawnerDispenserTall",
    "SpawnerContainerShort",
    "SpawnerButton",
    "SignPosterboard"
]

gen_config: Callable[[str], str] = lambda object_name : f"""
!ArenaConfig
arenas:
  0: !Arena
    timeLimit: 5
    items:
    - !Item
      name: {object_name}
      positions:
      - !Vector3 {{x: 20, y: 0, z: 20}}
      rotations: [0]
      sizes:
      - !Vector3 {{x: 1, y: 1, z: 1}}
    - !Item
      name: Agent
      positions:
      - !Vector3 {{x: 30, y: 0, z: 20}}
      rotations: [270]
"""

@pytest.mark.parametrize('item_name', test_configs)
def test_single_item_screenshot_test(item_name: str):
    config_content = gen_config(item_name)
    config_file_name = f"screenshot_test_config_{item_name}.yml"
    try:
        with open(config_file_name, "w") as file:
            file.write(config_content)
        run_screenshot_test(
            config_file_name,
            rf".\animal-ai-e2e\data\{item_name}_screenshot_test.pickle",
            test_name=item_name
        )
    finally:
        os.remove(config_file_name)
