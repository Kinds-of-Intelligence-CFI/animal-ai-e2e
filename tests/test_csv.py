import os
from datetime import datetime
from typing import Union, Literal

from shared import run_behaviour_in_aai, forwards_action, AAI_EXE_PATH

def compare_first_n_lines(file1: str, file2: str, n: int) -> Union[Literal[True], str]:
    """
    Compares the first n lines of two CSV files.

    Args:
        file1: Path to the first file
        file2: Path to the second file
        n: Number of lines to compare (default: 32)

    Returns:
        True if all lines match, or a string describing the first difference
    """
    with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
        for line_num in range(n):
            try:
                line1 = next(f1)
                line2 = next(f2)

                if line1 != line2:
                    # Split lines into cells and find the first different cell
                    cells1 = line1.strip().split(',')
                    cells2 = line2.strip().split(',')

                    for cell_num, (cell1, cell2) in enumerate(zip(cells1, cells2)):
                        if cell1 != cell2:
                            return f"Difference at line {line_num+1}, cell {cell_num+1}: '{cell1}' vs '{cell2}'"

                    # If we get here, the lines have different lengths
                    if len(cells1) != len(cells2):
                        return f"Different number of cells at line {line_num+1}: {len(cells1)} vs {len(cells2)}"

            except StopIteration:
                return f"One file ended unexpectedly at line {line_num+1}"

        return True

def test_basic_csv_creation():
    """
        Tests that a .csv data file is created, and that it has the expected contents
    """
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

    comp = compare_first_n_lines(
    csv_path,
    os.path.join(".", "data", "Template_observations.csv"),
    32
)

    assert isinstance(comp, bool), "CSV comparison failed"+comp
