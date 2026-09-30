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

    with app.test_client() as test_client:
        yield test_client

    session.close()
    engine.dispose()


def dados_do_evento():
    return {
        "nome": "Conferencia de Software",
        "data": "2026-10-20",
        "local": "Niteroi",
    }


def test_cria_evento_e_consulta_por_identificador(client):
    resposta = client.post("/eventos", json=dados_do_evento())

    assert resposta.status_code == 201
    assert resposta.get_json() == {
        "identificador": 1,
        "nome": "Conferencia de Software",
        "data": "2026-10-20",
        "local": "Niteroi",
        "status": "planejado",
    }

    resposta = client.get("/eventos/1")

    assert resposta.status_code == 200
    assert resposta.get_json()["nome"] == "Conferencia de Software"


def test_lista_eventos(client):
    client.post("/eventos", json=dados_do_evento())

    resposta = client.get("/eventos")

    assert resposta.status_code == 200
    assert len(resposta.get_json()) == 1


def test_criacao_de_evento_exige_campos_obrigatorios(client):
    resposta = client.post("/eventos", json={"nome": "Sem data"})

    assert resposta.status_code == 400
    assert "data" in resposta.get_json()["erro"]


def test_retorna_404_para_evento_inexistente(client):
    resposta = client.get("/eventos/999")

    assert resposta.status_code == 404
    assert resposta.get_json()["erro"] == "evento nao encontrado"


def test_encerramento_informa_dependencia_de_listagem_de_inscricoes(client):
    client.post("/eventos", json=dados_do_evento())

    resposta = client.post("/eventos/1/encerrar")

    assert resposta.status_code == 501
    assert "listar_por_evento" in resposta.get_json()["erro"]