import os

from inspect_ai import Task, eval, task
from inspect_ai.solver import (
    Solver,
    basic_agent,
    system_message,
)
from inspect_ai.model import (
    ChatMessage,
    GenerateConfig,
    ModelAPI,
    ModelOutput,
    modelapi,
)
from inspect_ai.tool import ToolChoice, ToolInfo
from inspect_ai.dataset import MemoryDataset, Sample
from animalai.LLM_scaffolds.environment_scaffolds import FrameByFrameScaffold
from animalai.LLM_scaffolds.inspect_wrapper import add_act_tool, total_reward_scorer


@modelapi("forward-only")
class ForwardOnlyModel(ModelAPI):
    async def generate(
        self,
        input: list[ChatMessage],
        tools: list[ToolInfo],
        tool_choice: ToolChoice,
        config: GenerateConfig,
    ) -> ModelOutput:
        return ModelOutput.for_tool_call(
            model="forward-only",
            tool_name="act",
            tool_arguments={"action": "FORWARD"},
        )

"""
Tests that the included LLM scaffolding works by running an inspect test with a mock LLM.

Venv patches applied to animalai (reinstall will revert these):
- inspect_wrapper.py no_graphics default: True -> False. True disables Unity rendering,
  producing black camera frames.
- inspect_wrapper.py encode_camera_obs: skip *255 scaling when obs is already uint8.
  _process_obs (environment_scaffolds.py) converts to uint8 before returning, so
  encode_camera_obs was double-scaling and saturating every non-zero pixel to 255.

- The test might not end properly if the LM fails, takes ages etc
"""


@task
def basic_arena_task(agent_solver: Solver | None = None) -> Task:
    dataset = MemoryDataset(samples=[
        Sample(
            input="Please path to the goal area marked by the green object.",
            metadata={
                "arenas_configurations": os.path.join("testconfigs","testUnmergedArenas.yml"),
                "no_graphics": False,
            },
            )
    ])

    solver_chain = [
        system_message(FrameByFrameScaffold.get_default_system_prompt()),
        add_act_tool(scaffold_type=FrameByFrameScaffold),
        agent_solver or basic_agent(),
    ]

    return Task(
        dataset=dataset,
        solver=solver_chain,
        scorer=total_reward_scorer(),
        message_limit=30,
    )

def test_basic_success():
    logs = eval(
        [basic_arena_task()],
        model="forward-only/model",
    )
    for log in logs:
        assert log.status == "success"
