from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class StatusEvento(Enum):
	PLANEJADO = "planejado"
	EM_ANDAMENTO = "em andamento"
	ENCERRADO = "encerrado"


class StatusInscricao(Enum):
	PENDENTE = "pendente"
	CONFIRMADA = "confirmada"
	CANCELADA = "cancelada"


class OperacaoInvalidaError(Exception):
	pass

@dataclass(frozen=True)
class CheckIn:
    data_hora: datetime

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


class Inscricao:
	def __init__(self, identificador, participante, lote):
		self.identificador = identificador
		self.participante = participante
		self.lote = lote
		self.status = StatusInscricao.PENDENTE
		self.checkin = None

	def confirmar(self):
		if self.status is not StatusInscricao.PENDENTE:
			raise OperacaoInvalidaError("inscricao nao pode ser confirmada")
		self.status = StatusInscricao.CONFIRMADA

	def cancelar(self):
		if self.checkin is not None:
			raise OperacaoInvalidaError("nao e possivel cancelar inscricao com check-in")
		if self.status is StatusInscricao.CANCELADA:
			raise OperacaoInvalidaError("inscricao ja esta cancelada")
		self.status = StatusInscricao.CANCELADA

	def realizar_checkin(self, data_hora=None):
		if self.status is not StatusInscricao.CONFIRMADA:
			raise OperacaoInvalidaError("check-in exige inscricao confirmada")
		if self.checkin is not None:
			raise OperacaoInvalidaError("check-in ja realizado")
		self.checkin = CheckIn(data_hora=data_hora or datetime.now())
