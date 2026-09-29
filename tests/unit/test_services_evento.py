from datetime import date
from types import SimpleNamespace

import pytest

from eventos.adapters.repository import FakeEventoRepository
from eventos.domain.model import (
    Evento,
    OperacaoInvalidaError,
    StatusEvento,
    StatusInscricao,
)
from eventos.service_layer.services import criar_evento, encerrar_evento


class FakeInscricaoRepository:
    def __init__(self, inscricoes=()):
        self.inscricoes = list(inscricoes)

    def listar_por_evento(self, identificador_evento):
        return [
            inscricao
            for inscricao in self.inscricoes
            if inscricao.evento_id == identificador_evento
        ]


def evento_teste(identificador=1, status=StatusEvento.EM_ANDAMENTO):
    return Evento(
        identificador=identificador,
        nome="Conferencia",
        data=date(2026, 10, 20),
        local="Niteroi",
        status=status,
    )


def inscricao_teste(evento_id, status):
    return SimpleNamespace(evento_id=evento_id, status=status)


def test_criar_evento_salva_e_retorna_identificador():
    repositorio = FakeEventoRepository()

    identificador = criar_evento(
        repositorio,
        nome="Conferencia",
        data="2026-10-20",
        local="Niteroi",
    )

    evento = repositorio.obter(identificador)
    assert identificador == 1
    assert evento.data == date(2026, 10, 20)
    assert evento.status is StatusEvento.PLANEJADO


def test_criar_evento_usa_proximo_identificador_disponivel():
    repositorio = FakeEventoRepository()
    repositorio.adicionar(evento_teste(identificador=4))

    identificador = criar_evento(
        repositorio,
        nome="Outro evento",
        data="2026-11-01",
        local="Rio de Janeiro",
    )

    assert identificador == 5


def test_encerrar_evento_sem_inscricoes_pendentes_atualiza_repositorio():
    eventos = FakeEventoRepository()
    inscricoes = FakeInscricaoRepository(
        [inscricao_teste(1, StatusInscricao.CONFIRMADA)]
    )
    evento = evento_teste()
    eventos.adicionar(evento)

    encerrar_evento(eventos, inscricoes, 1)

    assert eventos.obter(1).status is StatusEvento.ENCERRADO


def test_encerrar_evento_com_inscricao_pendente_propaga_erro():
    eventos = FakeEventoRepository()
    inscricoes = FakeInscricaoRepository(
        [inscricao_teste(1, StatusInscricao.PENDENTE)]
    )
    evento = evento_teste()
    eventos.adicionar(evento)

    with pytest.raises(OperacaoInvalidaError, match="inscricoes pendentes"):
        encerrar_evento(eventos, inscricoes, 1)

    assert eventos.obter(1).status is StatusEvento.EM_ANDAMENTO


def test_encerrar_evento_inexistente_gera_lookup_error():
    with pytest.raises(LookupError, match="evento 99 nao encontrado"):
        encerrar_evento(
            FakeEventoRepository(),
            FakeInscricaoRepository(),
            99,
        )