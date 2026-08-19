"""
SpamGuard AI — Inference (prediction) module.

Loads the persisted model + vectorizer once and exposes a `predict` function
used by the API. The model is NOT retrained on each request.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

import joblib
import numpy as np

try:
    from .preprocess import preprocess_email
except ImportError:  # pragma: no cover - direct execution
    from preprocess import preprocess_email

SAVED_MODELS_DIR = Path(__file__).resolve().parent / "saved_models"


class ModelUnavailableError(RuntimeError):
    """Raised when the trained model artifacts cannot be loaded."""


class SpamClassifier:
    """Thin wrapper around the persisted sklearn pipeline."""

    def __init__(self, models_dir: Path = SAVED_MODELS_DIR):
        self.models_dir = Path(models_dir)
        self.model = None
        self.vectorizer = None
        self.config: Dict = {}
        self.metrics: Dict = {}
        self._loaded = False

    def load(self) -> None:
        """Load model, vectorizer and config from disk (called once at startup)."""
        model_path = self.models_dir / "model.joblib"
        vectorizer_path = self.models_dir / "vectorizer.joblib"
        config_path = self.models_dir / "preprocess_config.json"
        metrics_path = self.models_dir / "metrics.json"

        missing = [p.name for p in (model_path, vectorizer_path) if not p.exists()]
        if missing:
            raise ModelUnavailableError(
                f"Model artifacts missing ({', '.join(missing)}). "
                f"Run `python server/ml/train_model.py` first."
            )

        self.model = joblib.load(model_path)
        self.vectorizer = joblib.load(vectorizer_path)

        if config_path.exists():
            self.config = json.loads(config_path.read_text())
        if metrics_path.exists():
            self.metrics = json.loads(metrics_path.read_text())

        self._loaded = True

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def model_name(self) -> str:
        return self.config.get("best_model", "Unknown")

    def predict(self, subject: str, body: str) -> Dict:
        """Classify an email, returning spam probability and class label."""
        if not self._loaded:
            raise ModelUnavailableError("Model not loaded.")

        # Preprocess using the EXACT same pipeline as training.
        clean = preprocess_email(subject, body, stem=False)
        vec = self.vectorizer.transform([clean])

        is_spam = int(self.model.predict(vec)[0])

        # Calibrated probabilities (falls back to decision_function sign).
        try:
            proba = self.model.predict_proba(vec)[0]
            spam_prob = float(proba[1]) if len(proba) > 1 else float(is_spam)
        except (AttributeError, IndexError):
            spam_prob = float(is_spam)

        safe_prob = 1.0 - spam_prob
        label = "SPAM" if is_spam == 1 else "SAFE"

        return {
            "label": label,
            "is_spam": bool(is_spam),
            "spam_probability": round(spam_prob, 4),
            "safe_probability": round(safe_prob, 4),
            "model": self.model_name,
        }


# Singleton instance shared across the application.
classifier = SpamClassifier()


def get_classifier() -> SpamClassifier:
    return classifier


__all__ = ["SpamClassifier", "get_classifier", "ModelUnavailableError"]
