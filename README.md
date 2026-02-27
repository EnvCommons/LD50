# LD50Predict

Single-turn OpenReward environment for predicting acute oral toxicity (LD50) of molecules from SMILES notation.

## Task

Given a molecule's SMILES string, the agent predicts the LD50 value in log(1/(mol/kg)). LD50 is the dose required to kill 50% of a test population. In this log-inverse-molar scale, **higher values indicate higher toxicity**.

## Data Source

All data comes from the [TDC LD50_Zhu dataset](https://tdcommons.ai/benchmark/admet_group/19ld50/) (Zhu et al.), containing 7,342 unique molecules with experimentally measured LD50 values. Units are `log(1/(mol/kg))` as documented by TDC.

1,100 molecules sampled (1,000 train + 100 test), shuffled with `random_state=42`.

### Data Statistics

| Split | Tasks | Answer Range | Mean | Median |
|-------|-------|-------------|------|--------|
| Train | 1,000 | [-0.34, 5.47] | 2.50 | 2.32 |
| Test | 100 | [0.70, 5.40] | 2.64 | 2.52 |

All values in log(1/(mol/kg)). Higher = more toxic.

## Reward Function

MAE-based reward (matches TDC benchmark metric). Since values are in log scale, absolute error is the natural metric:

```
reward = 1 / cosh(|predicted - actual|)
```

| MAE (log units) | Reward |
|----------------|--------|
| 0.0 (exact) | 1.000 |
| 0.3 | 0.957 |
| 0.5 | 0.887 |
| 1.0 | 0.648 |
| 1.5 | 0.425 |
| 2.0 | 0.266 |

## Environment API

- **Splits:** `train` (1,000 tasks), `test` (100 tasks)
- **Tool:** `submit_prediction(prediction: float)` — submit LD50 in log(1/(mol/kg))
- **Prompt:** Provides SMILES string and property description
- **Finished:** Always `True` after one tool call (single-turn)

## Files

```
ld50predict/
├── ld50predict.py     # Environment class (LD50Predict)
├── server.py          # Server wrapper
├── test_agent.py      # OpenAI Responses API test harness
├── prepare_data.py    # TDC download + JSON generation script
├── requirements.txt   # openreward, pydantic
├── Dockerfile
├── DATA_UPLOAD.md     # Cloud storage upload instructions
└── data/
    ├── train.json     # 1,000 training tasks
    └── test.json      # 100 test tasks
```

## Local Development

```bash
# Generate data (requires PyTDC)
pip install PyTDC pandas
python prepare_data.py

# Run server
pip install -r requirements.txt
python server.py

# Test with agent
export OPENAI_API_KEY=...
python test_agent.py
```

## Docker

```bash
docker build -t ld50predict:test .
docker run -p 8080:8080 ld50predict:test
```
