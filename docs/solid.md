# Análise e Refatoração SOLID

Este documento registra as refatorações realizadas pelos integrantes do grupo para corrigir violações dos princípios SOLID identificadas no código da Fase 1.

---

## Refatoração — Gabriela Bitencourt Freire da Silva (@gabibitencourt)

- **Agregado / Módulo:** Inscrição (`Participante`)
- **Princípio Violado:** SRP (Single Responsibility Principle — Princípio da Responsabilidade Única)

### 1. Problema 
A classe `Participante` acumulava responsabilidades distintas: gerenciar a identidade do participante e executar validações de baixo nível (expressões regulares para limpeza de CPF/CNPJ e tratamento de strings de e-mail). Qualquer mudança nas regras de sanitização de documentos ou validação de e-mail exigia modificar a classe principal da entidade do domínio.

### 2. Trecho de Código Antes
```python
class Participante:
    def __init__(self, identificador, nome, email, documento):
        if not nome or not nome.strip():
            raise ValueError("nome obrigatorio")

        doc_limpo = re.sub(r"\D", "", documento or "")
        if len(doc_limpo) not in (11, 14):
            raise ValueError("documento invalido")

        if not email or "@" not in email:
            raise ValueError("email invalido")

        self.identificador = identificador
        self.nome = nome.strip()
        self.email = email.lower().strip()
        self.documento = doc_limpo
```

### 3. Refatoração

Realizei a extração das responsabilidades de validação para os Value Objects de Documento e Email. A classe Participante passou a delegar essas veiuficações na construção, mantendo acesso às propriedades sanitizadas via @property 