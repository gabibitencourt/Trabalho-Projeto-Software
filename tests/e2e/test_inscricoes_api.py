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


def dados_da_inscricao():
    return {
        "identificador": 1,
        "participante": {
            "identificador": 1,
            "nome": "Samuel Dias",
            "email": "samuel@evento.com",
            "documento": "12345678900",
        },
        "lote": "Primeiro lote",
    }


def test_cria_e_consulta_inscricao(client):
    resposta = client.post("/inscricoes", json=dados_da_inscricao())

    assert resposta.status_code == 201
    assert resposta.get_json()["status"] == "pendente"

    resposta = client.get("/inscricoes/1")

    assert resposta.status_code == 200
    assert resposta.get_json()["participante"]["nome"] == "Samuel Dias"


def test_confirma_inscricao(client):
    client.post("/inscricoes", json=dados_da_inscricao())

    resposta = client.post("/inscricoes/1/confirmar")

    assert resposta.status_code == 200
    assert resposta.get_json()["status"] == "confirmada"


def test_cancela_inscricao(client):
    client.post("/inscricoes", json=dados_da_inscricao())

    resposta = client.post("/inscricoes/1/cancelar")

    assert resposta.status_code == 200
    assert resposta.get_json()["status"] == "cancelada"


def test_retorna_404_para_inscricao_inexistente(client):
    resposta = client.get("/inscricoes/999")

    assert resposta.status_code == 404
    assert resposta.get_json()["erro"] == "inscricao nao encontrada"
