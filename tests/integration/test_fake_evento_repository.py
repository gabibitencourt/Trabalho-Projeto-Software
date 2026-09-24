from datetime import date

from eventos.adapters.repository import FakeEventoRepository
from eventos.domain.model import Evento, StatusEvento


def criar_evento(identificador=1, status=StatusEvento.PLANEJADO):
    return Evento(
        identificador=identificador,
        nome="Conferencia de Software",
        data=date(2026, 10, 20),
        local="Niteroi",
        status=status,
    )


def test_adicionar_e_obter_evento_pelo_id():
    repository = FakeEventoRepository()
    evento = criar_evento()

    repository.adicionar(evento)

    assert repository.obter(evento.identificador) is evento


def test_obter_evento_com_id_inexistente_retorna_none():
    repository = FakeEventoRepository()

    assert repository.obter(999) is None


def test_listar_retorna_todos_os_eventos():
    repository = FakeEventoRepository()
    eventos = [criar_evento(1), criar_evento(2), criar_evento(3)]

    for evento in eventos:
        repository.adicionar(evento)

    eventos_listados = repository.listar()

    assert {evento.identificador for evento in eventos_listados} == {1, 2, 3}


def test_atualizar_evento_existente_substitui_o_evento_anterior():
    repository = FakeEventoRepository()
    evento_original = criar_evento()
    evento_atualizado = Evento(
        identificador=1,
        nome="Conferencia Atualizada",
        data=date(2026, 10, 20),
        local="Niteroi",
        status=StatusEvento.EM_ANDAMENTO,
    )
    repository.adicionar(evento_original)

    repository.atualizar(evento_atualizado)

    assert repository.obter(1) is evento_atualizado
    assert repository.obter(1).nome == "Conferencia Atualizada"
    assert repository.obter(1).status is StatusEvento.EM_ANDAMENTO
    assert len(repository.listar()) == 1


def test_atualizar_evento_inexistente_adiciona_o_evento():
    repository = FakeEventoRepository()
    evento = criar_evento()

    repository.atualizar(evento)

    assert repository.obter(evento.identificador) is evento
    assert repository.listar() == [evento]
