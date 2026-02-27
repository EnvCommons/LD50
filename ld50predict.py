"""
LD50Predict - Acute Oral Toxicity Prediction Environment

Single-turn environment where agents predict LD50 (Lethal Dose 50%) values
for molecules given their SMILES notation. LD50 is the dose required to kill
half the test population, measured in log(1/(mol/kg)). In this scale, higher
values indicate higher toxicity.

Data source: TDC LD50_Zhu dataset (7385 molecules).
Continuous reward based on relative prediction error using 1/cosh scaling.
"""

import json
import math
import os
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field

from openreward.environments import (
    Environment,
    JSONObject,
    Split,
    TextBlock,
    ToolOutput,
    tool,
)

if os.path.exists("/orwd_data"):
    ENV_PATH = Path("/orwd_data")
else:
    ENV_PATH = Path(__file__).parent


def load_all_tasks() -> dict[str, list[dict]]:
    data_dir = ENV_PATH / "data"
    all_tasks = {}
    for split in ["train", "test"]:
        json_file = data_dir / f"{split}.json"
        if json_file.exists():
            with open(json_file, "r", encoding="utf-8") as f:
                all_tasks[split] = json.load(f)
        else:
            print(f"Warning: {json_file} not found")
            all_tasks[split] = []
    return all_tasks


ALL_TASKS = load_all_tasks()

ANSWERS = {
    task["task_id"]: {"value": task["answer"]}
    for split_tasks in ALL_TASKS.values()
    for task in split_tasks
}

print(f"Loaded {len(ANSWERS)} LD50Predict tasks")


class LD50PredictTaskSpec(BaseModel):
    task_id: str
    smiles: str
    property_name: str
    property_units: str
    question: str


class SubmitPredictionInput(BaseModel):
    prediction: float = Field(
        ..., description="Your predicted LD50 value in log(1/(mol/kg))"
    )


class LD50Predict(Environment):
    """
    LD50 acute oral toxicity prediction environment.

    Agents predict LD50 values for molecules.
    Reward is continuous in [0, 1] based on relative prediction accuracy.
    """

    def __init__(self, task_spec: JSONObject, secrets: dict[str, str] = {}) -> None:
        super().__init__(task_spec)
        self.validated = LD50PredictTaskSpec.model_validate(task_spec)

        if self.validated.task_id not in ANSWERS:
            raise ValueError(f"Task {self.validated.task_id} not found in ANSWERS")

        self.answer = ANSWERS[self.validated.task_id]

    @classmethod
    def list_splits(cls) -> list[Split]:
        return [
            Split(name="train", type="train"),
            Split(name="test", type="test"),
        ]

    @classmethod
    def list_tasks(cls, split: str) -> list[JSONObject]:
        if split not in ALL_TASKS:
            return []
        return [
            {k: v for k, v in task.items() if k != "answer"}
            for task in ALL_TASKS[split]
        ]

    async def get_prompt(self) -> List[TextBlock]:
        return [TextBlock(text=self.validated.question)]

    @tool
    async def submit_prediction(self, params: SubmitPredictionInput) -> ToolOutput:
        """Submit your predicted LD50 value for the molecule."""
        predicted = params.prediction
        actual = self.answer["value"]
        reward = self._compute_reward(predicted, actual)

        feedback = (
            f"Prediction: {predicted:.4f}\n"
            f"Reward: {reward:.4f}\n\n"
            f"Property: LD50 Acute Oral Toxicity ({self.validated.property_units})"
        )

        return ToolOutput(
            blocks=[TextBlock(text=feedback)],
            metadata={
                "task_id": self.validated.task_id,
                "smiles": self.validated.smiles,
                "predicted": predicted,
                "actual": actual,
                "reward": reward,
            },
            reward=reward,
            finished=True,
        )

    def _compute_reward(self, predicted: float, actual: float) -> float:
        """MAE-based reward. Values are in log(1/(mol/kg)) so absolute
        error is the natural metric (matches TDC benchmark).

        reward = 1 / cosh(|predicted - actual|)
        - MAE 0.0 -> 1.000
        - MAE 0.5 -> 0.887
        - MAE 1.0 -> 0.648
        - MAE 2.0 -> 0.266
        """
        mae = abs(predicted - actual)
        reward = 1.0 / math.cosh(mae)
        return round(reward, 4)
