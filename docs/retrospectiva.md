# Retrospectiva da Arquitetura

Este documento responde se o grupo escolheria novamente a arquitetura adotada no sistema após conviver com ela ao longo da Fase 2, revisitar as previsões do Checkpoint 1 e avaliar o impacto real das camadas durante as refatorações SOLID e a aplicação dos padrões GoF.

---

## Análise — Arthur Siqueira Campos Alexandrino (@devalexandrino)

- **Escopo avaliado:** Agregado `Evento` (`Evento`, `RegraAlteracaoLote`, `RegraNaoReduzirCapacidadeAbaixoDoVendido`, `RegraNaoAlterarPrecoComVendas`, `EventoMemento`, `_InstantaneoLote` e `HistoricoEvento` em `src/eventos/domain/model.py`; `AbstractEventoRepository`, `FakeEventoRepository` e `SqlAlchemyEventoRepository` em `src/eventos/adapters/repository.py`; mapeamento da tabela `eventos` em `src/eventos/adapters/orm.py`; casos de uso `criar_evento` e `encerrar_evento` em `src/eventos/service_layer/services.py`; rotas `/eventos` em `src/eventos/entrypoints/flask_app.py` e suítes de teste em `tests/unit/test_evento.py`, `tests/unit/test_services_evento.py`, `tests/integration/test_repository_evento.py` e `tests/e2e/test_eventos_api.py`).

### 1. Revisitação do Checkpoint 1 e trade-offs na prática

No Checkpoint 1 (commit `03374aa`), defini na seção de **Requisitos arquiteturais** de `docs/arquitetura.md` três atributos de qualidade em ordem de prioridade: **1º Testabilidade**, **2º Integridade e Consistência das Regras de Negócio (Confiabilidade)** e **3º Modificabilidade e Manutenibilidade**, além do **ADR-002** sobre o desacoplamento entre `Evento.encerrar(inscricoes_pendentes)` e o agregado `Inscricao`.

Ao final da Fase 2, o balanço entre essas previsões e a prática foi o seguinte:

- **Previsões que se confirmaram:**
  - A **Testabilidade** e a **Integridade das Regras de Negócio** no domínio se confirmaram integralmente. Os 22 testes unitários de `tests/unit/test_evento.py` e os 5 testes de serviço em `tests/unit/test_services_evento.py` rodam em memória em milissegundos, sem subir Flask ou SQLite, garantindo que nenhuma transição inválida (iniciar evento encerrado, alterar lote com evento em andamento, reduzir capacidade abaixo do vendido ou encerrar evento com inscrições pendentes) corrompa o estado do agregado.
  - A decisão registrada no **ADR-002** provou seu valor durante toda a Fase 2: como `Evento.encerrar` recebe apenas a contagem inteira de pendências, pude refatorar e estender `Evento` nos Checkpoints 2 e 3 sem ser afetado pelas mudanças que outros integrantes fizeram em `Inscricao` (Factory Method) ou `Pagamento` (State e Observer).

- **Trade-offs que mais pesaram na prática:**
  - **Vazamento sutil do mapeamento imperativo (`map_imperatively`) para o design do domínio:** no Checkpoint 1, assumimos que o mapeamento clássico em `orm.py` tornava `domain/model.py` 100% alheio ao SQLAlchemy. Na prática, descobrimos na Fase 2 que o SQLAlchemy reconstrói instâncias de `Evento` vindas do banco **sem chamar `__init__`** e substitui `self._lotes` por uma `InstrumentedList`. Isso exigiu cuidados extras no domínio que só existem por causa do ORM.
  - **Alto custo de cerimônia (*boilerplate*) e lacunas de integração entre camadas:** enquanto o modelo de domínio evoluía rápido, conectar qualquer contrato entre agregados até a ponta HTTP exigia coordenar `repository.py`, `orm.py`, `services.py` e `flask_app.py`. Um exemplo concreto é que a rota `POST /eventos/<id>/encerrar` permaneceu retornando `501 Not Implemented` no teste E2E (`tests/e2e/test_eventos_api.py`) porque `SqlAlchemyInscricaoRepository` não implementou `listar_por_evento`, e as rotas de `/eventos` em `flask_app.py` continuaram chamando `session.commit()` diretamente por falta de uma *Unit of Work* unificada.

### 2. Evidências da Fase 2: Onde as camadas facilitaram e onde atrapalharam

