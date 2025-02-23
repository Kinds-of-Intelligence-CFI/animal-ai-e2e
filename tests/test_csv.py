from shared import run_behaviour_in_aai, forwards_action, AAI_EXE_PATH
import os
from datetime import datetime
import csv
import filecmp

"""
Tests that a .csv data file is created, and that it has the expected contents
"""
def test_basic_csv_creation():
    run_behaviour_in_aai(
        os.path.join(".", "testConfigs", "testUnmergedArenas.yml"),
        0.8,
        lambda _ : forwards_action
    )
    current_time = datetime.now()
    expected_filename = f"Observations_{current_time.strftime('%d-%m-%y_%H%M')}.csv"

    try:
        env_dir_path = os.path.dirname(os.environ[AAI_EXE_PATH])
        csv_path = os.path.join(env_dir_path, "ObservationLogs", expected_filename)
    except KeyError:
        raise EnvironmentError(f"Environment variable '{AAI_EXE_PATH}' not set")
    print(f"CSV path guess: {csv_path}")

    comp = filecmp.cmp(
        csv_path,
        os.path.join(".", "data", "Template_observations.csv"),
        shallow=False
    )

    assert comp
