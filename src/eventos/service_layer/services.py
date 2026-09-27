from eventos.domain.model import OperacaoInvalidaError, Pagamento, StatusPagamento


def processar_pagamento(
    identificador,
    inscricao_id,
    valor,
    aprovado,
    repositorio_pagamentos,
    repositorio_inscricoes,
) -> Pagamento:
    inscricao = repositorio_inscricoes.obter(inscricao_id)
    if inscricao is None:
        raise OperacaoInvalidaError("inscricao nao encontrada")

    pagamentos_da_inscricao = repositorio_pagamentos.listar_por_inscricao(inscricao)
    if any(p.status is StatusPagamento.APROVADO for p in pagamentos_da_inscricao):
        raise OperacaoInvalidaError("inscricao ja possui pagamento aprovado")

    pagamento = Pagamento(identificador, inscricao, valor)
    if aprovado:
        pagamento.aprovar()
    else:
        pagamento.recusar()

    repositorio_pagamentos.adicionar(pagamento)
    return pagamento


def confirmar_inscricao_apos_pagamento(
    pagamento_id,
    repositorio_pagamentos,
    repositorio_inscricoes,
):
    pagamento = repositorio_pagamentos.obter(pagamento_id)
    if pagamento is None:
        raise OperacaoInvalidaError("pagamento nao encontrado")

    if pagamento.status is not StatusPagamento.APROVADO:
        raise OperacaoInvalidaError(
            "so e possivel confirmar inscricao com pagamento aprovado"
        )

    pagamento.inscricao.confirmar()
    repositorio_inscricoes.atualizar(pagamento.inscricao)
