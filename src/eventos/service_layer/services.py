from eventos.domain.model import Inscricao


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
