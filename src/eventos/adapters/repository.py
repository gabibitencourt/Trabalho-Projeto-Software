import abc 
from eventos.domain.model import Inscricao

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