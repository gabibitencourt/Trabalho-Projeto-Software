import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from eventos.adapters.orm import metadata, start_mappers
from eventos.adapters.repository import SqlAlchemyInscricaoRepository
from eventos.domain.model import Inscricao, Participante
from eventos.entrypoints.flask_app import create_app


@pytest.fixture
def session():
    start_mappers()
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return sessionmaker(bind=engine)()


@pytest.fixture
def client(session):
    app = create_app(session)
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client

    session.close()


def _criar_inscricao(session, identificador=1):
    participante = Participante(
        identificador=identificador,
        nome=f"Participante {identificador}",
        email=f"participante{identificador}@evento.com",
        documento=f"1234567890{identificador}",
    )
    repositorio = SqlAlchemyInscricaoRepository(session)
    repositorio.adicionar(
        Inscricao(identificador=identificador, participante=participante, lote="Primeiro lote")
    )
    session.commit()


def test_registra_e_consulta_pagamento(session, client):
    _criar_inscricao(session)

    resposta = client.post(
        "/pagamentos",
        json={"identificador": 1, "inscricao_id": 1, "valor": 150},
    )

    assert resposta.status_code == 201
    assert resposta.get_json()["status"] == "pendente"

    resposta = client.get("/pagamentos/1")

    assert resposta.status_code == 200
    assert resposta.get_json()["valor"] == 150


def test_registra_pagamento_para_inscricao_inexistente(session, client):
    resposta = client.post(
        "/pagamentos",
        json={"identificador": 1, "inscricao_id": 999, "valor": 150},
    )

    assert resposta.status_code == 404


def test_aprova_pagamento_e_confirma_inscricao(session, client):
    _criar_inscricao(session)
    client.post("/pagamentos", json={"identificador": 1, "inscricao_id": 1, "valor": 150})

    resposta = client.post("/pagamentos/1/aprovar")
    assert resposta.status_code == 200
    assert resposta.get_json()["status"] == "aprovado"

    resposta = client.post("/pagamentos/1/confirmar-inscricao")
    assert resposta.status_code == 200
    assert resposta.get_json()["status"] == "confirmada"


def test_recusa_pagamento(session, client):
    _criar_inscricao(session)
    client.post("/pagamentos", json={"identificador": 1, "inscricao_id": 1, "valor": 150})

    resposta = client.post("/pagamentos/1/recusar")

    assert resposta.status_code == 200
    assert resposta.get_json()["status"] == "recusado"


def test_nao_confirma_inscricao_com_pagamento_pendente(session, client):
    _criar_inscricao(session)
    client.post("/pagamentos", json={"identificador": 1, "inscricao_id": 1, "valor": 150})

    resposta = client.post("/pagamentos/1/confirmar-inscricao")

    assert resposta.status_code == 400


def test_retorna_404_para_pagamento_inexistente(session, client):
    resposta = client.get("/pagamentos/999")

    assert resposta.status_code == 404
