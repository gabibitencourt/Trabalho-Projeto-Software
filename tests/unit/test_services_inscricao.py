from eventos.adapters.repository import FakeInscricaoRepository
from eventos.domain.model import StatusInscricao
from eventos.service_layer import services


def test_criar_inscricao_faz_commit():
    repo = FakeInscricaoRepository()

    services.criar_inscricao(1, "Samuel", "Primeiro lote", repo)

    assert repo.obter(1) is not None
    assert repo.commitou is True


def test_confirmar_inscricao_faz_commit():
    repo = FakeInscricaoRepository()
    services.criar_inscricao(1, "Samuel", "Primeiro lote", repo)
    repo.commitou = False

    inscricao = services.confirmar_inscricao(1, repo)

    assert inscricao.status == StatusInscricao.CONFIRMADA
    assert repo.commitou is True


def test_cancelar_inscricao_faz_commit():
    repo = FakeInscricaoRepository()
    services.criar_inscricao(1, "Samuel", "Primeiro lote", repo)
    repo.commitou = False

    inscricao = services.cancelar_inscricao(1, repo)

    assert inscricao.status == StatusInscricao.CANCELADA
    assert repo.commitou is True
