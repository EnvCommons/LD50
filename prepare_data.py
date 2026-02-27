"""
Download and prepare LD50 dataset from TDC.

Creates 1000 train + 100 test tasks from LD50_Zhu (7385 molecules).
Run once locally: python prepare_data.py
"""

import json
from pathlib import Path

from tdc.single_pred import Tox


PROPERTY_NAME = "LD50 Acute Oral Toxicity"
PROPERTY_UNITS = "log(1/(mol/kg))"
TRAIN_SIZE = 1000
TEST_SIZE = 100


def make_question(smiles: str) -> str:
    return (
        f"You are a molecular toxicity prediction expert.\n\n"
        f"Given the molecule with SMILES notation: {smiles}\n\n"
        f"Predict the LD50 (Lethal Dose 50%) value for this molecule in {PROPERTY_UNITS}. "
        f"LD50 is the dose of a substance required to kill half the test population. "
        f"In this log-inverse-molar scale, higher values indicate higher toxicity.\n\n"
        f"Submit your prediction as a single floating-point number using the submit_prediction tool."
    )


def main():
    print("Downloading LD50_Zhu dataset...")
    data = Tox(name="LD50_Zhu")
    df = data.get_data()
    df = df.dropna(subset=["Drug", "Y"])
    df = df.drop_duplicates(subset=["Drug"])
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    print(f"Total molecules: {len(df)}")

    total = TEST_SIZE + TRAIN_SIZE
    selected = df.head(total)

    tasks = []
    for idx, row in selected.iterrows():
        split = "test" if idx < TEST_SIZE else "train"
        task = {
            "task_id": f"ld50_{split}_{idx}",
            "smiles": row["Drug"],
            "property_name": PROPERTY_NAME,
            "property_units": PROPERTY_UNITS,
            "answer": float(row["Y"]),
            "question": make_question(row["Drug"]),
        }
        tasks.append(task)

    test_tasks = [t for t in tasks if "test" in t["task_id"]]
    train_tasks = [t for t in tasks if "train" in t["task_id"]]

    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)

    with open(data_dir / "test.json", "w") as f:
        json.dump(test_tasks, f, indent=2)
    with open(data_dir / "train.json", "w") as f:
        json.dump(train_tasks, f, indent=2)

    print(f"Saved {len(train_tasks)} train tasks and {len(test_tasks)} test tasks")


if __name__ == "__main__":
    main()
