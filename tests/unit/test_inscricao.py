from datetime import datetime
import pytest

from eventos.domain.model import (
    CheckIn,
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
    assert inscricao.checkin is None


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

    assert inscricao.checkin is not None
    assert isinstance(inscricao.checkin, CheckIn)
    assert isinstance(inscricao.checkin.data_hora, datetime)

def test_realiza_checkin_com_data_hora_especifica():
    inscricao = criar_inscricao()
    inscricao.confirmar()
    data_customizada = datetime(2026, 9, 16, 20, 0, 0)

    inscricao.realizar_checkin(data_hora=data_customizada)

    assert inscricao.checkin.data_hora == data_customizada


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
