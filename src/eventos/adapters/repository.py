import abc
from sqlalchemy.orm import Session

from eventos.domain.model import Evento, Inscricao, LoteDeIngresso, Pagamento


class AbstractEventoRepository(abc.ABC):
    @abc.abstractmethod
    def adicionar(self, evento: Evento):
        raise NotImplementedError

    @abc.abstractmethod
    def obter(self, identificador: int) -> Evento:
        raise NotImplementedError

    @abc.abstractmethod
    def listar(self) -> list[Evento]:
        raise NotImplementedError

    @abc.abstractmethod
    def atualizar(self, evento: Evento):
        raise NotImplementedError


class FakeEventoRepository(AbstractEventoRepository):
    def __init__(self):
        self._eventos = set()

    def adicionar(self, evento: Evento):
        self._eventos.add(evento)

    def obter(self, identificador: int) -> Evento:
        return next(
            (evento for evento in self._eventos if evento.identificador == identificador),
            None,
        )

    def listar(self) -> list[Evento]:
        return list(self._eventos)

    def atualizar(self, evento: Evento):
        evento_anterior = self.obter(evento.identificador)
        if evento_anterior is not None:
            self._eventos.remove(evento_anterior)
        self.adicionar(evento)


class SqlAlchemyEventoRepository(AbstractEventoRepository):
    def __init__(self, session: Session):
        self.session = session

    def adicionar(self, evento: Evento):
        self.session.add(evento)

    def obter(self, identificador: int) -> Evento | None:
        return self.session.get(Evento, identificador)

    def listar(self) -> list[Evento]:
        return list(self.session.query(Evento).all())

    def atualizar(self, evento: Evento):
        self.session.merge(evento)


class AbstractInscricaoRepository(abc.ABC):
    @abc.abstractmethod
    def adicionar(self, inscricao: Inscricao):
        raise NotImplementedError

    @abc.abstractmethod
    def obter(self, identificador: int) -> Inscricao | None:
        raise NotImplementedError

    @abc.abstractmethod
    def listar_por_participante(self, participante) -> list[Inscricao]:
        raise NotImplementedError

    @abc.abstractmethod
    def atualizar(self, inscricao: Inscricao):
        raise NotImplementedError

    @abc.abstractmethod
    def remover(self, identificador: int):
        raise NotImplementedError


class FakeInscricaoRepository(AbstractInscricaoRepository):
    def __init__(self):
        self._inscricoes = {}

    def adicionar(self, inscricao: Inscricao):
        self._inscricoes[inscricao.identificador] = inscricao

    def obter(self, identificador: int) -> Inscricao | None:
        return self._inscricoes.get(identificador)

    def listar_por_participante(self, participante) -> list[Inscricao]:
        return [
            inscricao
            for inscricao in self._inscricoes.values()
            if inscricao.participante == participante
        ]

    def atualizar(self, inscricao: Inscricao):
        self._inscricoes[inscricao.identificador] = inscricao

    def remover(self, identificador: int):
        self._inscricoes.pop(identificador, None)


class SqlAlchemyInscricaoRepository(AbstractInscricaoRepository):
    def __init__(self, session: Session):
        self.session = session

    def adicionar(self, inscricao: Inscricao):
        self.session.add(inscricao)

    def obter(self, identificador: int) -> Inscricao | None:
        return self.session.get(Inscricao, identificador)

    def listar_por_participante(self, participante) -> list[Inscricao]:
        return (
            self.session.query(Inscricao)
            .filter_by(participante=participante)
            .order_by(Inscricao.identificador)
            .all()
        )

    def atualizar(self, inscricao: Inscricao):
        self.session.add(inscricao)

    def remover(self, identificador: int):
        inscricao = self.obter(identificador)
        if inscricao:
            self.session.delete(inscricao)


class AbstractPagamentoRepository(abc.ABC):
    @abc.abstractmethod
    def adicionar(self, pagamento: Pagamento):
        raise NotImplementedError

    @abc.abstractmethod
    def obter(self, identificador: int) -> Pagamento:
        raise NotImplementedError

    @abc.abstractmethod
    def listar_por_inscricao(self, inscricao) -> list[Pagamento]:
        raise NotImplementedError

    @abc.abstractmethod
    def atualizar(self, pagamento: Pagamento):
        raise NotImplementedError

    @abc.abstractmethod
    def remover(self, identificador):
        raise NotImplementedError


class FakePagamentoRepository(AbstractPagamentoRepository):
    def __init__(self):
        self._pagamentos = set()

    def adicionar(self, pagamento: Pagamento):
        self._pagamentos.add(pagamento)

    def obter(self, identificador: int) -> Pagamento:
        return next(
            (p for p in self._pagamentos if p.identificador == identificador),
            None
        )

    def listar_por_inscricao(self, inscricao) -> list[Pagamento]:
        return [p for p in self._pagamentos if p.inscricao == inscricao]

    def atualizar(self, pagamento: Pagamento):
        self.remover(pagamento.identificador)
        self.adicionar(pagamento)

    def remover(self, identificador):
        pagamento = self.obter(identificador)
        if pagamento:
            self._pagamentos.remove(pagamento)


class SqlAlchemyPagamentoRepository(AbstractPagamentoRepository):
    def __init__(self, session: Session):
        self.session = session

    def adicionar(self, pagamento: Pagamento):
        self.session.add(pagamento)

    def obter(self, identificador) -> Pagamento | None:
        return self.session.query(Pagamento).filter_by(identificador=str(identificador)).first()

    def listar_por_inscricao(self, inscricao) -> list[Pagamento]:
        return self.session.query(Pagamento).filter_by(inscricao=inscricao).all()

    def atualizar(self, pagamento: Pagamento):
        self.session.merge(pagamento)

    def remover(self, identificador):
        pagamento = self.obter(identificador)
        if pagamento:
            self.session.delete(pagamento)