- **Onde as camadas facilitaram:**
  1. **Refatoração SOLID (OCP em `Evento.alterar_lote`, commit `a3e8858744`):** para corrigir a violação do Princípio Aberto/Fechado, extraí a abstração `RegraAlteracaoLote` e as regras `RegraNaoReduzirCapacidadeAbaixoDoVendido` e `RegraNaoAlterarPrecoComVendas`. Toda a mudança ficou contida em `src/eventos/domain/model.py` e `tests/unit/test_evento.py`, com **zero linhas alteradas** em `orm.py`, `repository.py`, `services.py` ou `flask_app.py`, confirmando a métrica de modificabilidade prevista no Checkpoint 1.
  2. **Padrão GoF Memento (`EventoMemento` e `HistoricoEvento`, commits `b9c4904d833` e `0fe4e20`):** foi possível implementar a captura e restauração de instantâneos imutáveis do evento e do seu catálogo de lotes (`_InstantaneoLote`) inteiramente na camada de domínio e validá-la com 4 novos testes unitários em `tests/unit/test_evento.py`, sem precisar alterar o esquema de tabelas em `orm.py`.

- **Onde as camadas e a infraestrutura atrapalharam:**
  1. **Reconstrução sem `__init__` no ORM (Checkpoint 2):** ao introduzir `_regras_alteracao_lote` na refatoração OCP de `Evento`, não bastou inicializar `self._regras_alteracao_lote` dentro de `Evento.__init__`. Como `SqlAlchemyEventoRepository.obter()` hidrata `Evento` via `map_imperatively` sem executar `__init__`, foi obrigatório definir `_regras_alteracao_lote = (RegraNaoReduzirCapacidadeAbaixoDoVendido(),)` também como atributo de classe em `Evento` (`model.py`, linha 145) para evitar `AttributeError` em instâncias carregadas do banco.
  2. **Coleção instrumentada (`InstrumentedList`) no Memento (Checkpoint 3):** em `Evento.restaurar(memento)` (`model.py`, linha 243), reatribuir `self._lotes = [...]` sobrescreveria o proxy `InstrumentedList` injetado pelo `relationship` de `orm.py` (linhas 101–105), quebrando o rastreamento de `cascade="all, delete-orphan"` do SQLAlchemy. Foi necessário atualizar a lista *in-place* com fatiamento (`self._lotes[:] = [instantaneo.reconstruir() for instantaneo in memento._lotes]`).

### 3. Decisão final: Escolheria essa arquitetura de novo?

**Decisão:** Para um projeto de produção real, **trocaria a combinação de microframework (Flask + mapeamento clássico manual) por uma arquitetura híbrida apoiada em um framework *full-stack* robusto (como Laravel, ou Django no ecossistema Python)**, mantendo classes de domínio ricas e padrões GoF apenas no núcleo de regras críticas.

**Justificativa:**
Conviver com a arquitetura do livro-texto (*Ports & Adapters* com mapeamento imperativo, repositórios abstratos, *Fake Repositories* e Flask puro) foi excelente do ponto de vista didático para exercitar TDD, SOLID (OCP) e GoF (Memento) em um domínio isolado. Contudo, na prática, pagamos um preço alto de *boilerplate* manual e de acoplamento invisível com o `map_imperatively`, sem contar com recursos essenciais para levar um sistema de venda de ingressos e eventos para produção (autenticação, controle de permissões de organizadores, migrações versionadas de banco, *jobs*/filas para pagamento, validação declarativa de payloads e transações atômicas nativas). Em um sistema real, utilizar um framework mais completo e opinativo como o **Laravel** (ou uma abordagem híbrida em um framework *full-stack* maduro) entregaria toda essa infraestrutura pronta e padronizada, permitindo concentrar o esforço de engenharia exclusivamente nas invariantes de negócio de `Evento`, `Lote`, `Inscricao` e `Pagamento`, sem precisar reinventar o encanamento arquitetural a cada rota.

---

## Análise — Gabriela Bitencourt Freire da Silva (@gabibitencourt)

- **Escopo avaliado:** Entidade `Participante`, Value Objects (`Documento` e `Email`) e hierarquia `Decorator` (`AbstractParticipante`, `ParticipanteDecorator`, `ParticipanteVIPDecorator`, `ParticipanteEstudanteDecorator`) em `src/eventos/domain/model.py` e `tests/unit/test_participante.py`.

