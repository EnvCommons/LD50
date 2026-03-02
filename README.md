# LD50

[![OpenReward Environment](https://img.shields.io/badge/%E2%AD%90%20OpenReward-Environment-f7e6cc)](https://openreward.ai/GeneralReasoning/LD50)

## Description

**LD50** is an environment for evaluating agents on acute oral toxicity prediction. Given a molecule's SMILES string, agents predict the LD50 (Lethal Dose 50%) value in log(1/(mol/kg)). LD50 is the dose required to kill half the test population; in this log-inverse-molar scale, higher values indicate higher toxicity. The dataset is derived from the [TDC LD50_Zhu dataset](https://tdcommons.ai/single_pred_tasks/tox/).

## Capabilities

- Predicting acute oral toxicity (LD50) from molecular SMILES notation
- Quantitative molecular property prediction
- Understanding structure-toxicity relationships

## Compute Requirements

LD50Predict does not require a sandbox. It has minimal compute requirements.

## License

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Tasks

There are two splits: train (1,000 tasks) and test (100 tasks), totaling 1,100 tasks. Each task provides a molecule's SMILES string and asks the agent to predict its LD50 value in log(1/(mol/kg)). Tasks are sampled from the [TDC LD50_Zhu dataset](https://tdcommons.ai/single_pred_tasks/tox/) (7,385 unique molecules).

## Reward Structure

This is a sparse, verifiable reward environment with continuous scoring. The agent calls `submit_prediction` once with a predicted LD50 value. The reward is based on absolute error using inverse hyperbolic cosine scaling:

$$\text{Reward} = \frac{1}{\cosh(|\hat{y} - y|)}$$

| Absolute Error (log units) | Reward |
|---------------------------|--------|
| 0.0 (exact) | 1.000 |
| 0.5 | 0.887 |
| 1.0 | 0.648 |
| 2.0 | 0.266 |

We do not use LLM graders for this task.

## Data

Task data is derived from the [TDC LD50_Zhu dataset](https://tdcommons.ai/single_pred_tasks/tox/), containing experimentally measured LD50 values for 7,385 molecules. Values are in log(1/(mol/kg)). Data files are stored on the OpenReward platform.

## Tools

Agents are given a single tool:

- `submit_prediction`: Submit a predicted LD50 value in log(1/(mol/kg)). Returns the reward based on prediction accuracy. This tool can only be called once per task.

## Time Horizon

LD50Predict is a single-turn environment. The agent receives a molecule and submits one prediction. Each task requires exactly one tool call.

## Environment Difficulty

[Statistics on environment difficulty here]

## Other Environment Requirements

There are no further environment requirements; LD50Predict works out of the box with the OpenReward endpoint.

## Safety

Agents in LD50Predict are asked to predict toxicity values for molecules. The environment does not present direct safety risks, as agents only provide numerical predictions with no access to external systems. However, agents trained on toxicity prediction may acquire knowledge relevant to identifying harmful compounds. The environment evaluates existing published data and does not generate novel toxicity information.

## Citations

```bibtex
@dataset{GRLD50,
  author    = {General Reasoning Inc. Team},
  title     = {LD50},
  year      = {2026},
  publisher = {OpenReward},
  url       = {https://openreward.ai/GeneralReasoning/LD50}
}
```

```bibtex
@article{zhu2009quantitative,
  title={Quantitative structure-activity relationship modeling of rat acute toxicity by oral exposure},
  author={Zhu, Hao and Martin, Todd M and Ye, Lin and Sedykh, Alexander and Young, Douglas M and Tropsha, Alexander},
  journal={Chemical Research in Toxicology},
  volume={22},
  number={12},
  pages={1913--1921},
  year={2009},
  publisher={ACS Publications}
}
```
