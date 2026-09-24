from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from eventos.adapters.orm import metadata, start_mappers
from eventos.adapters.repository import SqlAlchemyInscricaoRepository
from eventos.domain.model import (
    Inscricao,
    Organizador,
    Participante,
    RoleOrganizador,
    StatusInscricao,
)


@pytest.fixture
def session():
    start_mappers()
    engine = create_engine("sqlite://")
    metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
    metadata.drop_all(engine)


def criar_participante(identificador=1):
    return Participante(
        identificador=identificador,
        nome=f"Participante {identificador}",
        email=f"participante{identificador}@evento.com",
        documento=f"1234567890{identificador}",
    )


def criar_inscricao(identificador=1, participante=None):
    return Inscricao(
        identificador=identificador,
        participante=participante or criar_participante(),
        lote="Primeiro lote",
    )


def test_adiciona_e_obtem_inscricao_com_participante(session):
    repository = SqlAlchemyInscricaoRepository(session)
    inscricao = criar_inscricao()

    repository.adicionar(inscricao)
    session.commit()
    session.expunge_all()

    encontrada = repository.obter(1)

    assert encontrada.identificador == 1
    assert encontrada.participante.nome == "Participante 1"
    assert encontrada.lote == "Primeiro lote"
    assert encontrada.status is StatusInscricao.PENDENTE


def test_lista_inscricoes_por_participante(session):
    repository = SqlAlchemyInscricaoRepository(session)
    participante = criar_participante()
    repository.adicionar(criar_inscricao(1, participante))
    repository.adicionar(criar_inscricao(2, participante))
    repository.adicionar(criar_inscricao(3, criar_participante(2)))
    session.commit()

    inscricoes = repository.listar_por_participante(participante)

    assert [inscricao.identificador for inscricao in inscricoes] == [1, 2]


def test_atualiza_checkin_e_status_da_inscricao(session):
    repository = SqlAlchemyInscricaoRepository(session)
    inscricao = criar_inscricao()
    repository.adicionar(inscricao)
    session.commit()

    inscricao.confirmar()
    horario = datetime(2026, 9, 23, 10, 30)
    inscricao.realizar_checkin(horario)
    repository.atualizar(inscricao)
    session.commit()
    session.expunge_all()

    encontrada = repository.obter(1)
    assert encontrada.status is StatusInscricao.CONFIRMADA
    assert encontrada.checkin.data_hora == horario


def test_remove_inscricao(session):
    repository = SqlAlchemyInscricaoRepository(session)
    repository.adicionar(criar_inscricao())
    session.commit()

    repository.remover(1)
    session.commit()

    assert repository.obter(1) is None


def test_mapeia_organizador(session):
    organizador = Organizador(
        identificador=1,
        nome="Organizador",
        email="organizador@evento.com",
        role=RoleOrganizador.ADMIN,
    )
    session.add(organizador)
    session.commit()
    session.expunge_all()

    encontrado = session.get(Organizador, 1)

    assert encontrado.role is RoleOrganizador.ADMIN
