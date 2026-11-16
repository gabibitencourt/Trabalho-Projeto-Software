# Análise de Frameworks

Este documento analisa os frameworks utilizados no sistema (**Flask**, **SQLAlchemy** e **pytest**), detalhando como cada integrante os utilizou no escopo do seu agregado/módulo.

---

## Análise — Arthur Siqueira Campos Alexandrino (@devalexandrino)

- **Agregado / Módulo:** `Evento` (classe `Evento` em `src/eventos/domain/model.py`, mapeamento da tabela `eventos` em `src/eventos/adapters/orm.py`, `AbstractEventoRepository` / `FakeEventoRepository` / `SqlAlchemyEventoRepository` em `src/eventos/adapters/repository.py`, serviços `criar_evento` e `encerrar_evento` em `src/eventos/service_layer/services.py`, rotas `/eventos` em `src/eventos/entrypoints/flask_app.py` e testes em `tests/unit/test_evento.py`, `tests/unit/test_services_evento.py`, `tests/integration/test_repository_evento.py` e `tests/e2e/test_eventos_api.py`).

### 1. Papel de cada framework no módulo de `Evento` e independência do domínio

No escopo do agregado `Evento`, os frameworks ficam restritos às bordas da arquitetura (`entrypoints/`, `adapters/` e `tests/`), enquanto a entidade `Evento` e seus casos de uso permanecem isolados de detalhes de infraestrutura:

- **Flask (`src/eventos/entrypoints/flask_app.py`):**
  - **Papel e camada:** Atua na camada de entrada (*Entrypoints*) expondo as rotas `POST /eventos`, `GET /eventos`, `GET /eventos/<int:identificador>` e `POST /eventos/<int:identificador>/encerrar`. Ele extrai o JSON da requisição (`request.get_json`), aciona `services.criar_evento` ou `services.encerrar_evento`, confirma a transação e serializa a instância de `Evento` com `_serializar_evento` e `jsonify`.
  - **Por que `Evento` não depende dele:** `Evento` (`src/eventos/domain/model.py`) e os serviços `criar_evento` e `encerrar_evento` (`src/eventos/service_layer/services.py`) não importam `flask`. A entidade opera apenas sobre tipos nativos (`int`, `str`, `datetime.date`, `StatusEvento`) e sinaliza violações de invariantes levantando `OperacaoInvalidaError` ou `ValueError`, sem conhecer objetos HTTP ou códigos de status.

- **SQLAlchemy (`src/eventos/adapters/orm.py` e `src/eventos/adapters/repository.py`):**
  - **Papel e camada:** Atua na camada de adaptadores (*Adapters*) definindo a tabela `eventos` e seu mapeamento imperativo (`mapper_registry.map_imperatively(Evento, eventos, ...)`) em `orm.py`, além de implementar `SqlAlchemyEventoRepository` (`session.add`, `session.get`, `session.query`, `session.merge`) em `repository.py`.
  - **Por que `Evento` não depende dele:** Como foi utilizado o mapeamento clássico (`map_imperatively`), a classe `Evento` não herda de `declarative_base()` nem declara `Column` no domínio. Tanto a refatoração OCP (`RegraAlteracaoLote` em `_regras_alteracao_lote`) quanto o padrão GoF Memento (`Evento.criar_memento` e `Evento.restaurar`) foram implementados em Python puro dentro de `Evento`, sem nenhuma dependência do SQLAlchemy.

- **pytest (`tests/unit/test_evento.py`, `tests/unit/test_services_evento.py`, `tests/integration/test_repository_evento.py` e `tests/e2e/test_eventos_api.py`):**
  - **Papel e camada:** Atua na camada de testes (`tests/`), executando a verificação das invariantes de `Evento`, dos serviços `criar_evento`/`encerrar_evento` (com `FakeEventoRepository`), da persistência (`SqlAlchemyEventoRepository`) e das rotas HTTP (`/eventos`).
  - **Por que `Evento` não depende dele:** A direção de dependência é unidirecional (`tests/ -> src/eventos/`). `Evento` não contém código de teste; sua testabilidade decorre de ser uma classe Python independente da infraestrutura.

### 2. Pontos de Inversão de Controle (IoC) no código de `Evento`

Enquanto uma **biblioteca** é chamada diretamente pelo nosso código (como `date.fromisoformat(data)` dentro de `services.criar_evento`, onde nosso código mantém o controle da execução), um **framework** inverte o controle: o framework detém o fluxo principal e **chama o código de `Evento`** quando determinados eventos ocorrem.

No código do agregado `Evento`, essa inversão de controle ocorre nos seguintes pontos:

1. **Despacho das rotas de `/eventos` pelo Flask (`src/eventos/entrypoints/flask_app.py`):**
   - As funções `criar_evento()`, `listar_eventos()`, `obter_evento(identificador)` e `encerrar_evento(identificador)` são registradas com `@app.post("/eventos")`, `@app.get("/eventos")`, `@app.get("/eventos/<int:identificador>")` e `@app.post("/eventos/<int:identificador>/encerrar")`.
   - O código do módulo nunca invoca essas funções diretamente: é o Flask quem recebe a requisição HTTP, converte `<int:identificador>` da URL e chama a função registrada (ou invoca o handler `@app.errorhandler(OperacaoInvalidaError)` quando `Evento.encerrar()` rejeita o encerramento por haver inscrições pendentes).

