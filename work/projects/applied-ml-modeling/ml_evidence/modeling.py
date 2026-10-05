from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_FOLDS = 5


@dataclass(frozen=True)
class Evaluation:
    accuracy: float
    f1: float
    roc_auc: float


def load_dataset() -> tuple[pd.DataFrame, pd.Series]:
    dataset = load_breast_cancer(as_frame=True)
    frame = dataset.frame.copy()
    target = frame.pop("target")
    return frame, target


def split_dataset(
    X: pd.DataFrame,
    y: pd.Series,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    return train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )


def build_candidate() -> Pipeline:
    return Pipeline(
        steps=[
            ("scale", StandardScaler()),
            (
                "model",
                LogisticRegression(
                    max_iter=5000,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def evaluate(model, X: pd.DataFrame, y: pd.Series) -> Evaluation:
    predictions = model.predict(X)
    probabilities = model.predict_proba(X)[:, 1]
    return Evaluation(
        accuracy=float(accuracy_score(y, predictions)),
        f1=float(f1_score(y, predictions)),
        roc_auc=float(roc_auc_score(y, probabilities)),
    )


def training_cross_validation(
    candidate: Pipeline,
    X_train: pd.DataFrame,
    y_train: pd.Series,
) -> dict[str, dict[str, float]]:
    splitter = StratifiedKFold(
        n_splits=CV_FOLDS,
        shuffle=True,
        random_state=RANDOM_STATE,
    )
    scores = cross_validate(
        candidate,
        X_train,
        y_train,
        cv=splitter,
        scoring={
            "accuracy": "accuracy",
            "f1": "f1",
            "roc_auc": "roc_auc",
        },
        return_train_score=False,
    )

    result: dict[str, dict[str, float]] = {}
    for metric in ("accuracy", "f1", "roc_auc"):
        values = scores[f"test_{metric}"]
        result[metric] = {
            "mean": float(values.mean()),
            "std": float(values.std()),
        }
    return result


def train_and_evaluate(output_dir: str | Path) -> dict:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    X, y = load_dataset()
    X_train, X_test, y_train, y_test = split_dataset(X, y)

    baseline = DummyClassifier(strategy="most_frequent")
    baseline.fit(X_train, y_train)
    baseline_metrics = evaluate(baseline, X_test, y_test)

    candidate = build_candidate()
    cv_metrics = training_cross_validation(candidate, X_train, y_train)
    candidate.fit(X_train, y_train)
    candidate_metrics = evaluate(candidate, X_test, y_test)
    held_out_probabilities = candidate.predict_proba(X_test)[:, 1].tolist()

    model_path = output / "model.joblib"
    metrics_path = output / "metrics.json"
    metadata_path = output / "metadata.json"

    joblib.dump(candidate, model_path)

    metrics = {
        "baseline": asdict(baseline_metrics),
        "candidate": asdict(candidate_metrics),
        "cross_validation_training_only": cv_metrics,
    }
    metrics_path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")

    metadata = {
        "dataset": "sklearn.datasets.load_breast_cancer",
        "benchmark_only": True,
        "random_state": RANDOM_STATE,
        "test_size": TEST_SIZE,
        "cv_folds": CV_FOLDS,
        "rows_total": int(len(X)),
        "rows_train": int(len(X_train)),
        "rows_test": int(len(X_test)),
        "feature_count": int(X.shape[1]),
        "feature_names": list(X.columns),
        "trained_at": datetime.now(timezone.utc).isoformat(),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    return {
        "model_path": str(model_path),
        "metrics_path": str(metrics_path),
        "metadata_path": str(metadata_path),
        "metrics": metrics,
        "test_index": list(X_test.index),
        "held_out_probabilities": held_out_probabilities,
    }


def load_model(path: str | Path):
    return joblib.load(path)
