import pytest
from eventos.domain.model import Inscricao
from eventos.adapters.repository import FakeInscricaoRepository

def criar_inscricao(identificador=1, participante="Gabriela", lote="Lote 1", evento_id="EVT-01"):
    inscricao = Inscricao(identificador=identificador, participante=participante, lote=lote)
    inscricao.evento = evento_id 
    return inscricao

def test_repository_pode_adicionar_e_obter_inscricao():
    repo = FakeInscricaoRepository()
    inscricao = criar_inscricao(identificador=1)
    
    repo.adicionar(inscricao)
    resultado = repo.obter(1)
    
    assert resultado == inscricao
    assert resultado.identificador == 1

def test_repository_retorna_none_se_inscricao_nao_existe():
    repo = FakeInscricaoRepository()
    
    assert repo.obter(99) is None

def test_repository_pode_listar_inscricoes_por_participante():
    repo = FakeInscricaoRepository()
    repo.adicionar(criar_inscricao(identificador=1, participante="Gabriela"))
    repo.adicionar(criar_inscricao(identificador=2, participante="Samuel"))
    repo.adicionar(criar_inscricao(identificador=3, participante="Gabriela"))
    
    resultados = repo.listar_por_participante("Gabriela")
    
    assert len(resultados) == 2
    assert all(i.participante == "Gabriela" for i in resultados)

def test_repository_pode_listar_inscricoes_por_evento():
    repo = FakeInscricaoRepository()
    repo.adicionar(criar_inscricao(identificador=1, evento_id="PythonBrasil"))
    repo.adicionar(criar_inscricao(identificador=2, evento_id="PythonBrasil"))
    repo.adicionar(criar_inscricao(identificador=3, evento_id="CampusParty"))
    
    resultados = repo.listar_por_evento("PythonBrasil")
    
    assert len(resultados) == 2
    assert all(i.evento == "PythonBrasil" for i in resultados)

def test_repository_pode_atualizar_inscricao():
    repo = FakeInscricaoRepository()
    inscricao = criar_inscricao(identificador=1)
    repo.adicionar(inscricao)
    
    inscricao.confirmar()
    repo.atualizar(inscricao)
    
    resultado = repo.obter(1)
    assert resultado.status == inscricao.status

def test_repository_pode_remover_inscricao():
    repo = FakeInscricaoRepository()
    inscricao = criar_inscricao(identificador=1)
    repo.adicionar(inscricao)
    
    repo.remover(1)
    
    assert repo.obter(1) is None