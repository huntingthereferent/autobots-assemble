from pathlib import Path

import joblib

from ml_evidence.modeling import (
    load_dataset,
    load_model,
    split_dataset,
    train_and_evaluate,
)


def test_train_test_split_is_disjoint():
    X, y = load_dataset()
    X_train, X_test, y_train, y_test = split_dataset(X, y)

    assert set(X_train.index).isdisjoint(set(X_test.index))
    assert set(y_train.index) == set(X_train.index)
    assert set(y_test.index) == set(X_test.index)


def test_candidate_beats_baseline_and_acceptance_threshold(tmp_path: Path):
    result = train_and_evaluate(tmp_path)

    baseline = result["metrics"]["baseline"]
    candidate = result["metrics"]["candidate"]
    cv = result["metrics"]["cross_validation_training_only"]

    assert candidate["roc_auc"] > baseline["roc_auc"]
    assert candidate["roc_auc"] > 0.90
    assert 0.0 <= candidate["accuracy"] <= 1.0
    assert 0.0 <= candidate["f1"] <= 1.0
    assert cv["roc_auc"]["mean"] > 0.90


def test_model_artifact_reloads_with_equivalent_inference(tmp_path: Path):
    result = train_and_evaluate(tmp_path)
    model = load_model(result["model_path"])

    X, y = load_dataset()
    _, X_test, _, _ = split_dataset(X, y)
    sample = X_test.head(10)

    before = joblib.load(result["model_path"]).predict_proba(sample)
    after = model.predict_proba(sample)

    assert before.shape == after.shape
    assert (before == after).all()


def test_machine_readable_artifacts_are_written(tmp_path: Path):
    result = train_and_evaluate(tmp_path)

    assert Path(result["model_path"]).is_file()
    assert Path(result["metrics_path"]).is_file()
    assert Path(result["metadata_path"]).is_file()
