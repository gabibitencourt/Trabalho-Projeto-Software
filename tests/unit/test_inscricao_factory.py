from eventos.adapters.repository import FakeInscricaoRepository
from eventos.domain.model import (
    FabricaInscricaoCortesia,
    FabricaInscricaoPaga,
    Inscricao,
    StatusInscricao,
)
from eventos.service_layer import services


def test_fabrica_paga_cria_inscricao_pendente():
    inscricao = FabricaInscricaoPaga().criar(1, "Samuel", "Primeiro lote")

    assert isinstance(inscricao, Inscricao)
    assert inscricao.status is StatusInscricao.PENDENTE


def test_fabrica_cortesia_cria_inscricao_confirmada():
    inscricao = FabricaInscricaoCortesia().criar(1, "Samuel", "Primeiro lote")

    assert inscricao.status is StatusInscricao.CONFIRMADA


def test_inscricao_cortesia_permite_checkin_sem_pagamento():
    inscricao = FabricaInscricaoCortesia().criar(1, "Samuel", "Primeiro lote")

    inscricao.realizar_checkin()

    assert inscricao.checkin_realizado


def test_servico_usa_fabrica_paga_por_padrao():
    repo = FakeInscricaoRepository()

    inscricao = services.criar_inscricao(1, "Samuel", "Primeiro lote", repo)

    assert inscricao.status is StatusInscricao.PENDENTE


def test_servico_cria_inscricao_com_a_fabrica_recebida():
    repo = FakeInscricaoRepository()

    services.criar_inscricao(
        1, "Samuel", "Primeiro lote", repo, fabrica=FabricaInscricaoCortesia()
    )

    assert repo.obter(1).status is StatusInscricao.CONFIRMADA
    assert repo.commitou is True
