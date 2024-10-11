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

- Python 3.10+
- [pytest](https://docs.pytest.org/en/stable/) for running tests
- VSCode for integrated development (optional but recommended)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Kinds-of-Intelligence-CFI/animal-ai-e2e.git
   cd animal-ai-e2e
   ```

2. Set up your environment variables:
   - `AAI_EXE_PATH`: Path to the Animal-AI executable.
   - `LOCAL_PY_ENV_PATH`: Path to the local copy of the Animal-AI Python package.

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
LOCAL_PY_ENV_PATH="my/python/package/animal-ai-python"
```

## Usage

Run the tests using pytest:

```bash
pytest
```

You can also run a specific test file, i.e., `test_general.py`:
```bash
pytest tests/test_general.py
```

## Repository TODOs

- Write play mode tests (success + failure)
- Integrate with GitHub Actions for CI/CD
- Add a TOML configuration file
- Expand test coverage and scenarios
- Improve documentation with examples and detailed explanations

## Contributing

We welcome contributions!

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