### 1. Revisitação do Checkpoint 1 e trade-offs na prática

No Checkpoint 1, previmos que isolar o domínio dos frameworks privilegiaria a **testabilidade** e a **manutenibilidade** ao custo de maior complexidade estrutural. Na prática, esse *trade-off* se confirmou: consegui evoluir as regras de `Participante` e rodar todos os 15 testes unitários de `tests/unit/test_participante.py` em frações de segundo, sem inicializar banco de dados ou servidor HTTP.

Por outro lado, o custo que mais pesou no dia a dia foi a **fricção com o mapeamento imperativo (`map_imperatively`) do SQLAlchemy** e a manutenção de repositórios duplos (`FakeInscricaoRepository` e `SqlAlchemyInscricaoRepository`) para fluxos simples de cadastro e consulta.

### 2. Evidências da Fase 2: Onde as camadas facilitaram e onde atrapalharam

- **Onde facilitou (SOLID e GoF sem tocar na infraestrutura):** Tanto a refatoração de SRP (extração das regras de sanitização e validação para `Documento` e `Email`) quanto a introdução do padrão estrutural **Decorator** (`ParticipanteVIPDecorator` e `ParticipanteEstudanteDecorator`) ocorreram 100% em Python puro dentro de `src/eventos/domain/model.py`. Como a camada de domínio não depende do banco nem da API, não foi necessário criar migrações na tabela `participantes` em `orm.py` nem alterar rotas em `flask_app.py`.
- **Onde atrapalhou (acoplamento implícito com o ORM):** Mesmo sem importar o SQLAlchemy no domínio, `Participante` precisa respeitar a forma como `orm.py` mapeia suas colunas. Ao tentar encapsular `email` e `documento` com `@property` e atributos privados (`_email`, `_documento`), a persistência falhou com `IntegrityError` (`NOT NULL constraint failed: participantes.email`), exigindo manter os atributos diretos `self.email` e `self.documento` na classe e ajustar a interface `AbstractParticipante` para abstrair apenas os comportamentos (`obter_desconto_ingresso` e `obter_tipo_credencial`).

### 3. Decisão final: Escolheria essa arquitetura de novo?

**Decisão:** Adotaria uma **arquitetura híbrida**.

**Justificativa:** Para o núcleo de domínio — onde vivem validações de invariantes (`Documento`, `Email`) e extensões dinâmicas de comportamento (`Decorator` de categorias de participante) —, manter classes Python puras desacopladas de frameworks compensou claramente pela segurança e velocidade dos testes unitários. Porém, para operações puramente cadastrais de participantes e inscrições, eliminaria a camada de `FakeRepository` e simplificaria os serviços, usando diretamente o SQLite em memória nos testes, que já oferece execução rápida sem duplicar código de persistência.domínio realmente exige.

---

## Análise — Felipe Gomes de Mello (@FelipeGMello)

- **Escopo avaliado:** Agregado `LoteDeIngresso`, incluindo suas regras de criação e venda, o padrão GoF Strategy aplicado ao cálculo de preço, testes unitários e integração com as camadas de serviço, persistência e API.

### 1. Revisitação do Checkpoint 1 e trade-offs na prática

No Checkpoint 1, registrei que a implementação do lote “não foi tanta coisa”: uma classe e testes para criação e venda. Para aquele escopo, a previsão se confirmou. As regras de capacidade e venda ficaram em um objeto simples, e os testes unitários podem instanciá-lo diretamente, sem iniciar Flask ou banco de dados.

O que eu não considerei naquele momento foi o custo de evolução do sistema ao redor da entidade. Ao persistir e expor o lote, a mesma funcionalidade passou a envolver mapeamento ORM, repositório, serviço, rota e testes de integração ou E2E. Na Fase 2, a aplicação da Strategy também acrescentou uma interface e classes concretas. O trade-off que mais pesou foi, portanto, a testabilidade e o isolamento do domínio em troca de mais estrutura e trabalho para conectar um caso de uso de ponta a ponta.

### 2. Evidências da Fase 2: Onde as camadas facilitaram e onde atrapalharam

