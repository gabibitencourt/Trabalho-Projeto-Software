from enum import Enum


class StatusEvento(Enum):
	PLANEJADO = "planejado"
	EM_ANDAMENTO = "em andamento"
	ENCERRADO = "encerrado"


class OperacaoInvalidaError(Exception):
	pass


class Evento:
	def __init__(self, identificador, nome, data, local, status):
		self.identificador = identificador
		self.nome = nome
		self.data = data
		self.local = local
		self.status = status
		self._lotes = []

	@property
	def lotes(self):
		return tuple(self._lotes)

	def adicionar_lote(self, lote):
		self._exigir_evento_planejado()
		self._lotes.append(lote)

	def alterar_lote(self, identificador_lote, lote_atualizado):
		self._exigir_evento_planejado()
		for indice, lote in enumerate(self._lotes):
			if lote.identificador == identificador_lote:
				self._lotes[indice] = lote_atualizado
				return
		raise OperacaoInvalidaError("lote nao encontrado")



	def _exigir_evento_planejado(self):
		if self.status is not StatusEvento.PLANEJADO:
			raise OperacaoInvalidaError(
				"nao e possivel alterar lotes de evento em andamento ou encerrado"
			)
