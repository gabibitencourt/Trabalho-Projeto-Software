from datetime import date

import pytest

from eventos.domain.model import (
    Evento,
    OperacaoInvalidaError,
    StatusEvento,
)


class LoteFake:
    def __init__(self, identificador=1):
        self.identificador = identificador


def criar_evento(status=StatusEvento.PLANEJADO):
    return Evento(
        identificador=1,
        nome="Conferencia de Software",
        data=date(2026, 10, 20),
        local="Niteroi",
        status=status,
    )


def test_evento_armazena_seus_dados_principais():
    evento = criar_evento()

    assert evento.identificador == 1
    assert evento.nome == "Conferencia de Software"
    assert evento.data == date(2026, 10, 20)
    assert evento.local == "Niteroi"
    assert evento.status is StatusEvento.PLANEJADO


def test_status_do_evento_tem_valores_fechados():
    with pytest.raises(ValueError):
        StatusEvento("qualquer status")


def test_evento_adiciona_lote_sem_expor_lista_mutavel():
    evento = criar_evento()
    lote = LoteFake()

    evento.adicionar_lote(lote)

    assert evento.lotes == (lote,)
    assert not hasattr(evento.lotes, "append")


def test_nao_adiciona_lote_quando_evento_esta_em_andamento():
    evento = criar_evento(StatusEvento.EM_ANDAMENTO)

    with pytest.raises(OperacaoInvalidaError):
        evento.adicionar_lote(LoteFake())


def test_nao_altera_lote_quando_evento_esta_em_andamento():
    evento = criar_evento(StatusEvento.EM_ANDAMENTO)

    with pytest.raises(OperacaoInvalidaError):
        evento.alterar_lote(1, LoteFake(1))


def test_altera_lote_com_evento_planejado():
    evento = criar_evento()
    lote_original = LoteFake(1)
    outro_lote = LoteFake(2)
    lote_atualizado = LoteFake(1)
    evento.adicionar_lote(lote_original)
    evento.adicionar_lote(outro_lote)

    evento.alterar_lote(1, lote_atualizado)

    assert evento.lotes == (lote_atualizado, outro_lote)
    assert evento.status is StatusEvento.PLANEJADO


def test_nao_altera_lote_inexistente():
    evento = criar_evento()
    lote = LoteFake(1)
    evento.adicionar_lote(lote)

    with pytest.raises(OperacaoInvalidaError, match="lote nao encontrado"):
        evento.alterar_lote(2, LoteFake(2))

    assert evento.lotes == (lote,)


def test_nao_adiciona_lote_quando_evento_esta_encerrado():
    evento = criar_evento(StatusEvento.ENCERRADO)

    with pytest.raises(OperacaoInvalidaError):
        evento.adicionar_lote(LoteFake())

