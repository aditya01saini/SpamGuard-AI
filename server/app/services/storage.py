"""
Service: persistence layer (MongoDB with in-memory fallback).

Uses MongoDB when configured & reachable; otherwise falls back to an
in-memory store so the application keeps working (and keeps degrading
gracefully). Both backends expose the same interface.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from app.config import settings
from app.utils.logging import logger


class StorageInterface:
    def insert_scan(self, scan: Dict) -> str: ...
    def list_scans(self, limit: int, skip: int,
                   classification: Optional[str]) -> List[Dict]: ...
    def get_scan(self, scan_id: str) -> Optional[Dict]: ...
    def delete_scan(self, scan_id: str) -> bool: ...
    def count_scans(self) -> int: ...
    def analytics(self) -> Dict: ...


class MongoStorage(StorageInterface):
    """MongoDB-backed storage with a `scans` collection."""

    def __init__(self, uri: str, db_name: str):
        import pymongo
        from pymongo import MongoClient

        self.client = MongoClient(uri, serverSelectionTimeoutMS=3000)
        self.db = self.client[db_name]
        self.collection = self.db["scans"]
        # Useful indexes.
        self.collection.create_index("timestamp", background=True)
        self.collection.create_index("classification", background=True)
        self.collection.create_index("risk_score", background=True)

    def _doc(self, scan: Dict) -> Dict:
        return scan

    def insert_scan(self, scan: Dict) -> str:
        self.collection.insert_one(scan)
        return scan["_id"]

    def list_scans(self, limit: int, skip: int,
                   classification: Optional[str]) -> List[Dict]:
        query = {}
        if classification:
            query["classification"] = classification.upper()
        cursor = self.collection.find(query).sort("timestamp", -1) \
            .skip(skip).limit(limit)
        return [d for d in cursor]

    def get_scan(self, scan_id: str) -> Optional[Dict]:
        return self.collection.find_one({"_id": scan_id})

    def delete_scan(self, scan_id: str) -> bool:
        return self.collection.delete_one({"_id": scan_id}).deleted_count > 0

    def count_scans(self) -> int:
        return self.collection.count_documents({})

    def analytics(self) -> Dict:
        pipeline = [
            {"$group": {"_id": "$classification", "count": {"$sum": 1}}},
        ]
        classification_counts = {r["_id"]: r["count"]
                                 for r in self.collection.aggregate(pipeline)}
        risk_counts = {r["_id"]: r["count"] for r in self.collection.aggregate([
            {"$group": {"_id": "$risk_level", "count": {"$sum": 1}}},
        ])}
        avg_risk = list(self.collection.aggregate([
            {"$group": {"_id": None, "avg": {"$avg": "$risk_score"}}},
        ]))
        avg_risk_val = avg_risk[0]["avg"] if avg_risk else 0.0
        return {
            "total_scans": self.count_scans(),
            "classification_counts": classification_counts,
            "risk_counts": risk_counts,
            "average_risk_score": round(avg_risk_val or 0.0, 2),
        }


class InMemoryStorage(StorageInterface):
    """Fallback in-memory store (not persisted across restarts)."""

    def __init__(self):
        self.scans: Dict[str, Dict] = {}

    def insert_scan(self, scan: Dict) -> str:
        self.scans[scan["_id"]] = scan
        return scan["_id"]

    def list_scans(self, limit: int, skip: int,
                   classification: Optional[str]) -> List[Dict]:
        items = sorted(self.scans.values(),
                       key=lambda s: s.get("timestamp", ""), reverse=True)
        if classification:
            items = [s for s in items
                     if s.get("classification") == classification.upper()]
        return items[skip:skip + limit]

    def get_scan(self, scan_id: str) -> Optional[Dict]:
        return self.scans.get(scan_id)

    def delete_scan(self, scan_id: str) -> bool:
        return self.scans.pop(scan_id, None) is not None

    def count_scans(self) -> int:
        return len(self.scans)

    def analytics(self) -> Dict:
        cls_counts: Dict[str, int] = {}
        risk_counts: Dict[str, int] = {}
        risk_total = 0.0
        for s in self.scans.values():
            cls_counts[s.get("classification", "UNKNOWN")] = \
                cls_counts.get(s.get("classification", "UNKNOWN"), 0) + 1
            risk_counts[s.get("risk_level", "LOW")] = \
                risk_counts.get(s.get("risk_level", "LOW"), 0) + 1
            risk_total += s.get("risk_score", 0)
        n = len(self.scans)
        return {
            "total_scans": n,
            "classification_counts": cls_counts,
            "risk_counts": risk_counts,
            "average_risk_score": round(risk_total / n, 2) if n else 0.0,
        }


def build_storage() -> StorageInterface:
    """Create the best available storage backend."""
    try:
        store = MongoStorage(settings.mongodb_uri, settings.mongodb_db_name)
        # Verify connectivity.
        store.client.admin.command("ping")
        logger.info("Connected to MongoDB at %s", settings.mongodb_uri)
        return store
    except Exception as exc:
        logger.warning(
            "MongoDB unavailable (%s). Using in-memory fallback storage.", exc
        )
        return InMemoryStorage()


# Singleton.
storage: StorageInterface = build_storage()
