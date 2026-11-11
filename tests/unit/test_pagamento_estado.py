import pytest

from eventos.domain.model import (
    Inscricao,
    OperacaoInvalidaError,
    Pagamento,
    StatusPagamento,
    _EstadoAprovado,
    _EstadoEstornado,
    _EstadoPendente,
    _EstadoRecusado,
)


def criar_pagamento(status=StatusPagamento.PENDENTE):
    inscricao = Inscricao(identificador=1, participante="Samuel", lote="Primeiro lote")
    return Pagamento(identificador=1, inscricao=inscricao, valor=150, status=status)


def test_pagamento_pendente_resolve_estado_pendente():
    pagamento = criar_pagamento()

    assert isinstance(pagamento._estado, _EstadoPendente)


def test_pagamento_aprovado_resolve_estado_aprovado():
    pagamento = criar_pagamento(status=StatusPagamento.APROVADO)

    assert isinstance(pagamento._estado, _EstadoAprovado)


def test_pagamento_recusado_resolve_estado_recusado():
    pagamento = criar_pagamento(status=StatusPagamento.RECUSADO)

    assert isinstance(pagamento._estado, _EstadoRecusado)


def test_pagamento_estornado_resolve_estado_estornado():
    pagamento = criar_pagamento(status=StatusPagamento.ESTORNADO)

    assert isinstance(pagamento._estado, _EstadoEstornado)


def test_estado_e_reavaliado_apos_transicao():
    pagamento = criar_pagamento()
    estado_antes = pagamento._estado

    pagamento.aprovar()

    assert isinstance(estado_antes, _EstadoPendente)
    assert isinstance(pagamento._estado, _EstadoAprovado)


def test_estado_recusado_nao_permite_aprovar_nem_estornar():
    pagamento = criar_pagamento(status=StatusPagamento.RECUSADO)

    with pytest.raises(OperacaoInvalidaError):
        pagamento.aprovar()

    with pytest.raises(OperacaoInvalidaError):
        pagamento.estornar()
