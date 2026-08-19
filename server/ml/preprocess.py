"""
SpamGuard AI — Text preprocessing pipeline.

This module contains the reusable NLP preprocessing used BOTH during model
training and at inference time. Keeping it in a single shared module guarantees
that the text an email goes through at prediction time is *identical* to the
text the model was trained on (same cleaning, tokenization, stop-word removal,
etc.). This is critical: a mismatch between train-time and predict-time text
would silently degrade model accuracy.
"""

from __future__ import annotations

import html
import re
from typing import List, Optional

# --------------------------------------------------------------------------- #
# Constants / compiled regexes (compiled once for performance)
# --------------------------------------------------------------------------- #

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_EMAIL_RE = re.compile(r"\S+@\S+")
_NUMBER_RE = re.compile(r"\b\d+(?:[.,]\d+)*\b")
_NON_ALPHA_RE = re.compile(r"[^a-z0-9\s]")
_MULTI_SPACE_RE = re.compile(r"\s+")

# Fallback stop-word list (used only if the NLTK corpus is unavailable, e.g.
# in an offline environment). Mirrors the most common English stop words.
_FALLBACK_STOPWORDS = {
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your",
    "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she",
    "her", "hers", "herself", "it", "its", "itself", "they", "them", "their",
    "theirs", "themselves", "what", "which", "who", "whom", "this", "that",
    "these", "those", "am", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an",
    "the", "and", "but", "if", "or", "because", "as", "until", "while", "of",
    "at", "by", "for", "with", "about", "against", "between", "into", "through",
    "during", "before", "after", "above", "below", "to", "from", "up", "down",
    "in", "out", "on", "off", "over", "under", "again", "further", "then",
    "once", "here", "there", "when", "where", "why", "how", "all", "any",
    "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor",
    "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can",
    "will", "just", "don", "should", "now", "d", "ll", "m", "o", "re", "ve",
    "y", "ain", "aren", "couldn", "didn", "doesn", "hadn", "hasn", "haven",
    "isn", "ma", "mightn", "mustn", "needn", "shan", "shouldn", "wasn", "weren",
    "won", "wouldn",
}


def _load_stopwords() -> set:
    """Return the English stop-word set, using NLTK when available and falling
    back to a bundled list otherwise."""
    try:
        from nltk.corpus import stopwords

        words = set(stopwords.words("english"))
        if words:
            return words
    except Exception:
        pass
    return set(_FALLBACK_STOPWORDS)


STOPWORDS = _load_stopwords()


# --------------------------------------------------------------------------- #
# Individual preprocessing steps
# --------------------------------------------------------------------------- #

def strip_html(text: str) -> str:
    """Remove HTML tags and decode HTML entities (e.g. &amp; -> &)."""
    if not text:
        return ""
    text = _HTML_TAG_RE.sub(" ", text)
    text = html.unescape(text)
    return text


def strip_urls_and_emails(text: str) -> str:
    """Replace raw URLs and e-mail addresses with space tokens.

    URLs rarely carry useful signal for a bag-of-words classifier and inflate
    the feature space with unique junk tokens."""
    text = _URL_RE.sub(" ", text)
    text = _EMAIL_RE.sub(" ", text)
    return text


def _replace_numbers(text: str) -> str:
    """Normalise digit sequences to a single `number` token.

    Helps the model generalise (e.g. '1000' and '100000' become equivalent)."""
    return _NUMBER_RE.sub(" number ", text)


def tokenize(text: str) -> List[str]:
    """Lowercase + tokenize using NLTK's punkt tokenizer with a regex fallback."""
    text = text.lower()
    try:
        from nltk.tokenize import word_tokenize

        return word_tokenize(text)
    except Exception:
        return text.split()


def remove_stopwords(tokens: List[str]) -> List[str]:
    return [t for t in tokens if t not in STOPWORDS]


def stem_tokens(tokens: List[str]) -> List[str]:
    """Optional Porter stemming (reduces vocabulary, improves generalization)."""
    try:
        from nltk.stem import PorterStemmer

        stemmer = PorterStemmer()
        return [stemmer.stem(t) for t in tokens]
    except Exception:
        return tokens


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #

def preprocess_text(text: str, *, stem: bool = True) -> str:
    """Full preprocessing pipeline: returns a normalized, space-joined string.

    Order of operations:
      1. HTML removal
      2. URL / e-mail removal
      3. number normalization
      4. lowercase + tokenization
      5. stop-word removal
      6. optional stemming
      7. whitespace normalization
    """
    if not text:
        return ""

    text = strip_html(text)
    text = strip_urls_and_emails(text)
    text = text.lower()
    text = _replace_numbers(text)
    # Drop punctuation / special characters (already lowercased).
    text = _NON_ALPHA_RE.sub(" ", text)

    tokens = text.split()
    tokens = remove_stopwords(tokens)
    if stem:
        tokens = stem_tokens(tokens)

    return " ".join(tokens)


def combine_subject_body(subject: Optional[str], body: Optional[str]) -> str:
    """Combine the subject and body into a single analyzable string.

    The subject is repeated to give it extra weight (subject lines are short
    but highly informative for spam/phishing detection)."""
    subject = (subject or "").strip()
    body = (body or "").strip()
    parts = []
    if subject:
        # Weight subject by repeating it — a common, effective heuristic.
        parts.append(f"{subject} {subject}")
    if body:
        parts.append(body)
    return " ".join(parts)


def preprocess_email(subject: Optional[str], body: Optional[str], *,
                     stem: bool = True) -> str:
    """Convenience wrapper: combine subject+body then preprocess."""
    combined = combine_subject_body(subject, body)
    return preprocess_text(combined, stem=stem)


__all__ = [
    "preprocess_text",
    "preprocess_email",
    "combine_subject_body",
    "strip_html",
    "tokenize",
    "remove_stopwords",
    "STOPWORDS",
]
