import pytest

from eventos.domain.model import (
    Inscricao,
    OperacaoInvalidaError,
    StatusInscricao,
)


def criar_inscricao():
    return Inscricao(
        identificador=1,
        participante="Samuel",
        lote="Primeiro lote",
    )


def test_inscricao_inicia_pendente():
    inscricao = criar_inscricao()

    assert inscricao.status is StatusInscricao.PENDENTE
    assert not inscricao.checkin_realizado


def test_confirma_inscricao_pendente():
    inscricao = criar_inscricao()

    inscricao.confirmar()

    assert inscricao.status is StatusInscricao.CONFIRMADA


def test_nao_confirma_inscricao_cancelada():
    inscricao = criar_inscricao()
    inscricao.cancelar()

    with pytest.raises(OperacaoInvalidaError):
        inscricao.confirmar()


def test_realiza_checkin_de_inscricao_confirmada():
    inscricao = criar_inscricao()
    inscricao.confirmar()

    inscricao.realizar_checkin()

    assert inscricao.checkin_realizado


def test_nao_realiza_checkin_de_inscricao_pendente():
    inscricao = criar_inscricao()

    with pytest.raises(OperacaoInvalidaError):
        inscricao.realizar_checkin()


def test_nao_realiza_checkin_duplicado():
    inscricao = criar_inscricao()
    inscricao.confirmar()
    inscricao.realizar_checkin()

    with pytest.raises(OperacaoInvalidaError):
        inscricao.realizar_checkin()


def test_nao_cancela_inscricao_com_checkin():
    inscricao = criar_inscricao()
    inscricao.confirmar()
    inscricao.realizar_checkin()

    with pytest.raises(OperacaoInvalidaError):
        inscricao.cancelar()
