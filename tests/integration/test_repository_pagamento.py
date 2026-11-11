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


def test_pagamento_recarregado_do_banco_resolve_estado_pelo_status_persistido(session):
    repo = SqlAlchemyPagamentoRepository(session)
    repo.adicionar(criar_pagamento(4))
    session.commit()

    # Descarta a identity map para forcar o SQLAlchemy a reconstruir o
    # Pagamento a partir das linhas do banco, sem passar pelo __init__ do
    # agregado (mapeamento imperativo). O Estado (GoF State) precisa ser
    # resolvido a partir do status persistido, nao de algo guardado so na
    # construcao do objeto.
    session.expire_all()
    pagamento_recarregado = repo.obter(4)

    pagamento_recarregado.recusar()
    repo.atualizar(pagamento_recarregado)
    session.commit()
    session.expire_all()

    assert repo.obter(4).status is StatusPagamento.RECUSADO
