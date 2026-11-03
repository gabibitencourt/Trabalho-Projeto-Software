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

---

## Refatoração — Samuel Carvalho Dias (@SamuelCDiias)

- **Agregado / Módulo:** Inscrição (camada de serviço e entrypoint Flask)
- **Princípio Violado:** DIP (Dependency Inversion Principle — Princípio da Inversão de Dependência)
- **Commit "antes":** `e3fc05d` (28/09/2026)
- **Commit "depois":** `COLOCAR_HASH_AQUI`

### 1. Problema
Os casos de uso de inscrição (`criar_inscricao`, `confirmar_inscricao` e `cancelar_inscricao`) não confirmavam a transação. Quem fazia isso era a rota Flask, chamando `session.commit()` direto na sessão do SQLAlchemy. Ou seja, uma regra da aplicação ("ao final do caso de uso, salvar") dependia de um detalhe concreto de infraestrutura e estava no lugar errado.

Na prática isso trazia dois problemas:
- Os testes unitários com `FakeInscricaoRepository` não conseguiam verificar se o caso de uso salvava ou não, porque o commit só acontecia na rota (só os testes e2e passavam por ele).
- Qualquer outro ponto de entrada (um script, uma CLI, outro serviço) que chamasse esses serviços teria que lembrar de chamar `session.commit()`, e se esquecesse, a inscrição não seria gravada.

### 2. Trecho de Código Antes
```python
# services.py
def confirmar_inscricao(identificador, repositorio):
    inscricao = obter_inscricao(identificador, repositorio)
    inscricao.confirmar()
    repositorio.atualizar(inscricao)
    return inscricao

# flask_app.py
@app.post("/inscricoes/<int:identificador>/confirmar")
def confirmar_inscricao(identificador):
    inscricao = services.confirmar_inscricao(identificador, repository)
    session.commit()
    return jsonify(_serializar_inscricao(inscricao))
```

### 3. Refatoração
Adicionei o método abstrato `commit()` em `AbstractInscricaoRepository`. O `SqlAlchemyInscricaoRepository` implementa chamando `self.session.commit()` e o `FakeInscricaoRepository` só marca `commitou = True`. Os três serviços de inscrição passaram a chamar `repositorio.commit()` no final, e as rotas `POST /inscricoes`, `/confirmar` e `/cancelar` não chamam mais `session.commit()`.

```python
# services.py
def confirmar_inscricao(identificador, repositorio):
    inscricao = obter_inscricao(identificador, repositorio)
    inscricao.confirmar()
    repositorio.atualizar(inscricao)
    repositorio.commit()
    return inscricao

# flask_app.py
@app.post("/inscricoes/<int:identificador>/confirmar")
def confirmar_inscricao(identificador):
    inscricao = services.confirmar_inscricao(identificador, repository)
    return jsonify(_serializar_inscricao(inscricao))
```

Agora o serviço depende só da abstração (`AbstractInscricaoRepository`), e não da `Session` do SQLAlchemy.

### 4. Como os testes garantiram que o comportamento não mudou
- Os testes e2e de `tests/e2e/test_inscricoes_api.py` continuaram passando sem nenhuma alteração.
- Os testes do domínio (`tests/unit/test_inscricao.py`) e de integração (`tests/integration/test_sqlalchemy_inscricao_repository.py`) também passaram sem mudança.
- Criei `tests/unit/test_services_inscricao.py`, com 3 testes que usam o `FakeInscricaoRepository` e verificam que cada caso de uso faz o commit (`repo.commitou is True`). Antes isso não dava para testar sem banco.
- Resultado: 111 testes passando (108 antes + 3 novos).

### 5. Custo da refatoração
- Mais um método na interface do repositório, que todas as implementações precisam ter.
- O repositório passa a ter uma responsabilidade a mais (confirmar a transação). Isso é uma simplificação: o certo seria uma Unit of Work separada, como está proposto no ADR-004. Fiz assim porque a mudança fica pequena e só no meu módulo, sem mexer no código dos outros agregados.
- Só os casos de uso de inscrição foram alterados; as outras rotas ainda chamam `session.commit()`.

Compensa porque o caso de uso fica completo sozinho (não depende da rota lembrar de salvar), dá para testar o commit sem banco e é um passo em direção à Unit of Work do ADR-004.