- **Onde facilitou:** Implementei `EstrategiaPreco`, `PrecoIntegral` e `DescontoPercentual` junto de `LoteDeIngresso.calcular_preco`, sem importar Flask ou SQLAlchemy e sem alterar o esquema de persistência. Em `tests/unit/test_ingresso.py`, o mesmo lote é testado com preço integral e desconto de 25% (100 e 75), e outro teste verifica a rejeição de desconto acima do limite. Isso demonstra que as políticas podem ser verificadas isoladamente e que uma nova regra não precisa virar um condicional dentro da entidade.
- **Limite observado:** O teste exercita a Strategy diretamente, mas as rotas e os serviços atuais de lote não escolhem nem passam uma estratégia. Assim, a extensão está implementada e testada no domínio, mas ainda não altera o preço retornado ou cobrado pelo fluxo da aplicação. Para torná-la uma funcionalidade de usuário, será necessário decidir onde a política é selecionada e integrá-la ao caso de uso, sem misturar essa decisão à persistência.
- **Onde as camadas atrapalharam:** A separação exige manter mapeamento e repositório além do modelo de domínio, e uma mudança que atravessa o sistema precisa coordenar esses componentes. A análise arquitetural do projeto registra, como exemplo, que o caso de criação de lote envolveu quatro arquivos e 127 linhas. Essa estrutura facilita isolar responsabilidades, mas pesa para funcionalidades pequenas; também exige atenção para que o mapeamento clássico e os contratos entre agregado, serviço e repositório permaneçam consistentes.

### 3. Decisão final: escolheria essa arquitetura de novo?

**Decisão:** Manteria uma arquitetura híbrida: domínio e políticas de negócio em Python puro, com frameworks e persistência nas bordas, mas aplicaria as abstrações de forma proporcional à necessidade.

**Justificativa:** Para invariantes e cálculos com variações reais, como venda limitada à capacidade e políticas de preço, o isolamento permite testes rápidos e evita que regras dependam de HTTP ou banco. A Strategy faz sentido se surgirem diferentes políticas que precisem ser selecionadas pelo fluxo da aplicação; se houver somente preço integral, as classes adicionais seriam complexidade sem benefício efetivo. Também manteria o mapeamento clássico enquanto o desacoplamento do domínio for um requisito, aceitando seu custo de configuração.

Não substituiria toda a solução por um framework full-stack nem introduziria mais camadas automaticamente. Para problemas transacionais entre inscrição e lote, priorizaria primeiro a fronteira de transação (Unit of Work) descrita no ADR-004 e só depois mecanismos de eventos, conforme a necessidade. Assim, preservaria a testabilidade onde ela protege regras importantes e evitaria abstrações que ainda não tenham um uso concreto.

## Análise — João Marcello da Costa (@JoaoMarcelloCosta2000)

- **Escopo avaliado:** Entidades `CheckIn` / `Inscricao` e agregado `Pagamento`, incluindo persistência (`AbstractPagamentoRepository`, `FakePagamentoRepository`, `SqlAlchemyPagamentoRepository`), refatoração SOLID (SRP/DIP nos casos de uso de pagamento) e aplicação do padrão GoF **Observer** (`ObservadorPagamento`, `InscricaoSyncObserver`, `AuditoriaPagamentoObserver`, `NotificacaoPagamentoObserver`) em `src/eventos/domain/model.py` e `tests/unit/test_pagamento_observer.py`.

### 1. Revisitação do Checkpoint 1 e trade-offs na prática

No Checkpoint 1, optamos por manter as invariantes de `CheckIn` (`Inscricao.realizar_checkin`) e `Pagamento` isoladas em Python puro e utilizar o padrão Repository (`AbstractPagamentoRepository` + `FakePagamentoRepository`) com mapeamento imperativo do SQLAlchemy, apostando em **testabilidade rápida** e **independência de banco de dados**.

Na prática, essa previsão se confirmou plenamente nos testes de domínio e serviço: validar regras como bloqueio de check-in duplicado, proibição de estorno após check-in e disparo de múltiplos observadores ocorre em milissegundos, sem necessidade de subir servidor ou banco. Por outro lado, o trade-off que mais pesou foi o **custo de sincronização entre três representações da mesma entidade** (classe de domínio, tabela em `orm.py` e dupla implementação de repositório `Fake` + `SqlAlchemy`), além da necessidade de manter o commit transacional coordenado entre agregados (`Pagamento` e `Inscricao`).

### 2. Evidências da Fase 2: Onde as camadas facilitaram e onde atrapalharam

