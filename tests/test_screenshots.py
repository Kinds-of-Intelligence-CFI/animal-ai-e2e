from shared import run_screenshot_test
from typing import Callable
import pytest
import os

"""
This test validates three things: 
- We can load a config with many objects (if arena doesn't load we have failed this)
- Test if blackout camera works (i.e. a basic screenshot test)
- Visual inputs work (i.e. a basic screenshot test)
"""
def test_objects_blackout_camera():
    run_screenshot_test(
        os.path.join(".", "testConfigs", "testCrowdedArena.yml"),
        os.path.join(".", "data", "datascreenshottest.pickle"),
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
    "SignPosterboard",
    "DataZone",
    ("DataZone", {"zoneVisibility": "false"})
]

def unpack_extra_args(d: dict[str, str]):
    if not d:  # Check if dictionary is empty
        return ""

    result = "\n"
    for key, value in d.items():
        result += f"      {key}: {value}\n"

    return result

gen_config: Callable[[str, dict[str, str]], str] = lambda object_name, optional_args : f"""
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
      - !Vector3 {{x: 1, y: 1, z: 1}}{unpack_extra_args(optional_args)}
    - !Item
      name: Agent
      positions:
      - !Vector3 {{x: 30, y: 0, z: 20}}
      rotations: [270]
"""

def get_test_name(item: str | tuple[str, dict[str, str]]) -> str:
    if isinstance(item, tuple):
        item_name, args = item
        return f"{item_name}_{'_'.join(f'{k}_{v}' for k, v in args.items())}"
    else:
        return item

@pytest.mark.parametrize('item', test_configs, ids=get_test_name)
def test_single_item_screenshot_test(item: str | tuple[str, dict[str, str]]):
    test_name = get_test_name(item)
    if isinstance(item, tuple):
        item_name, args = item
    else:
        item_name, args = item, {}
    config_content = gen_config(item_name, args)
    config_file_name = f"screenshot_test_config_{test_name}.yml"
    try:
        with open(config_file_name, "w") as file:
            file.write(config_content)
        run_screenshot_test(
            config_file_name,
            os.path.join(".", "data", f"{test_name}_screenshot_test.pickle"),
            test_name=test_name
        )
    finally:
        os.remove(config_file_name)
