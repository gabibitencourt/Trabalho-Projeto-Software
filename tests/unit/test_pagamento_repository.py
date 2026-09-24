from eventos.adapters.repository import FakePagamentoRepository
from eventos.domain.model import Pagamento, StatusPagamento


def test_fake_pagamento_repository_adicionar_e_obter():
    repo = FakePagamentoRepository()
    pagamento = Pagamento(identificador="pag-100", inscricao=None, valor=120.0)

    repo.adicionar(pagamento)
    resgatado = repo.obter("pag-100")

    assert resgatado is not None
    assert resgatado.identificador == "pag-100"
    assert resgatado.valor == 120.0
    assert resgatado.status == StatusPagamento.PENDENTE


def test_fake_pagamento_repository_remover():
    repo = FakePagamentoRepository()
    pagamento = Pagamento(identificador="pag-200", inscricao=None, valor=50.0)

    repo.adicionar(pagamento)
    repo.remover("pag-200")

    assert repo.obter("pag-200") is None