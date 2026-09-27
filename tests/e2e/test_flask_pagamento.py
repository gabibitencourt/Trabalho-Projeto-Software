import pytest
from sqlalchemy.orm import clear_mappers

from eventos.adapters.repository import SqlAlchemyInscricaoRepository
from eventos.domain.model import Inscricao, Participante
from eventos.entrypoints.flask_app import create_app


@pytest.fixture
def app():
    aplicacao = create_app("sqlite:///:memory:")
    yield aplicacao
    clear_mappers()


@pytest.fixture
def client(app):
    return app.test_client()


def _criar_inscricao(app, identificador=1):
    session = app.session_factory()
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
    session.close()


def test_processa_pagamento_aprovado(app, client):
    _criar_inscricao(app)

    resposta = client.post(
        "/pagamentos",
        json={"identificador": 1, "inscricao_id": 1, "valor": 150, "aprovado": True},
    )

    assert resposta.status_code == 201
    assert resposta.get_json() == {"identificador": 1, "status": "aprovado"}


def test_processa_pagamento_para_inscricao_inexistente(app, client):
    resposta = client.post(
        "/pagamentos",
        json={"identificador": 1, "inscricao_id": 999, "valor": 150, "aprovado": True},
    )

    assert resposta.status_code == 400


def test_confirma_inscricao_apos_pagamento_aprovado(app, client):
    _criar_inscricao(app)
    client.post(
        "/pagamentos",
        json={"identificador": 1, "inscricao_id": 1, "valor": 150, "aprovado": True},
    )

    resposta = client.post("/pagamentos/1/confirmar-inscricao")

    assert resposta.status_code == 200


def test_nao_confirma_inscricao_com_pagamento_recusado(app, client):
    _criar_inscricao(app)
    client.post(
        "/pagamentos",
        json={"identificador": 1, "inscricao_id": 1, "valor": 150, "aprovado": False},
    )

    resposta = client.post("/pagamentos/1/confirmar-inscricao")

    assert resposta.status_code == 400
