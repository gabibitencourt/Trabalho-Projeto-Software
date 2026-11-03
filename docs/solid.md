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
- **Commit "depois":** `9e5a6d8`

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

---

## Refatoração — FelipeGMello

- **Agregado / Módulo:** Evento (`Evento`)
- **Princípio Violado:** SRP (Single Responsibility Principle — Princípio da Responsabilidade Única)
- **Commit "antes":** `e95754b` (FelipeGMello)
- **Commit "depois":** `bfb9d1d` (FelipeGMello)

### 1. Problema

A classe `Evento` controlava tanto o catálogo de lotes quanto as regras do ciclo de vida do evento. As validações de transição (`iniciar` e `encerrar`) e a condição de que os lotes só podem ser alterados enquanto o evento está planejado ficavam junto da gestão da coleção de lotes. Assim, mudanças nas regras de estado exigiam alterar a entidade que também coordena a coleção, espalhando a política de ciclo de vida por operações diferentes.

### 2. Trecho de Código Antes

```python
def _exigir_evento_planejado(self):
    if self.status is not StatusEvento.PLANEJADO:
        raise OperacaoInvalidaError(
            "nao e possivel alterar lotes de evento em andamento ou encerrado"
        )

def iniciar(self):
    if self.status is StatusEvento.EM_ANDAMENTO:
        raise OperacaoInvalidaError("evento ja esta em andamento")
    if self.status is StatusEvento.ENCERRADO:
        raise OperacaoInvalidaError("evento ja esta encerrado")
    self.status = StatusEvento.EM_ANDAMENTO

def encerrar(self, inscricoes_pendentes):
    if inscricoes_pendentes < 0:
        raise ValueError("a quantidade de inscricoes pendentes nao pode ser negativa")
    if self.status is StatusEvento.ENCERRADO:
        raise OperacaoInvalidaError("evento ja esta encerrado")
    if inscricoes_pendentes > 0:
        raise OperacaoInvalidaError(
            "nao e possivel encerrar evento com inscricoes pendentes"
        )
    self.status = StatusEvento.ENCERRADO
```

### 3. Refatoração

As regras de transição e a validação de estado para alteração de lotes foram extraídas para a política interna `_CicloDeVidaEvento`. A entidade `Evento` delega essas decisões e continua expondo os mesmos métodos, atributos e coleção de lotes; o mapeamento ORM também permanece inalterado.

O commit anterior de Felipe usado como referência é `e95754b`, no qual o código acima já estava presente. A extração foi registrada no commit `bfb9d1d`.

### 4. Como os testes garantiram que o comportamento não mudou

- Antes da refatoração, os testes focados de `Evento`, `LoteDeIngresso` e do repositório de eventos passaram: 23 testes.
- Após a refatoração, os testes existentes continuaram exercitando transições válidas e inválidas, encerramento com inscrições pendentes, bloqueio de alteração de lotes e integração com persistência.
- A suíte completa passou após a mudança: 111 testes.

### 5. Custo da refatoração

A mudança adiciona uma classe interna e uma camada de delegação entre `Evento` e as regras de ciclo de vida. Esse custo compensa porque as políticas de status ficam concentradas em um único lugar, enquanto `Evento` preserva sua interface e responsabilidade de coordenar o agregado e seu catálogo de lotes.

---

## Refatoração — Arthur Siqueira Campos Alexandrino (@devalexandrino)

- **Agregado / Módulo:** Evento (`Evento` em `src/eventos/domain/model.py`)
- **Princípio Violado:** OCP (Open/Closed Principle — Princípio Aberto/Fechado)
- **Commit "antes":** `53a858b` (16/09/2026)
- **Commit "depois":** ` a3e8858744`

### 1. Problema

No commit `53a858b` (anterior a 06/10/2026), o método `Evento.alterar_lote` apenas verificava se o evento estava no status `PLANEJADO`, localizava o lote pelo `identificador` e substituía diretamente a instância na coleção (`self._lotes[indice] = lote_atualizado`).

Isso expunha uma violação do Princípio Aberto/Fechado (OCP) diante das regras de negócio que comparam o estado anterior do lote (`lote_atual`) com o novo (`lote_atualizado`):
- A invariante prevista na especificação do agregado (`PROPOSTA.md`, seção 4.1: *"Não é possível reduzir a quantidade de um lote para um valor menor do que já foi vendido"*) não pode ser garantida isoladamente pelo construtor de `LoteDeIngresso` quando um novo objeto `LoteDeIngresso` (com `quant_vendida=0` por padrão) é passado para substituir um lote que já teve vendas registradas em `Evento`.
- Além disso, evoluções plausíveis de requisitos para alteração de lotes (como proibir alteração de preço de um lote que já possui ingressos vendidos ou impedir renomeação de lotes ativos) obrigavam a abrir e modificar diretamente o método `Evento.alterar_lote` para encadear novos blocos `if ...: raise OperacaoInvalidaError(...)`.

### 2. Trecho de Código Antes

