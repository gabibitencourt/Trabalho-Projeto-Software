import pytest
from eventos.domain.model import (
    AuditoriaPagamentoObserver,
    Inscricao,
    InscricaoSyncObserver,
    NotificacaoPagamentoObserver,
    Pagamento,
    Participante,
    StatusInscricao,
    StatusPagamento,
)


@pytest.fixture
def pagamento_com_inscricao():
    participante = Participante(
        identificador=1,
        nome="Lucas Silva",
        email="lucas@teste.com",
        documento="12345678901",
    )
    inscricao = Inscricao(identificador=10, participante=participante, lote="Lote 1")
    pagamento = Pagamento(identificador=100, inscricao=inscricao, valor=250.0)
    return pagamento, inscricao


def test_gof_observer_sincroniza_confirmacao_de_inscricao_ao_aprovar(
    pagamento_com_inscricao,
):
    pagamento, inscricao = pagamento_com_inscricao
    sync_observer = InscricaoSyncObserver()
    pagamento.adicionar_observador(sync_observer)

    assert inscricao.status == StatusInscricao.PENDENTE

    pagamento.aprovar()

    assert pagamento.status == StatusPagamento.APROVADO
    assert inscricao.status == StatusInscricao.CONFIRMADA


def test_gof_observer_auditoria_e_notificacao_registram_multiplos_eventos(
    pagamento_com_inscricao,
):
    pagamento, _ = pagamento_com_inscricao
    auditoria = AuditoriaPagamentoObserver()
    notificacao = NotificacaoPagamentoObserver()

    pagamento.adicionar_observador(auditoria)
    pagamento.adicionar_observador(notificacao)

    pagamento.aprovar()
    pagamento.estornar()

    assert len(auditoria.historico) == 2
    assert auditoria.historico[0]["evento"] == "PAGAMENTO_APROVADO"
    assert auditoria.historico[1]["evento"] == "PAGAMENTO_ESTORNADO"

    assert len(notificacao.notificacoes_enviadas) == 2
    assert "PAGAMENTO_APROVADO" in notificacao.notificacoes_enviadas[0]
    assert "lucas@teste.com" in notificacao.notificacoes_enviadas[0]


def test_gof_observer_remover_observador_impede_notificacao(pagamento_com_inscricao):
    pagamento, _ = pagamento_com_inscricao
    auditoria = AuditoriaPagamentoObserver()

    pagamento.adicionar_observador(auditoria)
    pagamento.remover_observador(auditoria)

    pagamento.recusar()

    assert len(auditoria.historico) == 0
    assert pagamento.status == StatusPagamento.RECUSADO