"""
SpamGuard AI — Model training pipeline.

Trains and compares four classifiers on a public spam/ham e-mail dataset,
selects the best one based on validation performance, and persists:
  * the trained model
  * the TF-IDF vectorizer
  * the preprocessing configuration
  * full evaluation metrics (accuracy / precision / recall / F1 / confusion matrix)

Usage:
    python server/ml/train_model.py [--dataset path/to/dataset.csv]

If `--dataset` is omitted, the script looks for the Enron spam dataset at
`data/enron_spam_data.csv` relative to the project root and, if missing,
attempts to download it automatically.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

# Allow running the script both as a module and directly.
try:
    from .preprocess import preprocess_email
except ImportError:  # pragma: no cover - direct execution
    from preprocess import preprocess_email

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAVED_MODELS_DIR = Path(__file__).resolve().parent / "saved_models"
DEFAULT_DATASET = PROJECT_ROOT / "data" / "enron_spam_data.csv"

# Official public Enron-Spam dataset (consolidated CSV) used when no local
# file is found. ~33,000 real emails, 17k spam / 16.5k ham.
DATASET_URL = (
    "https://github.com/MWiechmann/enron_spam_data/raw/master/enron_spam_data.zip"
)

RANDOM_STATE = 42
TEST_SIZE = 0.20

# --------------------------------------------------------------------------- #
# Model registry — every model exposes predict_proba for confidence scoring.
# --------------------------------------------------------------------------- #
def _build_models() -> Dict[str, Pipeline]:
    """Return a dict of model name -> sklearn estimator/Pipeline.

    LinearSVC does not natively expose calibrated probabilities, so it is
    wrapped in CalibratedClassifierCV. All other models support predict_proba
    directly.
    """
    return {
        "Multinomial Naive Bayes": MultinomialNB(alpha=0.1),
        "Logistic Regression": LogisticRegression(
            max_iter=1000, C=1.0, random_state=RANDOM_STATE, n_jobs=-1
        ),
        "Linear SVM": CalibratedClassifierCV(
            LinearSVC(C=1.0, max_iter=2000, random_state=RANDOM_STATE), cv=3
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            max_depth=None,
            min_samples_split=3,
            n_jobs=-1,
            random_state=RANDOM_STATE,
        ),
    }


# --------------------------------------------------------------------------- #
# Dataset handling
# --------------------------------------------------------------------------- #
def download_dataset(dest: Path) -> Path:
    """Download and extract the public Enron-Spam CSV if it is not present."""
    import io
    import urllib.request
    import zipfile

    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"[*] Downloading dataset from {DATASET_URL} ...")
    with urllib.request.urlopen(DATASET_URL, timeout=120) as resp:
        payload = resp.read()
    print(f"[*] Downloaded {len(payload) / 1e6:.1f} MB, extracting ...")
    with zipfile.ZipFile(io.BytesIO(payload)) as zf:
        name = zf.namelist()[0]
        with zf.open(name) as src, open(dest, "wb") as out:
            out.write(src.read())
    return dest


def load_and_clean_dataset(path: Path) -> pd.DataFrame:
    """Load the CSV and clean it: drop empty rows, fill NaN, keep only useful
    columns, and map labels to a boolean spam flag."""
    if not path.exists():
        path = download_dataset(path)

    df = pd.read_csv(path)
    print(f"[*] Loaded {len(df)} rows from {path.name}")

    # Normalize column names (defensive against alternate encodings).
    df.columns = [str(c).strip().replace("\ufeff", "") for c in df.columns]
    subject_col = "Subject" if "Subject" in df.columns else df.columns[1]
    message_col = "Message" if "Message" in df.columns else df.columns[2]
    label_col = "Spam/Ham" if "Spam/Ham" in df.columns else df.columns[3]

    df = df[[subject_col, message_col, label_col]].copy()
    df.columns = ["subject", "body", "label"]

    # Drop rows where both subject and body are empty.
    df["subject"] = df["subject"].fillna("").astype(str)
    df["body"] = df["body"].fillna("").astype(str)
    df = df[(df["subject"].str.strip() != "") | (df["body"].str.strip() != "")]
    df = df.drop_duplicates()

    df["label"] = df["label"].str.lower().str.strip()
    df = df[df["label"].isin(["spam", "ham"])]
    df["is_spam"] = (df["label"] == "spam").astype(int)

    print(f"[*] After cleaning: {len(df)} rows "
          f"(spam={int(df['is_spam'].sum())}, ham={int((df['is_spam'] == 0).sum())})")
    return df


# --------------------------------------------------------------------------- #
# Training / evaluation
# --------------------------------------------------------------------------- #
def train_all_models(X_train, y_train, X_test, y_test) -> Dict:
    """Fit every model, score it, and return structured results."""
    models = _build_models()
    results = []
    best_entry = None
    best_model = None

    for name, model in models.items():
        t0 = time.time()
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        probs = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else None

        acc = float(accuracy_score(y_test, preds))
        prec = float(precision_score(y_test, preds, zero_division=0))
        rec = float(recall_score(y_test, preds, zero_division=0))
        f1 = float(f1_score(y_test, preds, zero_division=0))
        cm = confusion_matrix(y_test, preds).tolist()
        elapsed = time.time() - t0

        entry = {
            "model": name,
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1_score": f1,
            "confusion_matrix": cm,
            "train_seconds": round(elapsed, 2),
        }
        results.append(entry)
        if best_entry is None or f1 > best_entry["f1_score"]:
            best_entry = entry
            best_model = model

        print(f"    {name:<28} acc={acc:.4f}  prec={prec:.4f}  "
              f"rec={rec:.4f}  f1={f1:.4f}  ({elapsed:.1f}s)")

    print(f"[*] Best model: {best_entry['model']} (F1={best_entry['f1_score']:.4f})")
    return {"results": results, "best": best_entry, "best_model": best_model}


# --------------------------------------------------------------------------- #
# Main entry point
# --------------------------------------------------------------------------- #
def main() -> None:
    parser = argparse.ArgumentParser(description="Train SpamGuard AI ML model")
    parser.add_argument("--dataset", type=str, default=str(DEFAULT_DATASET))
    parser.add_argument("--max-features", type=int, default=15000)
    parser.add_argument("--ngram", type=int, default=2)
    args = parser.parse_args()

    print("=" * 64)
    print("SpamGuard AI — ML training pipeline")
    print("=" * 64)

    # 1. Load + clean dataset
    df = load_and_clean_dataset(Path(args.dataset))

    # 2. Combine subject + body
    df["text"] = df.apply(
        lambda r: f"{r['subject']} {r['subject']} {r['body']}", axis=1
    )

    # 3. Preprocess
    print("[*] Preprocessing text ...")
    df["clean"] = df["text"].map(preprocess_email_lite)

    # 4. Train/test split (stratified to preserve class balance)
    from sklearn.model_selection import train_test_split

    X_train, X_test, y_train, y_test = train_test_split(
        df["clean"], df["is_spam"], test_size=TEST_SIZE,
        stratify=df["is_spam"], random_state=RANDOM_STATE,
    )
    print(f"[*] Train={len(X_train)}  Test={len(X_test)}")

    # 5. TF-IDF vectorization (fit only on train data)
    print(f"[*] Fitting TF-IDF vectorizer (max_features={args.max_features}, "
          f"ngram_range=(1,{args.ngram})) ...")
    vectorizer = TfidfVectorizer(
        max_features=args.max_features,
        ngram_range=(1, args.ngram),
        min_df=2,
        sublinear_tf=True,
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # 6. Train + evaluate all models
    print("[*] Training & evaluating models ...")
    outcome = train_all_models(X_train_vec, y_train, X_test_vec, y_test)
    best = outcome["best"]
    best_model = outcome["best_model"]

    # 7. Persist artifacts
    SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model_path = SAVED_MODELS_DIR / "model.joblib"
    vectorizer_path = SAVED_MODELS_DIR / "vectorizer.joblib"
    config_path = SAVED_MODELS_DIR / "preprocess_config.json"
    metrics_path = SAVED_MODELS_DIR / "metrics.json"

    joblib.dump(best_model, model_path)
    joblib.dump(vectorizer, vectorizer_path)

    config = {
        "preprocessing": {
            "lowercase": True,
            "strip_html": True,
            "strip_urls": True,
            "normalize_numbers": True,
            "remove_stopwords": True,
            "stemming": False,
            "subject_weight": 2,
            "tokenizer": "nltk.word_tokenize (regex fallback)",
        },
        "vectorizer": {
            "max_features": args.max_features,
            "ngram_range": [1, args.ngram],
            "min_df": 2,
            "sublinear_tf": True,
        },
        "best_model": best["model"],
        "dataset": {
            "name": "Enron-Spam (Metsis, Androutsopoulos & Paliouras)",
            "source": DATASET_URL,
            "rows": int(len(df)),
            "spam": int(df["is_spam"].sum()),
            "ham": int((df["is_spam"] == 0).sum()),
            "test_size": TEST_SIZE,
            "random_state": RANDOM_STATE,
        },
        "trained_at": datetime.now(timezone.utc).isoformat() + "Z",
    }
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    metrics = {
        "best_model": best["model"],
        "trained_at": config["trained_at"],
        "models": outcome["results"],
        "dataset": config["dataset"],
    }
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print("[*] Artifacts saved to", SAVED_MODELS_DIR)
    print("    - model.joblib")
    print("    - vectorizer.joblib")
    print("    - preprocess_config.json")
    print("    - metrics.json")
    print("\nEvaluation summary:")
    for r in outcome["results"]:
        print(f"  {r['model']:<28} F1={r['f1_score']:.4f}  Acc={r['accuracy']:.4f}")


def preprocess_email_lite(text: str) -> str:
    """Preprocess a single combined subject+body string (shared helper)."""
    from preprocess import preprocess_text

    return preprocess_text(text, stem=False)


if __name__ == "__main__":
    main()
