import abc
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


class _CicloDeVidaEvento:
	@staticmethod
	def exigir_planejado(status):
		if status is not StatusEvento.PLANEJADO:
			raise OperacaoInvalidaError(
				"nao e possivel alterar lotes de evento em andamento ou encerrado"
			)

	@staticmethod
	def iniciar(status):
		if status is StatusEvento.EM_ANDAMENTO:
			raise OperacaoInvalidaError("evento ja esta em andamento")
		if status is StatusEvento.ENCERRADO:
			raise OperacaoInvalidaError("evento ja esta encerrado")
		return StatusEvento.EM_ANDAMENTO

	@staticmethod
	def encerrar(status, inscricoes_pendentes):
		if inscricoes_pendentes < 0:
			raise ValueError(
				"a quantidade de inscricoes pendentes nao pode ser negativa"
			)
		if status is StatusEvento.ENCERRADO:
			raise OperacaoInvalidaError("evento ja esta encerrado")
		if inscricoes_pendentes > 0:
			raise OperacaoInvalidaError(
				"nao e possivel encerrar evento com inscricoes pendentes"
			)
		return StatusEvento.ENCERRADO


class RegraAlteracaoLote(abc.ABC):
	@abc.abstractmethod
	def validar(self, lote_atual, lote_atualizado):
		raise NotImplementedError


class RegraNaoReduzirCapacidadeAbaixoDoVendido(RegraAlteracaoLote):
	def validar(self, lote_atual, lote_atualizado):
		if lote_atualizado.quant_total < lote_atual.quant_vendida:
			raise OperacaoInvalidaError(
				"nao e possivel reduzir a quantidade do lote abaixo da quantidade ja vendida"
			)


class RegraNaoAlterarPrecoComVendas(RegraAlteracaoLote):
	def validar(self, lote_atual, lote_atualizado):
		if lote_atual.quant_vendida > 0 and lote_atualizado.preco != lote_atual.preco:
			raise OperacaoInvalidaError(
				"nao e possivel alterar o preco de lote com ingressos ja vendidos"
			)


class Evento:
	_regras_alteracao_lote = (RegraNaoReduzirCapacidadeAbaixoDoVendido(),)

	def __init__(
		self,
		identificador,
		nome,
		data,
		local,
		status,
		regras_alteracao_lote=None,
	):
		self.identificador = identificador
		self.nome = nome
		self.data = data
		self.local = local
		self.status = status
		self._lotes = []
		if regras_alteracao_lote is not None:
			self._regras_alteracao_lote = tuple(regras_alteracao_lote)

	@property
	def lotes(self):
		return tuple(self._lotes)

	def adicionar_lote(self, lote):
		_CicloDeVidaEvento.exigir_planejado(self.status)
		self._lotes.append(lote)

	def alterar_lote(self, identificador_lote, lote_atualizado):
		_CicloDeVidaEvento.exigir_planejado(self.status)
		for indice, lote in enumerate(self._lotes):
			if lote.identificador == identificador_lote:
				for regra in self._regras_alteracao_lote:
					regra.validar(lote, lote_atualizado)
				self._lotes[indice] = lote_atualizado
				return
		raise OperacaoInvalidaError("lote nao encontrado")

	def iniciar(self):
		self.status = _CicloDeVidaEvento.iniciar(self.status)

	def encerrar(self, inscricoes_pendentes):
		self.status = _CicloDeVidaEvento.encerrar(
			self.status, inscricoes_pendentes
		)

class Inscricao:
    def __init__(self, identificador, participante, lote):
        self.identificador = identificador
        self.participante = participante
        self.lote = lote
        self.status = StatusInscricao.PENDENTE
        self._checkin_data_hora = None

    @property
    def checkin(self) -> CheckIn | None:
        if self._checkin_data_hora is None:
            return None
        return CheckIn(data_hora=self._checkin_data_hora)

    @checkin.setter
    def checkin(self, checkin: CheckIn | None):
        self._checkin_data_hora = None if checkin is None else checkin.data_hora

    @property
    def checkin_realizado(self) -> bool:
        return self.checkin is not None

    def confirmar(self):
        if self.status is not StatusInscricao.PENDENTE:
            raise OperacaoInvalidaError("inscricao nao pode ser confirmada")
        self.status = StatusInscricao.CONFIRMADA

    def cancelar(self):
        if self.checkin_realizado:
            raise OperacaoInvalidaError("nao e possivel cancelar inscricao com check-in")
        if self.status is StatusInscricao.CANCELADA:
            raise OperacaoInvalidaError("inscricao ja esta cancelada")
        self.status = StatusInscricao.CANCELADA

    def realizar_checkin(self, data_hora=None) -> CheckIn:
        if self.status is not StatusInscricao.CONFIRMADA:
            raise OperacaoInvalidaError("check-in exige inscricao confirmada")
        if self.checkin_realizado:
            raise OperacaoInvalidaError("check-in ja realizado")
            
        self.checkin = CheckIn(data_hora=data_hora or datetime.now())
        return self.checkin


