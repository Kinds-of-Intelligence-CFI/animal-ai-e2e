import os
from datetime import datetime
from typing import Union, Literal, List

from shared import run_behaviour_in_aai, forwards_action, AAI_EXE_PATH


def compare_lines_by_indices(
    file1: str, file2: str, indices: List[int]
) -> Union[Literal[True], str]:
    """
    Compares lines at specified indices of two CSV files.

    Args:
        file1: Path to the first file.
        file2: Path to the second file.
        indices: List of line indices to compare.
                 Indices can be positive (0-based from the start) or negative (from the end of the file).

    Returns:
        True if all specified lines match, or a string describing the first difference.
    """
    with open(file1, "r", encoding="utf-8") as f1:
        lines1 = f1.readlines()

    with open(file2, "r", encoding="utf-8") as f2:
        lines2 = f2.readlines()

    for idx in indices:
        try:
            line1 = lines1[idx]
        except IndexError:
            return f"File '{file1}' does not have a line at index {idx}."
        try:
            line2 = lines2[idx]
        except IndexError:
            return f"File '{file2}' does not have a line at index {idx}."

        if line1 != line2:
            # Split lines into cells and find the first different cell.
            cells1 = line1.strip().split(",")
            cells2 = line2.strip().split(",")
            for cell_num, (cell1, cell2) in enumerate(zip(cells1, cells2)):
                if cell1 != cell2:
                    return f"Difference at line index {idx} (cell {cell_num+1}): '{cell1}' vs '{cell2}'"
            # If all common cells are the same, check if the number of cells differ.
            if len(cells1) != len(cells2):
                return f"Different number of cells at line index {idx}: {len(cells1)} vs {len(cells2)}"

    return True


def test_basic_csv_creation():
    """
    Tests that a .csv data file is created, and that it has the expected contents
    """
    run_behaviour_in_aai(
        os.path.join(".", "testConfigs", "testUnmergedArenas.yml"),
        0.8,
        lambda _: forwards_action,
    )
    current_time = datetime.now()
    expected_filename = f"Observations_{current_time.strftime('%d-%m-%y_%H%M')}.csv"

    try:
        env_dir_path = os.path.dirname(os.environ[AAI_EXE_PATH])
        csv_path = os.path.join(env_dir_path, "ObservationLogs", expected_filename)
    except KeyError:
        raise EnvironmentError(f"Environment variable '{AAI_EXE_PATH}' not set")
    print(f"CSV path guess: {csv_path}")

    comp = compare_lines_by_indices(
        csv_path,
        os.path.join(".", "data", "Template_observations.csv"),
        # Even though we're only testing one episode, there's a second episode of a few frames that hangs over
        # As the number of hangover frames is variable, only check the final 'Goals Collected' line
        list(range(31)) + [-1],
    )

    assert isinstance(comp, bool), "CSV comparison failed" + comp
