import pytest
from eventos.domain.model import Participante, Documento, Email

def criar_participante():
    return Participante(
        identificador=1,
        nome="Gabriela Bitencourt",
        email="gabi@email.com",
        documento="123.456.789-00",
    )

def test_participante_armazena_seus_dados_principais():
    participante = criar_participante()

    assert participante.identificador == 1
    assert participante.nome == "Gabriela Bitencourt"
    assert participante.email == "gabi@email.com"
    assert participante.documento == "12345678900"

def test_nao_cria_participante_com_nome_vazio():
    with pytest.raises(ValueError, match="nome obrigatorio"):
        Participante(1, "", "gabi@email.com", "12345678900")

def test_nao_cria_participante_com_email_invalido():
    with pytest.raises(ValueError, match="email invalido"):
        Participante(1, "Gabriela", "email_invalido", "12345678900")

def test_nao_cria_participante_com_documento_invalido():
    with pytest.raises(ValueError, match="documento invalido"):
        Participante(1, "Gabriela", "gabi@email.com", "123")

def test_altera_email_do_participante():
    participante = criar_participante()

    participante.alterar_email("novo_email@email.com")

    assert participante.email == "novo_email@email.com"

def test_nao_altera_email_para_formato_invalido():
    participante = criar_participante()

    with pytest.raises(ValueError, match="email invalido"):
        participante.alterar_email("email_sem_arroba")

def test_value_object_email_valido_e_normalizado():
    email = Email("  GABI@EMAIL.COM ")
    assert email.valor == "gabi@email.com"

def test_value_object_email_invalido_dispara_erro():
    with pytest.raises(ValueError, match="email invalido"):
        Email("email_sem_arroba")

def test_value_object_documento_valido_e_sanitizado():
    doc = Documento("123.456.789-00")
    assert doc.valor == "12345678900"

def test_value_object_documento_invalido_dispara_erro():
    with pytest.raises(ValueError, match="documento invalido"):
        Documento("123")