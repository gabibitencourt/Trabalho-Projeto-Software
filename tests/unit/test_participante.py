import pytest
from eventos.domain.model import Participante, Documento, Email, ParticipanteEstudanteDecorator, ParticipanteVIPDecorator

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

def test_gof_decorator_participante_padrao_sem_desconto():
    p = Participante(1, "Gabriela", "gabi@email.com", "12345678900")
    assert p.obter_desconto_ingresso() == 0.0
    assert p.obter_tipo_credencial() == "PADRÃO"

def test_gof_decorator_participante_vip():
    p_base = Participante(1, "Gabriela Bitencourt", "gabi@email.com", "12345678900")
    p_vip = ParticipanteVIPDecorator(p_base)

    assert p_vip.nome == "Gabriela Bitencourt"
    assert p_vip.obter_desconto_ingresso() == 0.20
    assert "VIP" in p_vip.obter_tipo_credencial()

def test_gof_decorator_participante_estudante_meia_entrada():
    p_base = Participante(1, "Gabriela", "gabi@email.com", "12345678900")
    p_estudante = ParticipanteEstudanteDecorator(p_base, matricula_estudante="2026100123")

    assert p_estudante.obter_desconto_ingresso() == 0.50
    assert "ESTUDANTE" in p_estudante.obter_tipo_credencial()

def test_gof_decorator_estudante_sem_matricula_dispara_erro():
    p_base = Participante(1, "Gabriela", "gabi@email.com", "12345678900")
    with pytest.raises(ValueError, match="matricula de estudante obrigatoria"):
        ParticipanteEstudanteDecorator(p_base, matricula_estudante="")

def test_gof_decorator_combina_vip_e_estudante():
    p_base = Participante(1, "Gabriela", "gabi@email.com", "12345678900")
    p_vip = ParticipanteVIPDecorator(p_base)
    p_combo = ParticipanteEstudanteDecorator(p_vip, matricula_estudante="2026100123")

    assert p_combo.obter_desconto_ingresso() == 0.50
    assert "VIP" in p_combo.obter_tipo_credencial()
    assert "ESTUDANTE" in p_combo.obter_tipo_credencial()