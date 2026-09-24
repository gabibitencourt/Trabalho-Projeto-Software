import abc 
from eventos.domain.model import Evento, Inscricao


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
    def __init__(self, session):
        self.session = session

    def adicionar(self, evento: Evento):
        self.session.add(evento)

    def obter(self, identificador: int) -> Evento:
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
    def obter(self, identificador:int) -> Inscricao:
        raise NotImplementedError

    @abc.abstractmethod 
    def listar_por_participante(self, participante) ->list[Inscricao]:
        raise NotImplementedError

    @abc.abstractmethod
    def listar_por_evento(self, evento) ->list[Inscricao]:
        raise NotImplementedError

    @abc.abstractmethod
    def atualizar(self, inscricao: Inscricao):
        raise NotImplementedError

    @abc.abstractmethod
    def remover(self, identificador: int):
        raise NotImplementedError
    
class FakeInscricaoRepository(AbstractInscricaoRepository):
    def __init__(self):
        self._inscricoes = set()

    def adicionar(self, inscricao: Inscricao):
        self._inscricoes.add(inscricao)

    def obter(self, identificador:int) -> Inscricao:
        return next(
            (i for i in self._inscricoes if i.identificador == identificador),
            None
        )

    def listar_por_participante(self, participante) -> list[Inscricao]:
        return [i for i in self._inscricoes if i.participante == participante]

    def listar_por_evento(self, evento) -> list[Inscricao]:
        return [i for i in self._inscricoes if i.evento == evento]

    def atualizar(self, inscricao: Inscricao):
        self.remover(inscricao.identificador)
        self.adicionar(inscricao)

    def remover(self, identificador: int):
        inscricao = self.obter(identificador)
        if inscricao:
            self._inscricoes.remove(inscricao)