import pytest
from eventos.adapters.repository import SqlAlchemyPagamentoRepository
from eventos.domain.model import Pagamento, StatusPagamento


def test_repository_can_save_and_retrieve_pagamento(session):
    repo = SqlAlchemyPagamentoRepository(session)
    pagamento = Pagamento(identificador="pag-int-1", inscricao=None, valor=150.0)

    repo.adicionar(pagamento)
    session.flush()

    retornado = repo.obter("pag-int-1")

    assert retornado is not None
    assert retornado.identificador == "pag-int-1"
    assert retornado.valor == 150.0
    assert retornado.status == StatusPagamento.PENDENTE


def test_repository_can_delete_pagamento(session):
    repo = SqlAlchemyPagamentoRepository(session)
    pagamento = Pagamento(identificador="pag-int-2", inscricao=None, valor=200.0)

    repo.adicionar(pagamento)
    session.flush()

    repo.remover("pag-int-2")
    session.flush()

    assert repo.obter("pag-int-2") is None