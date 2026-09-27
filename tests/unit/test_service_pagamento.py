import pytest

from eventos.adapters.repository import FakeInscricaoRepository, FakePagamentoRepository
from eventos.domain.model import (
    Inscricao,
    OperacaoInvalidaError,
    StatusInscricao,
    StatusPagamento,
)
from eventos.service_layer.services import (
    confirmar_inscricao_apos_pagamento,
    processar_pagamento,
)


def criar_inscricao(identificador=1):
    return Inscricao(identificador=identificador, participante="Samuel", lote="Primeiro lote")


@pytest.fixture
def repositorios():
    return FakePagamentoRepository(), FakeInscricaoRepository()


def test_processa_pagamento_aprovado(repositorios):
    repositorio_pagamentos, repositorio_inscricoes = repositorios
    repositorio_inscricoes.adicionar(criar_inscricao())

    pagamento = processar_pagamento(
        identificador=1,
        inscricao_id=1,
        valor=150,
        aprovado=True,
        repositorio_pagamentos=repositorio_pagamentos,
        repositorio_inscricoes=repositorio_inscricoes,
    )

    assert pagamento.status is StatusPagamento.APROVADO
    assert repositorio_pagamentos.obter(1) is pagamento


def test_processa_pagamento_recusado(repositorios):
    repositorio_pagamentos, repositorio_inscricoes = repositorios
    repositorio_inscricoes.adicionar(criar_inscricao())

    pagamento = processar_pagamento(
        identificador=1,
        inscricao_id=1,
        valor=150,
        aprovado=False,
        repositorio_pagamentos=repositorio_pagamentos,
        repositorio_inscricoes=repositorio_inscricoes,
    )

    assert pagamento.status is StatusPagamento.RECUSADO


def test_nao_processa_pagamento_para_inscricao_inexistente(repositorios):
    repositorio_pagamentos, repositorio_inscricoes = repositorios

    with pytest.raises(OperacaoInvalidaError):
        processar_pagamento(
            identificador=1,
            inscricao_id=999,
            valor=150,
            aprovado=True,
            repositorio_pagamentos=repositorio_pagamentos,
            repositorio_inscricoes=repositorio_inscricoes,
        )


def test_nao_processa_segundo_pagamento_para_inscricao_ja_aprovada(repositorios):
    repositorio_pagamentos, repositorio_inscricoes = repositorios
    repositorio_inscricoes.adicionar(criar_inscricao())
    processar_pagamento(
        identificador=1,
        inscricao_id=1,
        valor=150,
        aprovado=True,
        repositorio_pagamentos=repositorio_pagamentos,
        repositorio_inscricoes=repositorio_inscricoes,
    )

    with pytest.raises(OperacaoInvalidaError):
        processar_pagamento(
            identificador=2,
            inscricao_id=1,
            valor=150,
            aprovado=True,
            repositorio_pagamentos=repositorio_pagamentos,
            repositorio_inscricoes=repositorio_inscricoes,
        )


def test_confirma_inscricao_apos_pagamento_aprovado(repositorios):
    repositorio_pagamentos, repositorio_inscricoes = repositorios
    repositorio_inscricoes.adicionar(criar_inscricao())
    processar_pagamento(
        identificador=1,
        inscricao_id=1,
        valor=150,
        aprovado=True,
        repositorio_pagamentos=repositorio_pagamentos,
        repositorio_inscricoes=repositorio_inscricoes,
    )

    confirmar_inscricao_apos_pagamento(
        pagamento_id=1,
        repositorio_pagamentos=repositorio_pagamentos,
        repositorio_inscricoes=repositorio_inscricoes,
    )

    assert repositorio_inscricoes.obter(1).status is StatusInscricao.CONFIRMADA


def test_nao_confirma_inscricao_com_pagamento_recusado(repositorios):
    repositorio_pagamentos, repositorio_inscricoes = repositorios
    repositorio_inscricoes.adicionar(criar_inscricao())
    processar_pagamento(
        identificador=1,
        inscricao_id=1,
        valor=150,
        aprovado=False,
        repositorio_pagamentos=repositorio_pagamentos,
        repositorio_inscricoes=repositorio_inscricoes,
    )

    with pytest.raises(OperacaoInvalidaError):
        confirmar_inscricao_apos_pagamento(
            pagamento_id=1,
            repositorio_pagamentos=repositorio_pagamentos,
            repositorio_inscricoes=repositorio_inscricoes,
        )

    assert repositorio_inscricoes.obter(1).status is StatusInscricao.PENDENTE


def test_nao_confirma_com_pagamento_inexistente(repositorios):
    repositorio_pagamentos, repositorio_inscricoes = repositorios

    with pytest.raises(OperacaoInvalidaError):
        confirmar_inscricao_apos_pagamento(
            pagamento_id=999,
            repositorio_pagamentos=repositorio_pagamentos,
            repositorio_inscricoes=repositorio_inscricoes,
        )
