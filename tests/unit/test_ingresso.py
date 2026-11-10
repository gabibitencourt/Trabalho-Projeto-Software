from eventos.domain.model import (
    DescontoPercentual,
    LoteDeIngresso,
    PrecoIntegral,
)
import pytest
    
def teste_caminho_feliz(): # Caminho feliz
    ingresso = LoteDeIngresso(1, "Junqueira", 15, 20)
    for i in range(0, ingresso.quant_total):
        ingresso.venda()
    
def teste_limite_venda(): # Consigo vender mais ingresso que quant_total?
    ingresso = LoteDeIngresso(1, "Junqueira", 15, 20)
    with pytest.raises(Exception):
        for i in range(0, ingresso.quant_total+1): 
            ingresso.venda()

def teste_valores_negativos(): # Erro do usuário ou de outra função, valores negativos
    with pytest.raises(Exception):
        LoteDeIngresso(1, "Matoso", -20, -12, -5)

def teste_quant_vendido_invalida(): # Consigo criar um evento que vendeu mais do que tinha pra vender?
    with pytest.raises(Exception): 
        LoteDeIngresso(1, "Queiroz", 40, 20, 50)


def teste_lote_calcula_preco_com_estrategias_diferentes():
    lote = LoteDeIngresso(1, "Promocional", 100, 20)

    assert lote.calcular_preco(PrecoIntegral()) == 100
    assert lote.calcular_preco(DescontoPercentual(25)) == 75


def teste_desconto_percentual_invalido():
    with pytest.raises(ValueError):
        DescontoPercentual(101)