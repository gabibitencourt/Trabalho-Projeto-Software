from datetime import date

from eventos.domain.model import Evento, StatusEvento, StatusInscricao


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
