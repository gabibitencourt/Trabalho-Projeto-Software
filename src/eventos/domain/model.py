from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import re

class StatusEvento(Enum):
	PLANEJADO = "planejado"
	EM_ANDAMENTO = "em andamento"
	ENCERRADO = "encerrado"

class StatusInscricao(Enum):
	PENDENTE = "pendente"
	CONFIRMADA = "confirmada"
	CANCELADA = "cancelada"


class StatusPagamento(Enum):
	PENDENTE = "pendente"
	APROVADO = "aprovado"
	RECUSADO = "recusado"
	ESTORNADO = "estornado"

class RoleOrganizador(Enum):
    ADMIN = "admin"
    ORGANIZADOR = "organizador"

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
		self.checkin_realizado = True


class Pagamento:
	def __init__(self, identificador, inscricao, valor, status=StatusPagamento.PENDENTE):
		self.identificador = identificador
		self.inscricao = inscricao
		self.valor = valor
		self.status = status

	def aprovar(self):
		if self.status is StatusPagamento.APROVADO:
			raise OperacaoInvalidaError("pagamento aprovado nao pode ser reprocessado")
		if self.status is not StatusPagamento.PENDENTE:
			raise OperacaoInvalidaError("apenas pagamento pendente pode ser aprovado")
		self.status = StatusPagamento.APROVADO

	def recusar(self):
		if self.status is not StatusPagamento.PENDENTE:
			raise OperacaoInvalidaError("apenas pagamento pendente pode ser recusado")
		self.status = StatusPagamento.RECUSADO

	def estornar(self):
		if self.status is not StatusPagamento.APROVADO:
			raise OperacaoInvalidaError("apenas pagamento aprovado pode ser estornado")
		if self.inscricao.checkin_realizado:
			raise OperacaoInvalidaError(
				"nao e possivel estornar pagamento de inscricao com check-in"
			)
		self.status = StatusPagamento.ESTORNADO

		self.checkin = CheckIn(data_hora=data_hora or datetime.now())

class Participante:

    def __init__(self, identificador, nome, email, documento):
        if not nome or not nome.strip():
            raise ValueError("nome obrigatorio")

        doc_limpo = re.sub(r"\D", "", documento or "")
        if len(doc_limpo) not in (11, 14):
            raise ValueError("documento invalido")

        if not email or "@" not in email:
            raise ValueError("email invalido")

        self.identificador = identificador
        self.nome = nome.strip()
        self.email = email.lower().strip()
        self.documento = doc_limpo

    def alterar_email(self, novo_email):
        if not novo_email or "@" not in novo_email:
            raise ValueError("email invalido")
        self.email = novo_email.lower().strip()

class Organizador:

    def __init__(
        self, identificador, nome, email, role=RoleOrganizador.ORGANIZADOR
    ):
        if not nome or not nome.strip():
            raise ValueError("nome obrigatorio")

        if not email or "@" not in email:
            raise ValueError("email invalido")

        if not isinstance(role, RoleOrganizador):
            raise ValueError("role invalida")

        self.identificador = identificador
        self.nome = nome.strip()
        self.email = email.lower().strip()
        self.role = role