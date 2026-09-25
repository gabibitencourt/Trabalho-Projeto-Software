from eventos.adapters.repository import FakePagamentoRepository
from eventos.domain.model import Inscricao, Pagamento


def criar_inscricao():
    return Inscricao(
        identificador=1,
        participante="Samuel",
        lote="Primeiro lote",
    )


def criar_pagamento(identificador=1, inscricao=None, valor=150):
    return Pagamento(
        identificador=identificador,
        inscricao=inscricao or criar_inscricao(),
        valor=valor,
    )


def test_adiciona_e_obtem_pagamento():
    repositorio = FakePagamentoRepository()
    pagamento = criar_pagamento()

    repositorio.adicionar(pagamento)

    assert repositorio.obter(1) is pagamento


def test_obter_retorna_none_para_identificador_inexistente():
    repositorio = FakePagamentoRepository()

    assert repositorio.obter(999) is None


def test_lista_pagamentos_por_inscricao():
    repositorio = FakePagamentoRepository()
    inscricao = criar_inscricao()
    pagamento = criar_pagamento(inscricao=inscricao)
    repositorio.adicionar(pagamento)
    repositorio.adicionar(criar_pagamento(identificador=2))

    resultado = repositorio.listar_por_inscricao(inscricao)

    assert resultado == [pagamento]


def test_atualizar_substitui_pagamento_existente():
    repositorio = FakePagamentoRepository()
    pagamento = criar_pagamento()
    repositorio.adicionar(pagamento)
    pagamento.aprovar()

    repositorio.atualizar(pagamento)

    assert repositorio.obter(1).status == pagamento.status


def test_remover_exclui_pagamento():
    repositorio = FakePagamentoRepository()
    pagamento = criar_pagamento()
    repositorio.adicionar(pagamento)

    repositorio.remover(1)

    assert repositorio.obter(1) is None
