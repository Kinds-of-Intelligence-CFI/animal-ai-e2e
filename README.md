# Animal-AI E2E

#### Table of Contents
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
- [Configuration](#configuration)
  - [VSCode Configuration](#vscode-configuration)
  - [Environment Variables](#environment-variables)
- [Usage](#usage)

A suite of End-to-End (E2E) tests for the Animal-AI environment. This package aims to provide a suite of E2E tests for use in CI/CD pipelines with Python pytest package, ensuring the stability and reliability of the Animal-AI platform.

## Installation

### Prerequisites

- [uv](https://docs.astral.sh/uv/) (it installs the right Python, 3.14, by itself)
- VSCode for integrated development (optional but recommended)

### Setup

1. Clone this repository **next to a checkout of `animal-ai-python`**: the uv environment installs the
   Animal-AI Python package from `../animal-ai-python` (editable), so tests run against your local copy.
   ```bash
   git clone https://github.com/Kinds-of-Intelligence-CFI/animal-ai-e2e.git
   git clone https://github.com/Kinds-of-Intelligence-CFI/animal-ai-python.git
   cd animal-ai-e2e
   ```
   To use the released `animalai` package from PyPI instead, delete the `animalai = ...` line under
   `[tool.uv.sources]` in `pyproject.toml`.

2. Create the environment:
   ```bash
   uv sync
   ```

3. Set up your environment variables:
   - `AAI_EXE_PATH`: Path to the Animal-AI executable.
   - `E2E_TEST_PLATFORM`: `windows`, `linux` or `macos`.

## Configuration

### VSCode Configuration

To streamline development in VSCode, you can create a `.vscode/settings.json` file with the following content:

```json
{
    "python.testing.pytestArgs": [
        "."
    ],
    "python.testing.unittestEnabled": false,
    "python.testing.pytestEnabled": true,
    "python.envFile": "${workspaceFolder}/.vscode/.env"
}
```

### Environment Variables

Create a `.vscode/.env` file to specify the required environment variables:

```env
AAI_EXE_PATH="my/executable/path/Animal-AI.exe"
E2E_TEST_PLATFORM="windows"
```

To use the same file from the command line, pass it to uv: `uv run --env-file .vscode/.env pytest`.

## Usage

Run the tests using pytest:

```bash
uv run pytest
```

You can also run a specific test file, i.e., `test_general.py`:
```bash
uv run pytest tests/test_general.py
```

## Repository TODOs

- [x] Write play mode tests (success + failure)
- [ ] Integrate with GitHub Actions for CI/CD
- [ ] Add a TOML configuration file
- [ ] Expand test coverage and scenarios
- [ ] Improve documentation with examples and detailed explanations