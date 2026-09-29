from datetime import date

from eventos.domain.model import Evento, Inscricao, StatusEvento, StatusInscricao


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
