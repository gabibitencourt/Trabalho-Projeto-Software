import pytest

from eventos.domain.model import (
    Inscricao,
    OperacaoInvalidaError,
    Pagamento,
    StatusPagamento,
)


def criar_inscricao(checkin_realizado=False):
    inscricao = Inscricao(
        identificador=1,
        participante="Samuel",
        lote="Primeiro lote",
    )
    if checkin_realizado:
        inscricao.confirmar()
        inscricao.realizar_checkin()
    return inscricao


def criar_pagamento(inscricao=None, status=StatusPagamento.PENDENTE):
    return Pagamento(
        identificador=1,
        inscricao=inscricao or criar_inscricao(),
        valor=150,
        status=status,
    )


def test_pagamento_inicia_pendente():
    pagamento = criar_pagamento()

    assert pagamento.status is StatusPagamento.PENDENTE
    assert pagamento.valor == 150


def test_aprova_pagamento_pendente():
    pagamento = criar_pagamento()

    pagamento.aprovar()

    assert pagamento.status is StatusPagamento.APROVADO


def test_nao_reprocessa_pagamento_ja_aprovado():
    pagamento = criar_pagamento()
    pagamento.aprovar()

    with pytest.raises(OperacaoInvalidaError):
        pagamento.aprovar()

    assert pagamento.status is StatusPagamento.APROVADO


def test_nao_aprova_pagamento_recusado():
    pagamento = criar_pagamento(status=StatusPagamento.RECUSADO)

    with pytest.raises(OperacaoInvalidaError):
        pagamento.aprovar()


def test_recusa_pagamento_pendente():
    pagamento = criar_pagamento()

    pagamento.recusar()

    assert pagamento.status is StatusPagamento.RECUSADO


def test_nao_recusa_pagamento_ja_aprovado():
    pagamento = criar_pagamento()
    pagamento.aprovar()

    with pytest.raises(OperacaoInvalidaError):
        pagamento.recusar()

    assert pagamento.status is StatusPagamento.APROVADO


def test_estorna_pagamento_aprovado_sem_checkin():
    pagamento = criar_pagamento()
    pagamento.aprovar()

    pagamento.estornar()

    assert pagamento.status is StatusPagamento.ESTORNADO


def test_nao_estorna_pagamento_pendente():
    pagamento = criar_pagamento()

    with pytest.raises(OperacaoInvalidaError):
        pagamento.estornar()


def test_nao_estorna_pagamento_de_inscricao_com_checkin():
    inscricao = criar_inscricao(checkin_realizado=True)
    pagamento = criar_pagamento(inscricao=inscricao)
    pagamento.aprovar()

    with pytest.raises(OperacaoInvalidaError):
        pagamento.estornar()

    assert pagamento.status is StatusPagamento.APROVADO
