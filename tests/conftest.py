import sys
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

SRC_PATH = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_PATH))

from eventos.adapters.orm import metadata, start_mappers

@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session(in_memory_db):
    start_mappers()
    yield sessionmaker(bind=in_memory_db)()
    clear_mappers()


@pytest.fixture
def sqlite_session(session):
    return session