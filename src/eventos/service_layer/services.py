from datetime import date

from eventos.domain.model import (
    Evento,
    Inscricao,
    OperacaoInvalidaError,
    Pagamento,
    StatusEvento,
    StatusInscricao,
    StatusPagamento,
    LoteDeIngresso,
)


class InscricaoNaoEncontradaError(Exception):
    pass


def criar_inscricao(identificador, participante, lote, repositorio):
    inscricao = Inscricao(
        identificador=identificador,
        participante=participante,
        lote=lote,
    )
    repositorio.adicionar(inscricao)
    return inscricao


def obter_inscricao(identificador, repositorio):
    inscricao = repositorio.obter(identificador)
    if inscricao is None:
        raise InscricaoNaoEncontradaError("inscricao nao encontrada")
    return inscricao


def confirmar_inscricao(identificador, repositorio):
    inscricao = obter_inscricao(identificador, repositorio)
    inscricao.confirmar()
    repositorio.atualizar(inscricao)
    return inscricao


def cancelar_inscricao(identificador, repositorio):
    inscricao = obter_inscricao(identificador, repositorio)
    inscricao.cancelar()
    repositorio.atualizar(inscricao)
    return inscricao


def criar_evento(repositorio, nome: str, data: str, local: str) -> int:
    identificadores = [evento.identificador for evento in repositorio.listar()]
    identificador = max(identificadores, default=0) + 1
    evento = Evento(
        identificador=identificador,
        nome=nome,
        data=date.fromisoformat(data),
        local=local,
        status=StatusEvento.PLANEJADO,
    )
    repositorio.adicionar(evento)
    return identificador


def encerrar_evento(
	repositorio_evento,
	repositorio_inscricao,
	identificador_evento: int,
) -> None:
    evento = repositorio_evento.obter(identificador_evento)
    if evento is None:
        raise LookupError(f"evento {identificador_evento} nao encontrado")

    inscricoes = repositorio_inscricao.listar_por_evento(identificador_evento)
    inscricoes_pendentes = sum(
        inscricao.status is StatusInscricao.PENDENTE for inscricao in inscricoes
    )
    evento.encerrar(inscricoes_pendentes=inscricoes_pendentes)
    repositorio_evento.atualizar(evento)


class PagamentoNaoEncontradoError(Exception):
    pass


def registrar_pagamento(
    identificador: int,
    inscricao_id: int,
    valor: float,
    repositorio_pagamento,
    repositorio_inscricao,
):
    inscricao = repositorio_inscricao.obter(inscricao_id)
    if inscricao is None:
        raise InscricaoNaoEncontradaError("inscricao nao encontrada")

    pagamento = Pagamento(
        identificador=identificador,
        inscricao=inscricao,
        valor=valor,
    )
    repositorio_pagamento.adicionar(pagamento)
    return pagamento


def obter_pagamento(identificador: int, repositorio_pagamento):
    pagamento = repositorio_pagamento.obter(identificador)
    if pagamento is None:
        raise PagamentoNaoEncontradoError("pagamento nao encontrado")
    return pagamento


def aprovar_pagamento(identificador: int, repositorio_pagamento):
    pagamento = obter_pagamento(identificador, repositorio_pagamento)
    pagamento.aprovar()
    repositorio_pagamento.atualizar(pagamento)
    return pagamento


def recusar_pagamento(identificador: int, repositorio_pagamento):
    pagamento = obter_pagamento(identificador, repositorio_pagamento)
    pagamento.recusar()
    repositorio_pagamento.atualizar(pagamento)
    return pagamento


def estornar_pagamento(identificador: int, repositorio_pagamento):
    pagamento = obter_pagamento(identificador, repositorio_pagamento)
    pagamento.estornar()
    repositorio_pagamento.atualizar(pagamento)
    return pagamento


def confirmar_inscricao_apos_pagamento(
    identificador: int,
    repositorio_pagamento,
    repositorio_inscricao,
):
    pagamento = obter_pagamento(identificador, repositorio_pagamento)
    if pagamento.status is not StatusPagamento.APROVADO:
        raise OperacaoInvalidaError(
            "so e possivel confirmar inscricao com pagamento aprovado"
        )

    pagamento.inscricao.confirmar()
    repositorio_inscricao.atualizar(pagamento.inscricao)
    return pagamento.inscricao

def criar_lote_ingresso(repositorio_evento, evento_id, identificador, nome, preco, quant_total, quant_vendida=0):    
    if repositorio_evento.obter(evento_id) is None:
        raise Exception("Evento nao encontrado.")
        
    return LoteDeIngresso(identificador, nome, preco, quant_total, quant_vendida)

def obter_lote(repositorio, identificador):
    lote = repositorio.obter(identificador)
    if lote is None:
        raise Exception("Lote nao encontrado.")
    return lote