class FabricaDeInscricao(abc.ABC):
    @abc.abstractmethod
    def criar(self, identificador, participante, lote) -> Inscricao:
        raise NotImplementedError


class FabricaInscricaoPaga(FabricaDeInscricao):
    def criar(self, identificador, participante, lote):
        return Inscricao(identificador, participante, lote)


class FabricaInscricaoCortesia(FabricaDeInscricao):
    def criar(self, identificador, participante, lote):
        inscricao = Inscricao(identificador, participante, lote)
        inscricao.confirmar()
        return inscricao


class EstadoPagamento(abc.ABC):
	"""State (GoF) do agregado Pagamento: cada status concentra as transicoes validas a partir dele."""

	@abc.abstractmethod
	def aprovar(self, pagamento: "Pagamento") -> None:
		raise NotImplementedError

	@abc.abstractmethod
	def recusar(self, pagamento: "Pagamento") -> None:
		raise NotImplementedError

	@abc.abstractmethod
	def estornar(self, pagamento: "Pagamento") -> None:
		raise NotImplementedError


class _EstadoPendente(EstadoPagamento):
	def aprovar(self, pagamento):
		pagamento.status = StatusPagamento.APROVADO

	def recusar(self, pagamento):
		pagamento.status = StatusPagamento.RECUSADO

	def estornar(self, pagamento):
		raise OperacaoInvalidaError("apenas pagamento aprovado pode ser estornado")


class _EstadoAprovado(EstadoPagamento):
	def aprovar(self, pagamento):
		raise OperacaoInvalidaError("pagamento aprovado nao pode ser reprocessado")

	def recusar(self, pagamento):
		raise OperacaoInvalidaError("apenas pagamento pendente pode ser recusado")

	def estornar(self, pagamento):
		if pagamento.inscricao.checkin_realizado:
			raise OperacaoInvalidaError(
				"nao e possivel estornar pagamento de inscricao com check-in"
			)
		pagamento.status = StatusPagamento.ESTORNADO


class _EstadoRecusado(EstadoPagamento):
	def aprovar(self, pagamento):
		raise OperacaoInvalidaError("apenas pagamento pendente pode ser aprovado")

	def recusar(self, pagamento):
		raise OperacaoInvalidaError("apenas pagamento pendente pode ser recusado")

	def estornar(self, pagamento):
		raise OperacaoInvalidaError("apenas pagamento aprovado pode ser estornado")


class _EstadoEstornado(EstadoPagamento):
	def aprovar(self, pagamento):
		raise OperacaoInvalidaError("apenas pagamento pendente pode ser aprovado")

	def recusar(self, pagamento):
		raise OperacaoInvalidaError("apenas pagamento pendente pode ser recusado")

	def estornar(self, pagamento):
		raise OperacaoInvalidaError("apenas pagamento aprovado pode ser estornado")


_ESTADOS_POR_STATUS: dict[StatusPagamento, EstadoPagamento] = {
	StatusPagamento.PENDENTE: _EstadoPendente(),
	StatusPagamento.APROVADO: _EstadoAprovado(),
	StatusPagamento.RECUSADO: _EstadoRecusado(),
	StatusPagamento.ESTORNADO: _EstadoEstornado(),
}


class Pagamento:
	def __init__(self, identificador, inscricao, valor, status=StatusPagamento.PENDENTE):
		self.identificador = identificador
		self.inscricao = inscricao
		self.valor = valor
		self.status = status

	@property
	def _estado(self) -> EstadoPagamento:
		return _ESTADOS_POR_STATUS[self.status]

	def aprovar(self):
		self._estado.aprovar(self)

	def recusar(self):
		self._estado.recusar(self)

	def estornar(self):
		self._estado.estornar(self)

class Documento:
    """Value Object que encapsula a regra de sanitização e validação de documentos (CPF/CNPJ)."""
    def __init__(self, valor: str):
        doc_limpo = re.sub(r"\D", "", valor or "")
        if len(doc_limpo) not in (11, 14):
            raise ValueError("documento invalido")
        self.valor = doc_limpo

    def __eq__(self, outro):
        return isinstance(outro, Documento) and self.valor == outro.valor


class Email:
    """Value Object que encapsula a validação e normalização de e-mails."""
    def __init__(self, valor: str):
        if not valor or "@" not in valor:
            raise ValueError("email invalido")
        self.valor = valor.lower().strip()

    def __eq__(self, outro):
        return isinstance(outro, Email) and self.valor == outro.valor

