# animal-ai-e2e
A suite of E2E tests for AAI.

This is the package that (hopefully) will eventually become a suite of E2E tests we can use in CI/CD for Animal-AI.

The tests are written to use pytest (`pip install pytest`), which has default integration in vscode.

Tasks of turning this into a proper test suite (get good coverage over use cases, use a proper testing framework ...) tracked in https://www.notion.so/763741e558da4edb992b199a1233f169?v=da4b83d65c6b4ced81744d180b36001b&p=19c3c7c87da84dd0b42ff38bc2af0350&pm=s

# TODO

- Move user specific constants to separate file
- Write proper README

## tests-to-write

- play mode success
- play mode failure
- blackout
- objects
- training an agent
- Running with graphics
