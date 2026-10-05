# Applied ML Modeling — Evidence Build

## Referent

Build one inspectable machine-learning workflow that proves model-development ability rather than another general software platform.

The first slice uses scikit-learn's packaged Wisconsin Diagnostic Breast Cancer benchmark dataset because it is deterministic, widely used, requires no private/client data, and can run in clean CI without a network dependency.

**This is a modeling benchmark only. It is not a clinical decision system and no medical-use claim is made.**

## Ability witness

The project must prove:

- explicit train/test separation;
- preprocessing fitted inside a scikit-learn Pipeline rather than on the full dataset;
- a simple baseline model;
- a trained predictive model;
- measured held-out metrics;
- cross-validation on the training partition;
- reproducible random state;
- serialized model artifact;
- artifact reload with equivalent inference;
- machine-readable metrics and metadata;
- automated acceptance tests.

## First model

Baseline:
- `DummyClassifier(strategy="most_frequent")`

Candidate:
- `StandardScaler`
- `LogisticRegression`

The point is not model novelty. The point is to prove correct modeling boundaries and measurable improvement over a trivial baseline.

## Acceptance

- held-out test data is not used to fit preprocessing or the model;
- candidate ROC AUC must exceed the dummy baseline;
- candidate ROC AUC must exceed 0.90 on the fixed benchmark split;
- 5-fold stratified CV metrics are recorded from training data only;
- model artifact reload reproduces the same predictions;
- metrics and run metadata are written to disk;
- clean GitHub Actions run passes.

## Boundary

This closes a first **Machine Learning / Applied AI** witness if CI passes. It does not claim deep learning, LLM engineering, MLOps production deployment, or clinical utility.
