import os
import random
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


def compare_csv_file(
    template_path: str, lines_to_compare: List[int], tidy_up_csv=True
) -> Union[Literal[True], str]:
    try:
        csv_files_dir_path = os.path.join(
            os.path.dirname(os.environ[AAI_EXE_PATH]), "ObservationLogs"
        )
        files = [
            os.path.join(csv_files_dir_path, f)
            for f in os.listdir(csv_files_dir_path)
            if os.path.isfile(os.path.join(csv_files_dir_path, f))
        ]
        csv_path = max(files, key=os.path.getmtime)
    except KeyError as exc:
        raise EnvironmentError(
            f"Environment variable '{AAI_EXE_PATH}' not set"
        ) from exc
    print(f"CSV path guess: {csv_path}")

    comp = compare_lines_by_indices(csv_path, template_path, lines_to_compare)

    # AAI might overwrite CSV files written in the same minute, so tidy up the file
    if tidy_up_csv:
        if comp is True:
            os.remove(csv_path)
        else:
            random_suffix = random.randint(
                0, 999
            )  # In case two tests fail in the same minute
            file_name, file_ext = os.path.splitext(csv_path)
            new_path = f"{file_name}_failed_{random_suffix}{file_ext}"
            os.rename(csv_path, new_path)

    return comp


def test_basic_csv_creation():
    """
    Tests that a .csv data file is created, and that it has the expected contents
    """
    run_behaviour_in_aai(
        os.path.join(".", "testConfigs", "testUnmergedArenas.yml"),
        0.8,
        lambda _: forwards_action,
    )
    comp = compare_csv_file(
        os.path.join(".", "data", "csv_tests", "Template_observations.csv"),
        # Even though we're only testing one episode, there's a second episode of a few frames that hangs over
        # As the number of hangover frames is variable, only check the final 'Goals Collected' line
        list(range(31)) + [-1],
    )

    assert isinstance(comp, bool), "CSV comparison failed" + comp


def test_datazones():
    """
    Tests that datazones produce the expected output
    """
    run_behaviour_in_aai(
        os.path.join(".", "testConfigs", "testDatazone.yml"),
        0.8,
        lambda _: forwards_action,
    )
    comp = compare_csv_file(
        os.path.join(".", "data", "csv_tests", "Template_datazones.csv"),
        list(range(89)),
    )

    assert isinstance(comp, bool), "CSV comparison failed" + comp


def test_overlapping_datazones_should_combine_messages():
    """
    Tests that overlapping datazones don't interfere with one another
    """
    run_behaviour_in_aai(
        os.path.join(".", "testConfigs", "testDatazoneOverlap.yml"),
        0.8,
        lambda _: forwards_action,
        watch=True,
    )
    # Check all possible orders of writing from the data zones since we have a race condition
    file_names = [
        f"Template_overlappingDatazonesShouldCombineMessages_{i}.csv"
        for i in range(1, 5)
    ]
    comps = [
        compare_csv_file(
            os.path.join(".", "data", "csv_tests", file_name),
            list(range(44)),
            # Only tidy up the file on the last comparison
            tidy_up_csv=(False if i != 4 else True),
        )
        for i, file_name in enumerate(file_names)
    ]

    assert any(isinstance(comp, bool) for comp in comps), (
        "CSV comparison failed" + "\n" + "\n".join([str(comp) for comp in comps])
    )