- **Onde facilitou (refatoração SOLID e implementação do GoF Observer):** Na Fase 2, tanto a refatoração de SRP/DIP nos casos de uso de pagamento (desacoplando `services.py` da `Session` direta e delegando a persistência aos contratos de repositório) quanto a introdução do padrão **Observer** em `Pagamento` (`16835b1`) foram realizadas sem alterar uma linha de `orm.py` ou `flask_app.py`. Como `Pagamento` é uma classe Python pura, adicionar a lista `observadores` e os observadores concretos (`InscricaoSyncObserver`, `AuditoriaPagamentoObserver`, `NotificacaoPagamentoObserver`) exigiu apenas testes unitários em `tests/unit/test_pagamento_observer.py`, preservando todos os testes existentes de persistência (`test_repository_pagamento.py`) e API (`test_flask_pagamento.py`).
- **Onde atrapalhou (ciclo de vida do ORM e fronteira transacional):** O mapeamento imperativo do SQLAlchemy (`map_imperatively`) reconstrói instâncias de `Pagamento` do banco sem executar `__init__`. Isso exige cuidado defensivo no domínio (como verificar `hasattr(self, "observadores")` antes de iterar observadores em objetos recarregados do banco) para evitar falhas em tempo de execução. Além disso, como os observadores em memória não são persistidos pelo ORM, a conexão dos ouvintes (`InscricaoSyncObserver`) precisa ser reconfigurada na camada de serviço a cada caso de uso, enquanto o controle de transação entre `Pagamento` e `Inscricao` ainda depende de `commit()` explícito em vez de uma `Unit of Work` unificada (como apontado no ADR-004).

### 3. Decisão final: Escolheria essa arquitetura de novo?

**Decisão:** Adotaria uma **arquitetura híbrida**, mantendo o núcleo de domínio puro e simplificando a infraestrutura ao redor dele.

**Justificativa:** Para agregados com regras de negócio críticas e múltiplos efeitos colaterais — como o ciclo de vida financeiro de `Pagamento`, a sincronização de status com `Inscricao` e as invariantes de `CheckIn` —, separar o domínio dos frameworks valeu a pena pela clareza das regras, facilidade de aplicar padrões (State e Observer) e rapidez dos testes unitários. Contudo, em uma próxima versão, eu substituiria os `FakeRepository` manuais por testes de integração diretos com SQLite em memória (eliminando código duplicado de consulta) e implementaria logo de início uma **Unit of Work** na camada de serviço para gerenciar transações que envolvem mais de um agregado (`Pagamento` + `Inscricao`) sem depender de `commit()` espalhado nas rotas ou nos repositórios individuais.

---

## Análise — Samuel Carvalho Dias (@SamuelCDiias)

- **Escopo avaliado:** agregado `Inscricao` (`Inscricao`, `FabricaDeInscricao`, `FabricaInscricaoPaga` e `FabricaInscricaoCortesia` em `src/eventos/domain/model.py`), seus repositórios em `src/eventos/adapters/repository.py`, os casos de uso de inscrição em `src/eventos/service_layer/services.py` e as rotas `/inscricoes` em `src/eventos/entrypoints/flask_app.py`. Também revisito a seção **Alternativa** de `docs/arquitetura.md` e o **ADR-004**, ambos de minha autoria (commit `6ead0be`).

### 1. Revisitação do Checkpoint 1 e trade-offs na prática

No Checkpoint 1 eu comparei a arquitetura atual com **Unit of Work + Message Bus** e recomendei adotá-la de forma incremental, começando pela Unit of Work, porque as duas maiores lacunas eram o `session.commit()` nas rotas e a inscrição criada sem consumir vaga do lote. Com a mudança do enunciado, esses módulos deixaram de ser exigidos e a UoW não foi implementada. Mesmo assim, dá para conferir as previsões:

