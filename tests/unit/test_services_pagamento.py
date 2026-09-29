import pytest

from eventos.adapters.repository import FakeInscricaoRepository, FakePagamentoRepository
from eventos.domain.model import Inscricao, Pagamento, StatusPagamento
from eventos.service_layer import services


def criar_inscricao_teste():
    return Inscricao(
        identificador=1,
        participante="Participante Teste",
        lote="Lote Teste",
    )


def test_registrar_pagamento_salva_no_repositorio():
    repositorio_pagamento = FakePagamentoRepository()
    repositorio_inscricao = FakeInscricaoRepository()
    
    # Prepara a inscrição no repositório
    inscricao = criar_inscricao_teste()
    repositorio_inscricao.adicionar(inscricao)

    # Executa o serviço
    pagamento = services.registrar_pagamento(
        identificador=100,
        inscricao_id=1,
        valor=150.0,
        repositorio_pagamento=repositorio_pagamento,
        repositorio_inscricao=repositorio_inscricao,
    )

    # Verifica o resultado
    assert pagamento.identificador == 100
    assert pagamento.valor == 150.0
    assert pagamento.inscricao == inscricao
    assert repositorio_pagamento.obter(100) is pagamento


def test_registrar_pagamento_falha_se_inscricao_nao_existir():
    repositorio_pagamento = FakePagamentoRepository()
    repositorio_inscricao = FakeInscricaoRepository()

    with pytest.raises(services.InscricaoNaoEncontradaError):
        services.registrar_pagamento(
            identificador=100,
            inscricao_id=99,  # Inscrição não existe
            valor=150.0,
            repositorio_pagamento=repositorio_pagamento,
            repositorio_inscricao=repositorio_inscricao,
        )


def test_aprovar_pagamento_muda_status_e_atualiza_repositorio():
    repositorio_pagamento = FakePagamentoRepository()
    inscricao = criar_inscricao_teste()
    pagamento = Pagamento(identificador=100, inscricao=inscricao, valor=150.0)
    repositorio_pagamento.adicionar(pagamento)

    pagamento_aprovado = services.aprovar_pagamento(
        identificador=100,
        repositorio_pagamento=repositorio_pagamento,
    )

    assert pagamento_aprovado.status == StatusPagamento.APROVADO
    assert repositorio_pagamento.obter(100).status == StatusPagamento.APROVADO


def test_obter_pagamento_inexistente_gera_erro():
    repositorio_pagamento = FakePagamentoRepository()

    with pytest.raises(services.PagamentoNaoEncontradoError):
        services.obter_pagamento(99, repositorio_pagamento)