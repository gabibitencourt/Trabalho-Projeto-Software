import pytest
from eventos.adapters.repository import SqlAlchemyPagamentoRepository
from eventos.domain.model import Pagamento, StatusPagamento


def criar_pagamento(identificador=1, inscricao=None, valor=150.0):
    return Pagamento(identificador=identificador, inscricao=inscricao, valor=valor)


def test_repository_can_save_and_retrieve_pagamento(session):
    repo = SqlAlchemyPagamentoRepository(session)
    pagamento = criar_pagamento()

    repo.adicionar(pagamento)
    session.commit()
    session.expire_all()

    retornado = repo.obter(1)

    assert retornado is not None
    assert retornado.identificador == 1
    assert retornado.valor == 150.0
    assert retornado.status == StatusPagamento.PENDENTE


def test_repository_can_delete_pagamento(session):
    repo = SqlAlchemyPagamentoRepository(session)
    repo.adicionar(criar_pagamento(2))
    session.commit()

    repo.remover(2)
    session.commit()

    assert repo.obter(2) is None


def test_repository_atualiza_status_do_pagamento(session):
    repo = SqlAlchemyPagamentoRepository(session)
    pagamento = criar_pagamento(3)
    repo.adicionar(pagamento)
    session.commit()

    pagamento.aprovar()
    repo.atualizar(pagamento)
    session.commit()
    session.expire_all()

    assert repo.obter(3).status is StatusPagamento.APROVADO
