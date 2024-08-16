# animal-ai-e2e
A suite of E2E tests for AAI.

This is the package that (hopefully) will eventually become a suite of E2E tests we can use in CI/CD for Animal-AI.

The tests are written to use pytest (`pip install pytest`), which has default integration in vscode.

# Environment variables
- The location of the AAI executable is specified using the AAI_EXE_PATH environment variable. This might be a release, or a version under development that has been manually built.

- The location of a local copy of the AAI python package can be specified with the LOCAL_PY_ENV_PATH environment variable. If this is not included the E2E tests will default to whatever version of the package is available in the environment

## Example

For example, if I'm developing in the python package in VSCode and I've cloned the python package to "my\python\package\animal-ai-python" and my executable is at "my\executable\path\Animal-AI.exe" I could configure my tests by:

- Creating the file ".vscode\settings.json" if it doesn't exist already and adding the following contents (the key line is `"python.envFile": "${workspaceFolder}/.vscode/.env"
}`):
```
{
    "python.testing.pytestArgs": [
        "."
    ],
    "python.testing.unittestEnabled": false,
    "python.testing.pytestEnabled": true,
    "python.envFile": "${workspaceFolder}/.vscode/.env"
}
```
- Creating the file ".vscode\.env" with the following contents:
```
AAI_EXE_PATH="my\executable\path\Animal-AI.exe"
LOCAL_PY_ENV_PATH="my\python\package\animal-ai-python"
```

# TODO

- Write play mode tests (success + failure)
- Run with github actions
- Add a TOML 
