from entitys import Ingresso
    
def teste_ingresso(nome, preco, quant_total, quant_vendida=0):
    ingresso = Ingresso(nome, preco, quant_total, quant_vendida)
    for i in range(0, quant_total+1): # Consigo vender mais ingresso que quant_total?
        try:
            ingresso.venda()
        except Exception as e:
            print(e)


teste_ingresso("Junqueira", 15, 20) # Caminho feliz
try:
    teste_ingresso("Queiroz", 40, 20, 50) # Consigo criar um evento que vendeu mais do que tem pra vender?
except Exception as e:
    print(e)
try:
    teste_ingresso("Matoso", -20, -12, -5) # Valores negativos devem ser tratados, possível erro do usuário.
except Exception as e:
    print(e)