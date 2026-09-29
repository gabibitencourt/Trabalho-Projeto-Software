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

def test_realiza_checkin_com_sucesso(client):
    # 1. Cria a inscrição (ela nasce como PENDENTE)
    client.post("/inscricoes", json=dados_da_inscricao())
    
    # 2. Confirma a inscrição (regra do domínio exige isso para o check-in)
    client.post("/inscricoes/1/confirmar")

    # 3. Realiza o check-in
    resposta = client.post("/inscricoes/1/checkin")

    assert resposta.status_code == 200
    # Valida se a chave 'checkin' não é mais nula, conforme sua serialização
    assert resposta.get_json()["checkin"] is not None


def test_nao_permite_checkin_em_inscricao_pendente(client):
    # 1. Cria a inscrição (ela nasce como PENDENTE)
    client.post("/inscricoes", json=dados_da_inscricao())

    # 2. Tenta fazer check-in direto, sem confirmar
    resposta = client.post("/inscricoes/1/checkin")

    # 3. Deve falhar com erro 400 (OperacaoInvalidaError)
    assert resposta.status_code == 400
    assert "check-in exige inscricao confirmada" in resposta.get_json()["erro"]