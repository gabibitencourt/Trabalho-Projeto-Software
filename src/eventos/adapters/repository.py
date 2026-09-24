import abc

from sqlalchemy.orm import Session

from eventos.domain.model import Inscricao


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
        if inscricao is not None:
            self.session.delete(inscricao)