2. **Ciclo de vida das fixtures `repository` e `client` no pytest (`tests/integration/test_repository_evento.py` e `tests/e2e/test_eventos_api.py`):**
   - Em `test_repository_evento.py`, a fixture `@pytest.fixture def repository()` prepara o banco em memória e faz `yield SqlAlchemyEventoRepository(session), session`; em `test_eventos_api.py`, `@pytest.fixture def client()` faz `yield test_client`.
   - O pytest inspeciona a assinatura de cada teste (ex.: `def test_atualizar_evento_persiste_mudanca_de_status(repository):`), invoca a fixture antes do teste, injeta o `SqlAlchemyEventoRepository` como argumento, executa a função de teste e depois retoma o bloco `finally` pós-`yield` para fechar a sessão e limpar os mapeadores (`clear_mappers()`).

3. **Materialização de `Evento` pelo mapeamento clássico do SQLAlchemy (`src/eventos/adapters/orm.py`):**
   - Ao registrar `mapper_registry.map_imperatively(Evento, eventos, ...)` em `start_mappers()`, o SQLAlchemy passa a controlar a instanciação de `Evento` nas leituras do banco (`evento_repository.obter(1)`), criando a instância sem passar por `Evento.__init__` e populando seus atributos e sua coleção `_lotes` a partir dos registros do SQLite.

### 3. Padrões de projeto usados internamente pelos frameworks no código de `Evento`

1. **Data Mapper e Proxy (`InstrumentedList`) no SQLAlchemy (`src/eventos/adapters/orm.py` e `src/eventos/domain/model.py`):**
   - **Onde aparece:** no mapeamento `mapper_registry.map_imperatively(Evento, eventos, properties={"_lotes": relationship(..., collection_class=list)})` em `orm.py` (linhas 97–106) e no método `Evento.restaurar(memento)` em `model.py` (linha 167).
   - **Papel interno:** O SQLAlchemy aplica um **Data Mapper** para desacoplar `Evento` da tabela `eventos` e envolve `self._lotes` em um **Proxy** (`InstrumentedList`) que intercepta adições e leituras na lista para sincronizá-las com o banco. É por conta desse proxy que, ao implementar o padrão Memento em `Evento.restaurar()`, a lista é atualizada *in-place* (`self._lotes[:] = ...`) em vez de reatribuir `self._lotes = [...]`.

2. **Unit of Work e Identity Map na `Session` do SQLAlchemy (`src/eventos/adapters/repository.py` e `tests/integration/test_repository_evento.py`):**
   - **Onde aparece:** em `SqlAlchemyEventoRepository` (`self.session.add(evento)`, `self.session.get(Evento, identificador)`, `self.session.merge(evento)`, linhas 48–63 de `repository.py`) e nas chamadas a `session.commit()` e `session.expire_all()` em `test_repository_evento.py` (linhas 41–42 e 59–60).
   - **Papel interno:** A `Session` mantém um **Identity Map** que garante uma única instância de `Evento` por `identificador` na sessão (razão pela qual `test_repository_evento.py` chama `session.expire_all()` antes de `evento_repository.obter(1)` para forçar nova consulta ao banco) e funciona como uma **Unit of Work** que acumula as alterações feitas via `adicionar`/`atualizar` para enviá-las atomicamente no `session.commit()`.

3. **Factory em `sessionmaker` (SQLAlchemy) e Application Factory em `create_app` (Flask) (`tests/integration/test_repository_evento.py` e `tests/e2e/test_eventos_api.py`):**
   - **Onde aparece:** na criação da sessão `session = sessionmaker(bind=engine)()` em `test_repository_evento.py` (linha 17) e `test_eventos_api.py` (linha 14), e na chamada `app = create_app(session)` em `test_eventos_api.py` (linha 15).
   - **Papel interno:** `sessionmaker(bind=engine)` atua como uma fábrica configurada que encapsula a `engine` SQLite e instancia objetos `Session` sob demanda, enquanto `create_app(session)` aplica o padrão *Application Factory* no Flask para criar uma instância isolada da API de eventos em cada teste E2E.

### 4. O que mudaria no agregado `Evento` com um framework full-stack como o Django

Se o módulo de `Evento` tivesse sido implementado com **Django** em vez de Flask + SQLAlchemy:

- **`Evento` passaria de classe pura (Data Mapper) para Active Record (`models.Model`):** em vez de `Evento` ser uma classe Python independente em `src/eventos/domain/model.py` mapeada externamente em `orm.py`, ela herdaria de `django.db.models.Model`, misturando atributos de coluna (`models.CharField`, `models.DateField`) com regras de negócio.
- **Perda do encapsulamento estrito de `_lotes` e impacto em OCP e Memento:** hoje `Evento` protege `self._lotes` (expondo apenas `tuple(self._lotes)`) e obriga modificações a passarem por `adicionar_lote` e `alterar_lote` (onde rodam `_CicloDeVidaEvento` e as regras OCP `RegraAlteracaoLote`), além de permitir salvar e restaurar `EventoMemento` 100% em memória. No Django, a relação reversa de lotes seria um `RelatedManager` acoplado ao banco de dados, dificultando impedir alterações diretas fora da raiz do agregado e impossibilitando restaurar um `EventoMemento` sem tocar no banco.
- **Eliminação de `SqlAlchemyEventoRepository` e `FakeEventoRepository` vs. perda de velocidade nos testes unitários:** o Django dispensaria a escrita manual de `SqlAlchemyEventoRepository` (usando `Evento.objects.get()` e `evento.save()`), mas em troca os testes de `tests/unit/test_evento.py` e `tests/unit/test_services_evento.py` (que hoje rodam em memória com `FakeEventoRepository` sem criar banco) passariam a depender de `django.test.TestCase` com banco de dados relacional.
