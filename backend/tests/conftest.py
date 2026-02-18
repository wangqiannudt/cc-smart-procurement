import os
import sys

import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.core.database import SessionLocal, init_db
from app.models.analysis_history import AnalysisHistory


@pytest.fixture(autouse=True)
def clean_analysis_history():
    """Keep analysis history tests deterministic and repeatable."""
    init_db()
    db = SessionLocal()
    try:
        db.query(AnalysisHistory).delete()
        db.commit()
    finally:
        db.close()

    yield

    db = SessionLocal()
    try:
        db.query(AnalysisHistory).delete()
        db.commit()
    finally:
        db.close()
