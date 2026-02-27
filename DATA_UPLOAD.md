# Data Upload Requirements for LD50Predict

## Overview
This environment requires LD50 acute oral toxicity prediction data uploaded to OpenReward cloud storage.

## Directory Structure
```
/orwd_data/
└── data/
    ├── train.json (1000 tasks, ~400 KB)
    └── test.json (100 tasks, ~40 KB)
```

## Files Required
- **train.json**: 1000 LD50 prediction tasks from TDC LD50_Zhu dataset
- **test.json**: 100 LD50 prediction tasks

## Data Generation
Run locally: `python prepare_data.py` (requires `pip install PyTDC pandas`)

## Upload Instructions
Upload the `data/` directory to your OpenReward namespace at https://openreward.ai.
