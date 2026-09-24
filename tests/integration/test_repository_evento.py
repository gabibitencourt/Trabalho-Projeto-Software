from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import clear_mappers, sessionmaker

from eventos.adapters.orm import metadata, start_mappers
from eventos.adapters.repository import SqlAlchemyEventoRepository
from eventos.domain.model import Evento, LoteDeIngresso, StatusEvento


@pytest.fixture
def repository():
    start_mappers()
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    try:
        yield SqlAlchemyEventoRepository(session), session
    finally:
        session.close()
        engine.dispose()
        clear_mappers()


def criar_evento(identificador=1):
    return Evento(
        identificador=identificador,
        nome="Conferencia de Software",
        data=date(2026, 10, 20),
        local="Niteroi",
        status=StatusEvento.PLANEJADO,
    )


def test_adicionar_e_obter_evento(repository):
    evento_repository, session = repository
    evento = criar_evento()

    evento_repository.adicionar(evento)
    session.commit()
    session.expire_all()

    evento_recuperado = evento_repository.obter(1)

    assert evento_recuperado.nome == evento.nome
    assert evento_recuperado.data == evento.data
    assert evento_recuperado.status is StatusEvento.PLANEJADO


def test_atualizar_evento_persiste_mudanca_de_status(repository):
    evento_repository, session = repository
    evento = criar_evento()
    evento_repository.adicionar(evento)
    session.commit()

    evento.iniciar()
    evento_repository.atualizar(evento)
    session.commit()
    session.expire_all()

    assert evento_repository.obter(1).status is StatusEvento.EM_ANDAMENTO


def test_adicionar_evento_persiste_seus_lotes(repository):
    evento_repository, session = repository
    evento = criar_evento()
    evento.adicionar_lote(LoteDeIngresso(1, "Inteira", 100, 50))

    evento_repository.adicionar(evento)
    session.commit()
    session.expire_all()

    evento_recuperado = evento_repository.obter(1)

    assert len(evento_recuperado.lotes) == 1
    assert evento_recuperado.lotes[0].nome == "Inteira"


def test_listar_retorna_todos_os_eventos(repository):
    evento_repository, session = repository
    evento_repository.adicionar(criar_evento(1))
    evento_repository.adicionar(criar_evento(2))
    session.commit()

    eventos = evento_repository.listar()

    assert {evento.identificador for evento in eventos} == {1, 2}
