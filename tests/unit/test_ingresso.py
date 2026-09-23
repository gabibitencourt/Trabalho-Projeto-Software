from eventos.domain.model import LoteDeIngresso
import pytest
    
def teste_caminho_feliz(): # Caminho feliz
    ingresso = LoteDeIngresso("Junqueira", 15, 20)
    for i in range(0, ingresso.quant_total):
        ingresso.venda()
    
def teste_limite_venda(): # Consigo vender mais ingresso que quant_total?
    ingresso = LoteDeIngresso("Junqueira", 15, 20)
    with pytest.raises(Exception):
        for i in range(0, ingresso.quant_total+1): 
            ingresso.venda()

def teste_valores_negativos(): # Erro do usuário ou de outra função, valores negativos
    with pytest.raises(Exception):
        LoteDeIngresso("Matoso", -20, -12, -5)

def teste_quant_vendido_invalida(): # Consigo criar um evento que vendeu mais do que tinha pra vender?
    with pytest.raises(Exception): 
        LoteDeIngresso("Queiroz", 40, 20, 50)