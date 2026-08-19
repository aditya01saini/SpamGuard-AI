"""ML layer tests: preprocessing, model loading, and prediction."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SERVER_DIR = Path(__file__).resolve().parents[1]
ML_DIR = SERVER_DIR / "ml"
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))
if str(ML_DIR) not in sys.path:
    sys.path.insert(0, str(ML_DIR))

from preprocess import preprocess_text, combine_subject_body, strip_html  # noqa: E402
from predict import SpamClassifier, ModelUnavailableError  # noqa: E402

SAVED = ML_DIR / "saved_models"


class TestPreprocessing:
    def test_lowercase_and_html_removal(self):
        out = preprocess_text("<b>Hello</b> WORLD")
        assert "<" not in out and ">" not in out
        assert "world" in out

    def test_stopword_removal(self):
        out = preprocess_text("this is a test email")
        # 'is', 'a', 'this' are stopwords and should be removed.
        for sw in ("is", "a", "this"):
            assert sw not in out.split()

    def test_special_chars_and_whitespace(self):
        out = preprocess_text("Click   here!!! now   ")
        assert "  " not in out
        assert "!!!" not in out

    def test_combine_subject_body_weights_subject(self):
        combined = combine_subject_body("invoice", "please pay")
        assert combined.count("invoice") == 2  # subject repeated for weight

    def test_empty_input(self):
        assert preprocess_text("") == ""
        assert preprocess_text(None) == ""


class TestModelLoading:
    def test_load_trained_model(self):
        clf = SpamClassifier(SAVED)
        clf.load()
        assert clf.is_loaded
        assert clf.model_name

    def test_missing_model_raises(self, tmp_path):
        clf = SpamClassifier(tmp_path)
        with pytest.raises(ModelUnavailableError):
            clf.load()


class TestPrediction:
    @pytest.fixture(scope="class")
    def clf(self):
        c = SpamClassifier(SAVED)
        c.load()
        return c

    def test_spam_email(self, clf):
        res = clf.predict(
            "URGENT verify your account now",
            "Click here to confirm your password and credit card number",
        )
        assert res["label"] in ("SPAM", "POSSIBLE PHISHING")

    def test_safe_email(self, clf):
        res = clf.predict(
            "Team meeting agenda",
            "Hi team, please review the attached agenda before our Monday sync.",
        )
        assert res["label"] == "SAFE"

    def test_probabilities_sum_to_one(self, clf):
        res = clf.predict("test subject", "some normal body text here")
        assert abs(res["spam_probability"] + res["safe_probability"] - 1.0) < 1e-6