class AbstractParticipante(abc.ABC):
    """Component (Interface Abstrata) do padrão Decorator."""
    @abc.abstractmethod
    def obter_desconto_ingresso(self) -> float:
        """Retorna o percentual de desconto aplicado ao ingresso (0.0 a 1.0)."""
        pass

    @abc.abstractmethod
    def obter_tipo_credencial(self) -> str:
        """Retorna a descrição impressa no crachá/credencial."""
        pass

class Participante(AbstractParticipante):
    def __init__(self, identificador, nome, email, documento):
        if not nome or not nome.strip():
            raise ValueError("nome obrigatorio")

        self.identificador = identificador
        self.nome = nome.strip()
        
        # Delega a validação/sanitização para os Value Objects e armazena o valor processado
        self.email = email.valor if isinstance(email, Email) else Email(email).valor
        self.documento = documento.valor if isinstance(documento, Documento) else Documento(documento).valor

    def alterar_email(self, novo_email):
        self.email = novo_email.valor if isinstance(novo_email, Email) else Email(novo_email).valor

    def obter_desconto_ingresso(self) -> float:
        return 0.0  # Participante padrão paga valor integral

    def obter_tipo_credencial(self) -> str:
        return "PADRÃO"

class ParticipanteDecorator(AbstractParticipante):
    """Base Decorator: Envolve um AbstractParticipante delegando chamadas padrão."""
    def __init__(self, participante: AbstractParticipante):
        self._participante = participante

    @property
    def identificador(self):
        return getattr(self._participante, "identificador", None)

    @property
    def nome(self) -> str:
        return getattr(self._participante, "nome", "")

    @property
    def email(self) -> str:
        return getattr(self._participante, "email", "")

    @property
    def documento(self) -> str:
        return getattr(self._participante, "documento", "")

    def obter_desconto_ingresso(self) -> float:
        return self._participante.obter_desconto_ingresso()

    def obter_tipo_credencial(self) -> str:
        return self._participante.obter_tipo_credencial()


class ParticipanteVIPDecorator(ParticipanteDecorator):
    """Concrete Decorator: Concede acesso ao Lounge VIP e 20% de desconto."""
    def obter_desconto_ingresso(self) -> float:
        desconto_atual = super().obter_desconto_ingresso()
        return max(desconto_atual, 0.20)

    def obter_tipo_credencial(self) -> str:
        base = super().obter_tipo_credencial()
        return f"{base} | VIP (Acesso ao Lounge)"

class ParticipanteEstudanteDecorator(ParticipanteDecorator):
    """Concrete Decorator: Valida matricula e garante 50% de desconto (meia-entrada)."""
    def __init__(self, participante: AbstractParticipante, matricula_estudante: str):
        super().__init__(participante)
        if not matricula_estudante or not matricula_estudante.strip():
            raise ValueError("matricula de estudante obrigatoria")
        self.matricula_estudante = matricula_estudante.strip()

    def obter_desconto_ingresso(self) -> float:
        desconto_atual = super().obter_desconto_ingresso()
        return max(desconto_atual, 0.50)

    def obter_tipo_credencial(self) -> str:
        base = super().obter_tipo_credencial()
        return f"{base} | ESTUDANTE (Meia-Entrada)"
    
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

class EstrategiaPreco(abc.ABC):
    @abc.abstractmethod
    def calcular(self, preco_base):
        raise NotImplementedError


class PrecoIntegral(EstrategiaPreco):
    def calcular(self, preco_base):
        return preco_base


class DescontoPercentual(EstrategiaPreco):
    def __init__(self, percentual):
        if not 0 <= percentual <= 100:
            raise ValueError("percentual de desconto deve estar entre 0 e 100")
        self.percentual = percentual

    def calcular(self, preco_base):
        return preco_base * (1 - self.percentual / 100)


class LoteDeIngresso:
    def __init__(self, identificador, nome, preco, quant_total, quant_vendida=0):
        if quant_total < 0 or quant_vendida < 0 or preco < 0:
            raise Exception("Erro: Valor negativo")
        elif quant_total < quant_vendida:
            raise Exception("Erro: valor de quant_vendida invalido")

        self.identificador = identificador
        self.nome = nome
        self.preco = preco
        self.quant_total = quant_total
        self.quant_vendida = quant_vendida

    def calcular_preco(self, estrategia):
        return estrategia.calcular(self.preco)

    def __str__(self):
            return f"nome: {self.nome}\npreco: {self.preco}\nquantidade total: {self.quant_total}\nquantidade vendida: {self.quant_vendida}"

    def venda(self):
        if self.quant_vendida == self.quant_total:
            raise Exception("Erro: Ingressos esgotados")
        self.quant_vendida += 1