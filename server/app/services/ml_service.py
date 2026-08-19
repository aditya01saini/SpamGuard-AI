"""
Service: ML model access.

Wraps the `server/ml` package so the rest of the app talks to a single
predictor interface. The model is loaded once at application startup (see
`app/main.py` lifespan) and reused for every request.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict

# Ensure `server/ml` is importable regardless of the working directory.
_ML_DIR = Path(__file__).resolve().parents[2] / "ml"
if str(_ML_DIR) not in sys.path:
    sys.path.insert(0, str(_ML_DIR))

from ml.predict import SpamClassifier, ModelUnavailableError  # noqa: E402


class MLService:
    def __init__(self, models_dir: str):
        self.classifier = SpamClassifier(Path(models_dir))

    def load(self) -> None:
        self.classifier.load()

    @property
    def is_loaded(self) -> bool:
        return self.classifier.is_loaded

    @property
    def model_name(self) -> str:
        return self.classifier.model_name

    @property
    def metrics(self) -> Dict:
        return self.classifier.metrics

    @property
    def config(self) -> Dict:
        return self.classifier.config

    def predict(self, subject: str, body: str) -> Dict:
        return self.classifier.predict(subject, body)


__all__ = ["MLService", "ModelUnavailableError"]
