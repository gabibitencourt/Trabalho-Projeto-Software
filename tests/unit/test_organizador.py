import pytest
from eventos.domain.model import Organizador, RoleOrganizador


def criar_organizador(role=RoleOrganizador.ORGANIZADOR):
    return Organizador(
        identificador=1,
        nome="Leonardo Cruz",
        email="leo@evento.com",
        role=role,
    )


def test_organizador_armazena_seus_dados_principais():
    org = criar_organizador()

    assert org.identificador == 1
    assert org.nome == "Leonardo Cruz"
    assert org.email == "leo@evento.com"
    assert org.role is RoleOrganizador.ORGANIZADOR


def test_role_do_organizador_tem_valores_fechados():
    with pytest.raises(ValueError, match="role invalida"):
        Organizador(1, "Leonardo", "leo@evento.com", role="qualquer_role")


def test_nao_cria_organizador_com_nome_vazio():
    with pytest.raises(ValueError, match="nome obrigatorio"):
        Organizador(1, "", "leo@evento.com")


def test_nao_cria_organizador_com_email_invalido():
    with pytest.raises(ValueError, match="email invalido"):
        Organizador(1, "Leonardo", "email_invalido")