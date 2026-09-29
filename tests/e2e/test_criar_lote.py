import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from eventos.adapters.orm import metadata, start_mappers
from eventos.entrypoints.flask_app import create_app


@pytest.fixture
def client():
    start_mappers()
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    app = create_app(session)
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client

    session.close()
    engine.dispose()

def dados_lote():
    return{
        "identificador": 1,
        "event_id": 1,
        "nome": "Primeiro lote",
        "preco": 67,
        "quant_total": 100,
        "quant_vendida": 0,
    }

def test_cria_lote_errado(client):
    
    resposta = client.post("/lote", json=dados_lote())

    assert resposta.status_code == 404


