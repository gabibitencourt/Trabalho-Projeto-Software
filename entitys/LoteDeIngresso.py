class LoteDeIngresso:
    def __init__(self, nome, preco, quant_total, quant_vendida=0):
        if quant_total < 0 or quant_vendida < 0 or preco < 0:
            raise Exception("Erro: Valor negativo")
        elif quant_total < quant_vendida:
            raise Exception("Erro: valor de quant_vendida invalido")
        
        self.nome = nome
        self.preco = preco
        self.quant_total = quant_total
        self.quant_vendida = quant_vendida

    def __str__(self):
            return f"""nome: {self.nome}
            preco: {self.preco}
            quantidade total: {self.quant_total}
            quantidade vendida: {self.quant_vendida}"""

    def venda(self):
        if self.quant_vendida == self.quant_total:
            raise Exception("Erro: Ingressos esgotados")
        self.quant_vendida += 1

    def get_nome(self):
         return self.nome

    def get_preco(self):
         return self.preco

    def get_quant_total(self):
         return self.quant_total

    def get_quant_vendida(self):
        return self.quant_vendida