```python
class Evento:
	def __init__(self, identificador, nome, data, local, status):
		self.identificador = identificador
		self.nome = nome
		self.data = data
		self.local = local
		self.status = status
		self._lotes = []

	def alterar_lote(self, identificador_lote, lote_atualizado):
		self._exigir_evento_planejado()
		for indice, lote in enumerate(self._lotes):
			if lote.identificador == identificador_lote:
				self._lotes[indice] = lote_atualizado
				return
		raise OperacaoInvalidaError("lote nao encontrado")
```

### 3. Refatoração

Extraí o contrato abstrato `RegraAlteracaoLote` com o método `validar(lote_atual, lote_atualizado)` e implementei as regras concretas `RegraNaoReduzirCapacidadeAbaixoDoVendido` (ativa por padrão em `Evento`) e `RegraNaoAlterarPrecoComVendas`. A classe `Evento` passou a iterar sobre uma coleção imutável de regras (`self._regras_alteracao_lote`) antes de substituir o lote:

```python
class RegraAlteracaoLote(abc.ABC):
	@abc.abstractmethod
	def validar(self, lote_atual, lote_atualizado):
		raise NotImplementedError


class RegraNaoReduzirCapacidadeAbaixoDoVendido(RegraAlteracaoLote):
	def validar(self, lote_atual, lote_atualizado):
		if lote_atualizado.quant_total < lote_atual.quant_vendida:
			raise OperacaoInvalidaError(
				"nao e possivel reduzir a quantidade do lote abaixo da quantidade ja vendida"
			)


class RegraNaoAlterarPrecoComVendas(RegraAlteracaoLote):
	def validar(self, lote_atual, lote_atualizado):
		if lote_atual.quant_vendida > 0 and lote_atualizado.preco != lote_atual.preco:
			raise OperacaoInvalidaError(
				"nao e possivel alterar o preco de lote com ingressos ja vendidos"
			)


class Evento:
	_regras_alteracao_lote = (RegraNaoReduzirCapacidadeAbaixoDoVendido(),)

	def __init__(
		self,
		identificador,
		nome,
		data,
		local,
		status,
		regras_alteracao_lote=None,
	):
		...
		if regras_alteracao_lote is not None:
			self._regras_alteracao_lote = tuple(regras_alteracao_lote)

	def alterar_lote(self, identificador_lote, lote_atualizado):
		_CicloDeVidaEvento.exigir_planejado(self.status)
		for indice, lote in enumerate(self._lotes):
			if lote.identificador == identificador_lote:
				for regra in self._regras_alteracao_lote:
					regra.validar(lote, lote_atualizado)
				self._lotes[indice] = lote_atualizado
				return
		raise OperacaoInvalidaError("lote nao encontrado")
```

Com isso, `Evento.alterar_lote` fica **fechado para modificação** e **aberto para extensão**: novas políticas de validação de alteração de lote são adicionadas criando novas subclasses de `RegraAlteracaoLote`, sem editar `Evento`. A definição de `_regras_alteracao_lote` também como atributo de classe garante compatibilidade total com o mapeamento imperativo do SQLAlchemy (`map_imperatively`), que reconstrói instâncias do banco sem invocar `__init__`.

### 4. Como os testes garantiram que o comportamento não mudou

- Todos os testes pré-existentes de `Evento` (`tests/unit/test_evento.py`), serviços (`tests/unit/test_services_evento.py`), repositório SQLAlchemy (`tests/integration/test_repository_evento.py`) e rotas Flask (`tests/e2e/test_eventos_api.py`) continuaram passando sem alteração.
- Foram adicionados 3 novos testes unitários em `tests/unit/test_evento.py`:
  1. `test_nao_altera_lote_reduzindo_quantidade_abaixo_do_ja_vendido`: garante que a regra padrão bloqueia a redução de `quant_total` abaixo da `quant_vendida` do lote original;
  2. `test_altera_lote_aceita_extensao_com_regra_de_bloqueio_de_preco_apos_venda`: verifica a composição com `RegraNaoAlterarPrecoComVendas`;
  3. `test_altera_lote_permite_nova_regra_customizada_sem_modificar_evento`: demonstra a introdução de uma nova regra (`RegraNaoAlterarNomeDoLote`) estendendo `RegraAlteracaoLote` sem modificar `Evento`.
- A suíte completa passou a contar com 114 testes passando (111 anteriores + 3 novos).

### 5. Custo da refatoração

- **Custo:** adição de uma classe abstrata (`RegraAlteracaoLote`), duas classes concretas de regra e uma camada de indireção na leitura do fluxo de `alterar_lote`, além de um parâmetro opcional no construtor de `Evento`.
- **Por que compensa:** protege a invariante de capacidade vendida do agregado `Evento`, isola cada regra de negócio em uma classe coesa e testável de forma independente e permite adicionar ou combinar novas políticas de alteração de lotes sem tocar no código da entidade `Evento` nem no mapeamento ORM.