- **Fronteira transacional nas rotas: confirmou-se e foi parcialmente corrigida.** O documento contava 12 chamadas a `session.commit()` em `flask_app.py`. Depois das refatorações DIP de inscrição (`9e5a6d8`, minha) e de pagamento (`d219773`, do Lucas), sobraram 4, todas fora das rotas de inscrição. A correção, porém, foi a versão pequena da minha própria proposta: um `commit()` em cada repositório, e não uma UoW. O custo apareceu em `services.confirmar_inscricao_apos_pagamento`, que só chama `repositorio_inscricao.commit()` e grava a mudança do pagamento por efeito colateral, porque os dois repositórios compartilham a mesma `Session` em `create_app`. A atomicidade entre agregados existe, mas por acaso da composição, não por contrato.
- **Estoque do lote: confirmou-se e não foi resolvido.** A coluna `inscricoes.lote` continua `String(255)`. Isso limitou o meu padrão GoF: a `FabricaInscricaoCortesia` cria a inscrição já confirmada, mas nenhuma das duas fábricas consegue chamar `LoteDeIngresso.venda()`, porque a inscrição não tem um lote de verdade para chamar.
- **Risco de contratos Fake/SQLAlchemy sem teste compartilhado: confirmou-se no meu módulo.** `services.encerrar_evento` chama `repositorio_inscricao.listar_por_evento`, mas esse método não existe em `AbstractInscricaoRepository`, em `FakeInscricaoRepository` nem em `SqlAlchemyInscricaoRepository`. Ele só existe no dublê escrito dentro de `tests/unit/test_services_evento.py`. Os testes de unidade passam, e a rota `POST /eventos/<id>/encerrar` responde `501` (`tests/e2e/test_eventos_api.py`). Foi exatamente o risco descrito na evidência 4 de `docs/arquitetura.md`.
- **Testabilidade: confirmou-se.** A suíte unitária cresceu de 64 para 100 testes e roda em 0,08s; a e2e, com 19 testes, leva 0,33s.

O trade-off que mais pesou na prática foi **testabilidade contra simplicidade na fronteira transacional**: o Fake tornou trivial testar que o caso de uso faz commit (`FakeInscricaoRepository.commitou`), mas cada agregado ganhou o seu próprio `commit()`, e ninguém testa a transação que envolve dois agregados.

### 2. Evidências da Fase 2: onde as camadas facilitaram e onde atrapalharam

- **Facilitaram:**
  1. **Refatoração DIP (`9e5a6d8`):** a mudança tocou só as três camadas envolvidas (`repository.py` +11, `services.py` +3, `flask_app.py` −3) mais o teste novo `tests/unit/test_services_inscricao.py`. Os 6 testes e2e de inscrição que já existiam continuaram passando sem alteração, o que comprovou que o comportamento HTTP não mudou.
  2. **Factory Method (`0885326`):** as fábricas entraram em `model.py` (+18 linhas), e `criar_inscricao` ganhou um parâmetro com valor padrão. Por isso, as chamadas antigas e os testes de `test_services_inscricao.py` não mudaram, e `orm.py` não foi tocado. Os 5 testes de unidade novos rodam sem banco.
- **Atrapalharam:**
  1. **Uma regra pequena atravessa todas as camadas.** "Inscrição de cortesia nasce confirmada" é uma regra de duas linhas, mas exigiu mudar domínio, serviço, rota e dois arquivos de teste: foram 5 arquivos no commit `0885326`, sendo 3 de produção.
  2. **O ORM restringe o domínio.** Como o SQLAlchemy reconstrói `Inscricao` sem chamar `__init__`, nenhuma regra de criação pode morar no construtor. As fábricas ficaram como classes separadas também por esse motivo, e não só por causa do padrão.

### 3. Decisão final: escolheria essa arquitetura de novo?

**Decisão:** sim, **manteria a arquitetura em camadas com domínio puro**, com duas mudanças desde o início: **uma Unit of Work na camada de serviço** e **o lote referenciado por chave estrangeira** em `inscricoes`.

**Justificativa:** no agregado `Inscricao`, as camadas cumpriram o que prometeram. A refatoração SOLID e o padrão GoF entraram sem tocar no esquema do banco e foram validados por testes que rodam em milissegundos. Os problemas que encontrei não vieram de ter camadas demais, e sim de uma camada que faltou: os três problemas da seção 1 (commit por repositório, estoque do lote ignorado e contrato `listar_por_evento` ausente) são todos de **coordenação entre agregados**, que é justamente o papel da Unit of Work proposta no ADR-004. Trocar por Active Record ou Django reduziria o código de mapeamento, mas não resolveria a coordenação, e custaria a velocidade da suíte unitária, que é o atributo de maior prioridade em `docs/arquitetura.md`. Eu não adotaria o Message Bus: com um único processo síncrono e seis agregados, a indireção dos eventos não se pagou nem na Fase 2, quando o requisito foi removido.
