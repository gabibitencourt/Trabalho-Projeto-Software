# Padrão GoF: Strategy

- **Categoria:** comportamental.
- **Agregado:** `LoteDeIngresso`.

## Contexto e problema

O lote mantém o preço-base do ingresso (`preco`), mas regras diferentes podem
ser necessárias para calcular o valor cobrado, como preço integral ou desconto
percentual. Concentrar todas essas variações em condicionais de
`LoteDeIngresso` faria a entidade conhecer cada política e exigiria alterá-la
sempre que uma nova regra fosse adicionada.

O método `LoteDeIngresso.calcular_preco` delega o cálculo a uma estratégia
fornecida pelo chamador. `PrecoIntegral` mantém o preço-base, enquanto
`DescontoPercentual` calcula o valor com desconto. O preço persistido continua
sendo o preço-base; a política é selecionada para cada cálculo.

## Por que Strategy

Strategy permite variar o algoritmo sem acoplar o lote às regras concretas e
sem alterar o comportamento existente de criação, venda ou persistência do
lote. Uma alternativa seria colocar uma condição para cada tipo de promoção
dentro de `LoteDeIngresso`; essa opção parece mais simples inicialmente, mas
faz a entidade acumular regras e crescer a cada nova política. State também
foi considerado, mas não se ajusta ao problema: o cálculo depende de uma
política escolhida, não de uma transição do ciclo de vida do lote.

## Participantes

| Papel no padrão | Classe/método no sistema |
|---|---|
| Contexto | `LoteDeIngresso`, que mantém o preço-base e delega em `calcular_preco` |
| Strategy | `EstrategiaPreco`, contrato abstrato com `calcular` |
| Concrete Strategy | `PrecoIntegral`, que retorna o preço-base |
| Concrete Strategy | `DescontoPercentual`, que aplica o percentual validado |
| Cliente | Chamador de `LoteDeIngresso.calcular_preco`, que escolhe a estratégia |

## Diagrama de classes

```mermaid
classDiagram
    class LoteDeIngresso {
        +preco
        +calcular_preco(estrategia)
    }
    class EstrategiaPreco {
        <<abstract>>
        +calcular(preco_base)
    }
    class PrecoIntegral {
        +calcular(preco_base)
    }
    class DescontoPercentual {
        +percentual
        +calcular(preco_base)
    }
    class Cliente {
        +escolher estrategia
    }

    Cliente ..> LoteDeIngresso : solicita cálculo
    Cliente ..> EstrategiaPreco : escolhe
    LoteDeIngresso ..> EstrategiaPreco : delega
    EstrategiaPreco <|.. PrecoIntegral
    EstrategiaPreco <|.. DescontoPercentual
```

## Teste

`tests/unit/test_ingresso.py::teste_lote_calcula_preco_com_estrategias_diferentes`
exercita as duas estratégias no mesmo lote: preço integral e desconto de 25%.
`teste_desconto_percentual_invalido` também verifica a validação do intervalo
permitido para o desconto.

## Custo da aplicação

Nesta implementação, o custo inicial foi criar uma
interface (`EstrategiaPreco`), duas implementações (`PrecoIntegral` e
`DescontoPercentual`) e o método de delegação em `LoteDeIngresso`, além dos
testes. Cada nova política de preço exige outra classe de estratégia e testes próprios. 
O chamador também precisa escolher e fornecer a estratégia quando calcula o preço.

Entretanto, há mais arquivos conceituais e indireção do que com um
cálculo simples ou uma condição dentro do lote. Para apenas duas regras
estáveis, essa estrutura pode ser desnecessária; seu benefício aparece quando
as políticas variam ou novas regras são adicionadas com frequência. Nesse caso,
a regra nova fica isolada e não aumenta os condicionais nem altera
`LoteDeIngresso`. As estratégias não precisam ser persistidas, então não há
custo de migração do esquema do banco de dados.


# Padrão GoF: Decorator

- **Categoria:** Estrutural
- **Agregado:** `Inscrição` (`Participante`)
- **Autora:** Gabriela Bitencourt Freire da Silva (@gabibitencourt)

## Contexto e problema

O sistema precisava conceder benefícios e tratamentos diferenciados (como descontos no valor do ingresso e identificação em credenciais/crachás) para categorias especiais de participantes (ex: VIP, Meia-Entrada / Estudante).

Adicionar múltiplos campos booleanos (`is_vip`, `is_estudante`) na classe `Participante` violaria o Princípio da Responsabilidade Única (SRP) e inflaria a entidade. Por outro lado, criar subclasses estáticas para cada combinação possível geraria uma explosão de classes (`ParticipanteVIPEstudante`, `ParticipanteVIP`, etc.).

## Por que Decorator

O padrão **Decorator** permite adicionar responsabilidades e comportamentos adicionais a um objeto individual dinamicamente em tempo de execução, sem afetar outros objetos da mesma classe e sem modificar o código-fonte da entidade `Participante`.

Como alternativa, considerei a Herança Múltipla ou Subclasses Estáticas. No entanto, essa abordagem acoplaria as regras em tempo de compilação e tornaria inviável a combinação dinâmica e flexível de múltiplos privilégios sobre um mesmo participante.

## Participantes

| Papel no padrão | Classe/método no sistema |
|---|---|
| Component (Interface) | `AbstractParticipante`, contrato abstrato com as propriedades e métodos `obter_desconto_ingresso` e `obter_tipo_credencial` |
| Concrete Component | `Participante`, entidade base que retorna o valor integral (0% desconto) e credencial "PADRÃO" |
| Decorator Base | `ParticipanteDecorator`, classe base abstrata que envolve uma instância de `AbstractParticipante` e delega as chamadas |
| Concrete Decorator | `ParticipanteVIPDecorator`, estende a credencial com acesso ao Lounge e garante 20% de desconto |
| Concrete Decorator | `ParticipanteEstudanteDecorator`, valida a matrícula do estudante, estende a credencial e garante 50% de desconto (meia-entrada) |

## Diagrama de classes

```mermaid
classDiagram
    class AbstractParticipante {
        <<interface>>
        +nome: str
        +email: str
        +documento: str
        +obter_desconto_ingresso() float*
        +obter_tipo_credencial() str*
    }
    class Participante {
        +identificador: int
        +nome: str
        +email: str
        +documento: str
        +obter_desconto_ingresso() float
        +obter_tipo_credencial() str
    }
    class ParticipanteDecorator {
        -_participante: AbstractParticipante
        +obter_desconto_ingresso() float
        +obter_tipo_credencial() str
    }
    class ParticipanteVIPDecorator {
        +obter_desconto_ingresso() float
        +obter_tipo_credencial() str
    }
    class ParticipanteEstudanteDecorator {
        +matricula_estudante: str
        +obter_desconto_ingresso() float
        +obter_tipo_credencial() str
    }

    AbstractParticipante <|.. Participante
    AbstractParticipante <|.. ParticipanteDecorator
    ParticipanteDecorator o-- AbstractParticipante : envolve
    ParticipanteDecorator <|-- ParticipanteVIPDecorator
    ParticipanteDecorator <|-- ParticipanteEstudanteDecorator
```

## Teste

Os testes unitários em `tests/unit/test_participante.py` exercitam:

`test_gof_decorator_participante_padrao_sem_desconto`: comportamento baseline.

`test_gof_decorator_participante_vip`: benefícios isolados de VIP.

`test_gof_decorator_participante_estudante_meia_entrada`: validação de matrícula e meia-entrada.

`test_gof_decorator_combina_vip_e_estudante`: empilhamento dinâmico de múltiplos decorators sobre a mesma instância.

## Custo da aplicação
O custo principal foi a introdução da interface abstrata `AbstractParticipante`, da classe base `ParticipanteDecorator` e das subclasses de decoradores concretos, além de pequenas indireções no acesso aos atributos.

Em contrapartida, o benefício é a capacidade de combinar privilégios livremente em tempo de execução sem alterar o modelo de dados nem modificar o schema do banco relacional.


# Padrão GoF: State

- **Categoria:** Comportamental
- **Agregado:** `Pagamento`
- **Autor:** Lucas Paixao de Lima Costa (@LucasLimmm2000)

## Contexto e problema

O `Pagamento` tem quatro status (`PENDENTE`, `APROVADO`, `RECUSADO`, `ESTORNADO`) e três transições (`aprovar`, `recusar`, `estornar`), cada uma válida só a partir de alguns status. Antes desta refatoração, os três métodos viviam na própria classe `Pagamento` e cada um checava o status atual com `if`/comparação de enum antes de decidir se a transição era permitida (ver ADR-005, que já documentava essa decisão na Fase 1).

Isso funciona, mas concentra em `Pagamento` o conhecimento de todas as combinações válidas entre status e transição. A cada novo status ou nova transição, os três métodos (ou mais) precisariam ser revisados, e a regra "o que pode acontecer a partir do status X" fica espalhada em vários `if`s em vez de estar num lugar só.

## Por que State

O padrão **State** resolve isso movendo o comportamento de cada transição para uma classe por status: `_EstadoPendente`, `_EstadoAprovado`, `_EstadoRecusado` e `_EstadoEstornado` implementam `aprovar`, `recusar` e `estornar` cada uma à sua maneira — permitindo a transição e trocando o status, ou levantando `OperacaoInvalidaError`. O agregado `Pagamento` não guarda mais a regra: ele resolve o estado atual a partir do `status` persistido e delega a chamada.

Considerei manter as condicionais como estavam (mais simples para só 4 status), mas o GoF State decompõe exatamente esse tipo de máquina de estados finita, e o agregado Pagamento é o que no sistema modela o ciclo de vida mais explícito via enum. Como alternativa, cheguei a pensar num campo de status "livre" (string) com uma tabela de transições, mas isso é o que o próprio ADR-005 já rejeitou — o enum fechado (`StatusPagamento`) continua sendo a fonte da verdade, e o State só organiza o comportamento associado a cada valor dele.

**Decisão de projeto importante:** o `_estado` **não é guardado como atributo no `__init__`** — é uma `@property` que consulta um dicionário `_ESTADOS_POR_STATUS` a partir de `self.status` a cada chamada. Isso é necessário porque o `SqlAlchemyPagamentoRepository` usa mapeamento imperativo (`map_imperatively`): ao recarregar um `Pagamento` do banco, o SQLAlchemy reconstrói o objeto e popula `status` direto, **sem passar pelo `__init__`**. Um `_estado` calculado só na construção ficaria desatualizado nesse cenário (o mesmo cuidado que o Arthur já registrou na refatoração OCP do `Evento`, em `docs/solid.md`).

## Participantes

| Papel no padrão | Classe/método no sistema |
|---|---|
| Contexto | `Pagamento`, que mantém `status` e delega `aprovar`/`recusar`/`estornar` via a property `_estado` |
| State | `EstadoPagamento`, contrato abstrato com `aprovar`, `recusar` e `estornar` |
| Concrete State | `_EstadoPendente` — permite aprovar e recusar; bloqueia estornar |
| Concrete State | `_EstadoAprovado` — permite estornar (se não houve check-in); bloqueia aprovar e recusar |
| Concrete State | `_EstadoRecusado` — bloqueia as três transições |
| Concrete State | `_EstadoEstornado` — bloqueia as três transições |

## Diagrama de classes

```mermaid
classDiagram
    class Pagamento {
        +status: StatusPagamento
        +aprovar()
        +recusar()
        +estornar()
    }
    class EstadoPagamento {
        <<abstract>>
        +aprovar(pagamento)
        +recusar(pagamento)
        +estornar(pagamento)
    }
    class _EstadoPendente {
        +aprovar(pagamento)
        +recusar(pagamento)
        +estornar(pagamento)
    }
    class _EstadoAprovado {
        +aprovar(pagamento)
        +recusar(pagamento)
        +estornar(pagamento)
    }
    class _EstadoRecusado {
        +aprovar(pagamento)
        +recusar(pagamento)
        +estornar(pagamento)
    }
    class _EstadoEstornado {
        +aprovar(pagamento)
        +recusar(pagamento)
        +estornar(pagamento)
    }

    Pagamento ..> EstadoPagamento : resolve via status
    EstadoPagamento <|.. _EstadoPendente
    EstadoPagamento <|.. _EstadoAprovado
    EstadoPagamento <|.. _EstadoRecusado
    EstadoPagamento <|.. _EstadoEstornado
```

## Teste

- `tests/unit/test_pagamento.py` — já existia e continuou passando sem alteração; cobre as transições válidas e inválidas pela interface pública de `Pagamento`, provando que o comportamento não mudou.
- `tests/unit/test_pagamento_estado.py` (novo) — testa o padrão diretamente: `test_pagamento_*_resolve_estado_*` confirma que cada status resolve para a classe de estado correta; `test_estado_e_reavaliado_apos_transicao` prova que o estado não fica em cache depois de uma transição; `test_estado_recusado_nao_permite_aprovar_nem_estornar` cobre um estado "terminal".
- `tests/integration/test_repository_pagamento.py::test_pagamento_recarregado_do_banco_resolve_estado_pelo_status_persistido` (novo) — recarrega um `Pagamento` do SQLite via `session.expire_all()` (contornando a identity map, sem passar pelo `__init__`) e confirma que `_estado` ainda resolve corretamente a partir do `status` persistido.

## Custo da aplicação

- **Custo:** quatro classes de estado concreto além da interface abstrata, mais a property `_estado` que faz o lookup no dicionário `_ESTADOS_POR_STATUS`. Para 4 status e 3 transições, isso é mais código do que os `if`s originais.
- **Por que compensa:** a regra "o que pode acontecer a partir do status X" fica inteira em uma única classe, em vez de espalhada nos três métodos de `Pagamento`. Adicionar um novo status no futuro significa criar uma nova classe de estado, sem editar as transições dos estados existentes. A interface pública de `Pagamento` (`aprovar`/`recusar`/`estornar`/`status`) não mudou, então `services.py`, `flask_app.py` e todos os testes existentes continuaram funcionando sem alteração — só o `tests/unit/test_pagamento_estado.py` e o novo teste de integração foram acrescentados.

# Padrão GoF: Observer

- **Categoria:** Comportamental
- **Agregado:** `Pagamento`
- **Autor:** João Marcello (@JoaoMarcelloCosta2000)

## Contexto e problema

Quando um `Pagamento` tem seu ciclo de vida alterado (como aprovação, recusa ou estorno), múltiplos subsistemas e entidades precisam reagir a esse evento financeiro:
- A `Inscricao` correspondente deve ser confirmada automaticamente assim que o pagamento for aprovado;
- O participante precisa receber uma notificação ou recibo da transação por e-mail;
- O livro-razão / auditoria contábil precisa registrar cada transição para fins de conciliação.

Fazer com que a classe `Pagamento` invoque diretamente esses serviços ou agregados externos violaria o Princípio da Responsabilidade Única (SRP) e geraria alto acoplamento entre o domínio financeiro e infraestruturas secundárias.

## Por que Observer

O padrão **Observer** estabelece uma dependência um-para-muitos entre objetos, de forma que quando o sujeito (`Pagamento`) muda de estado, todos os seus observadores registrados são notificados e atualizados automaticamente.

Como alternativas, considerou-se chamadas diretas no método da entidade (acoplamento excessivo) e orquestração procedural na camada de serviços (enfraquecimento do modelo de domínio com regras de negócio dispersas).

## Participantes

| Papel no padrão | Classe/método no sistema |
|---|---|
| Subject | `Pagamento`, gerencia a inscrição de interessados (`adicionar_observador`, `remover_observador`) e notifica a lista via `notificar` |
| Observer (Interface) | `ObservadorPagamento`, contrato abstrato com o método `atualizar(pagamento, evento)` |
| Concrete Observer | `InscricaoSyncObserver`, confirma a inscrição automaticamente após aprovação |
| Concrete Observer | `AuditoriaPagamentoObserver`, mantém o registro histórico para conciliação contábil |
| Concrete Observer | `NotificacaoPagamentoObserver`, simula o envio de recibo ao e-mail do participante |

## Diagrama de classes

```mermaid
classDiagram
    class Pagamento {
        +identificador: int
        +valor: float
        +status: StatusPagamento
        +observadores: list
        +adicionar_observador(observador)
        +remover_observador(observador)
        +notificar(evento)
        +aprovar()
        +recusar()
        +estornar()
    }

    class ObservadorPagamento {
        <<interface>>
        +atualizar(pagamento: Pagamento, evento: str)*
    }

    class InscricaoSyncObserver {
        +atualizar(pagamento: Pagamento, evento: str)
    }

    class AuditoriaPagamentoObserver {
        +historico: list
        +atualizar(pagamento: Pagamento, evento: str)
    }

    class NotificacaoPagamentoObserver {
        +notificacoes_enviadas: list
        +atualizar(pagamento: Pagamento, evento: str)
    }

    Pagamento o-- ObservadorPagamento : notifica
    ObservadorPagamento <|.. InscricaoSyncObserver
    ObservadorPagamento <|.. AuditoriaPagamentoObserver
    ObservadorPagamento <|.. NotificacaoPagamentoObserver
```

## Teste

Os testes unitários em `tests/unit/test_pagamento_observer.py` exercitam:
- `test_gof_observer_sincroniza_confirmacao_de_inscricao_ao_aprovar`: comprova a reação e confirmação automática da inscrição acoplada ao evento financeiro.
- `test_gof_observer_auditoria_e_notificacao_registram_multiplos_eventos`: testa múltiplos observadores conectados ao mesmo sujeito recebendo aprovação e estorno.
- `test_gof_observer_remover_observador_impede_notificacao`: valida a desinscrição dinâmica de observadores.

## Custo da aplicação

O custo do padrão foi a introdução da interface `ObservadorPagamento`, das classes concretas de observação e do gerenciador de ouvintes dentro de `Pagamento`. Em contrapartida, desacoplou-se completamente o processamento financeiro das regras de notificação, auditoria e sincronização entre agregados.
    
# Padrão GoF: Factory Method

- **Categoria:** Criacional
- **Agregado:** `Inscricao`
- **Autor:** Samuel Carvalho Dias (@SamuelCDiias)

## Contexto e problema

Toda `Inscricao` nascia `PENDENTE`, aguardando pagamento. Inscrições de cortesia (palestrantes, convidados, equipe) não passam por pagamento e precisam nascer `CONFIRMADA`, prontas para o check-in. Sem um ponto de criação, `services.criar_inscricao` teria que conhecer cada tipo de inscrição e montar cada uma com condicionais, e cada novo tipo exigiria editar o caso de uso.

## Por que Factory Method

O **Factory Method** tira a decisão de "como nasce a inscrição" do caso de uso. `services.criar_inscricao` recebe uma `FabricaDeInscricao` e chama `criar`; cada fábrica concreta decide o estado inicial. A rota `POST /inscricoes` escolhe a fábrica pelo campo `cortesia` da requisição, e o padrão continua sendo a inscrição paga.

Alternativas consideradas:
- **Parâmetro `cortesia` no construtor de `Inscricao`:** mais simples, mas mistura regras de cada tipo no agregado e faz o `__init__` crescer a cada novo tipo.
- **Subclasse `InscricaoCortesia`:** exigiria mapeamento polimórfico no SQLAlchemy (coluna discriminadora e migração do esquema) só para mudar o estado inicial.

## Participantes

| Papel no padrão | Classe/método no sistema |
|---|---|
| Creator | `FabricaDeInscricao`, com o factory method abstrato `criar` |
| Concrete Creator | `FabricaInscricaoPaga`, que cria a inscrição `PENDENTE` |
| Concrete Creator | `FabricaInscricaoCortesia`, que cria a inscrição já `CONFIRMADA` |
| Product | `Inscricao` |
| Cliente | `services.criar_inscricao`, que recebe a fábrica (padrão: `FabricaInscricaoPaga`) |

## Diagrama de classes

```mermaid
classDiagram
    class FabricaDeInscricao {
        <<abstract>>
        +criar(identificador, participante, lote) Inscricao
    }
    class FabricaInscricaoPaga {
        +criar(identificador, participante, lote) Inscricao
    }
    class FabricaInscricaoCortesia {
        +criar(identificador, participante, lote) Inscricao
    }
    class Inscricao {
        +status: StatusInscricao
        +confirmar()
    }
    class criar_inscricao {
        <<service>>
    }

    FabricaDeInscricao <|-- FabricaInscricaoPaga
    FabricaDeInscricao <|-- FabricaInscricaoCortesia
    FabricaDeInscricao ..> Inscricao : cria
    criar_inscricao ..> FabricaDeInscricao : usa
```

## Teste

- `tests/unit/test_inscricao_factory.py`: `test_fabrica_paga_cria_inscricao_pendente`, `test_fabrica_cortesia_cria_inscricao_confirmada`, `test_inscricao_cortesia_permite_checkin_sem_pagamento`, `test_servico_usa_fabrica_paga_por_padrao` e `test_servico_cria_inscricao_com_a_fabrica_recebida`.
- `tests/e2e/test_inscricoes_api.py::test_cria_inscricao_cortesia_ja_confirmada`: cria uma inscrição de cortesia pela API.
- Os testes existentes de inscrição continuaram passando sem alteração.

## Custo da aplicação

- **Custo:** uma classe abstrata e duas fábricas concretas para dois tipos de inscrição, mais um parâmetro em `criar_inscricao`. Com só dois tipos, é mais indireção do que um `if` no serviço.
- **Benefício:** um novo tipo de inscrição entra como uma nova fábrica, sem editar `Inscricao` nem o caso de uso. Como o produto continua sendo `Inscricao`, não há mudança no mapeamento ORM nem no esquema do banco, e a chamada existente de `criar_inscricao` continua funcionando pelo valor padrão.


# Padrão GoF: Memento

- **Categoria:** Comportamental
- **Agregado:** `Evento`
- **Autor:** Arthur Siqueira Campos Alexandrino (@devalexandrino)

## Contexto e problema

Durante o planejamento e a operação de um `Evento`, o organizador realiza sucessivas edições na configuração do evento e no seu catálogo de lotes (`adicionar_lote`, `alterar_lote`, mudança de nome/local e transição de início com `iniciar()`). Na prática, é comum que um organizador configure novos lotes promocionais, reajuste capacidades/preços em lote ou inicie o evento por engano e precise desfazer a operação, restaurando o agregado para o último ponto de configuração válido.

No entanto, a raiz do agregado `Evento` encapsula estritamente sua coleção interna `self._lotes`, expondo a propriedade `evento.lotes` apenas como uma `tuple` somente-leitura (sem *setter*). Sem um mecanismo próprio de captura e restauração, qualquer tentativa externa de salvar e reverter o estado de `Evento` violaria o encapsulamento ao manipular diretamente `evento._lotes`. Além disso, guardar apenas referências para as instâncias de `LoteDeIngresso` não protegeria o estado salvo contra mutações internas nos próprios lotes (como a atualização de `quant_vendida` via `lote.venda()`).

## Por que Memento

O padrão **Memento** permite capturar e externalizar um instantâneo completo do estado interno de `Evento` (`EventoMemento`) sem violar o seu encapsulamento, permitindo que o agregado seja restaurado posteriormente a esse estado com garantia de integridade das invariantes de negócio (como bloquear a reversão de um evento que já foi `ENCERRADO` ou rejeitar um instantâneo pertencente a outro `identificador` de evento).

Alternativas consideradas:
- **Expor um *setter* `evento.lotes = ...` ou manipular `evento._lotes` externamente:** descartada porque quebraria o encapsulamento da raiz do agregado (verificado inclusive pelo teste existente `test_evento_adiciona_lote_sem_expor_lista_mutavel`), permitindo que código cliente contornasse as regras `RegraAlteracaoLote` e `_CicloDeVidaEvento`.
- **Clonagem externa com `copy.deepcopy(evento)`:** descartada porque transfere para o chamador a responsabilidade de substituir a referência da instância inteira de `Evento` (o que conflita com o controle de identidade da sessão do SQLAlchemy) e não centraliza no domínio as validações de segurança no momento da restauração (por exemplo, impedir que um evento já `ENCERRADO` volte a `PLANEJADO`).

## Participantes

| Papel no padrão | Classe/método no sistema |
|---|---|
| Originator | `Evento`, que gera o instantâneo em `criar_memento()` e restaura seu estado interno em `restaurar(memento)` |
| Memento | `EventoMemento` (auxiliado por `_InstantaneoLote`), `dataclass(frozen=True)` imutável que armazena o estado de `Evento` e a cópia de valor dos seus lotes |
| Caretaker | `HistoricoEvento`, que gerencia a pilha de instantâneos (`salvar(evento)` e `desfazer(evento)`) sem inspecionar ou alterar o conteúdo interno do memento |

## Diagrama de classes

```mermaid
classDiagram
    class Evento {
        +identificador: int
        +nome: str
        +data: date
        +local: str
        +status: StatusEvento
        -_lotes: list~LoteDeIngresso~
        -_regras_alteracao_lote: tuple~RegraAlteracaoLote~
        +adicionar_lote(lote)
        +alterar_lote(identificador_lote, lote_atualizado)
        +iniciar()
        +encerrar(inscricoes_pendentes)
        +criar_memento() EventoMemento
        +restaurar(memento: EventoMemento) None
    }

    class EventoMemento {
        <<frozen dataclass>>
        +identificador: int
        +nome: str
        +data: date
        +local: str
        +status: StatusEvento
        -_lotes: tuple~_InstantaneoLote~
        -_regras_alteracao_lote: tuple~RegraAlteracaoLote~
    }

    class _InstantaneoLote {
        <<frozen dataclass>>
        +identificador: int
        +nome: str
        +preco: float
        +quant_total: int
        +quant_vendida: int
        +de_lote(lote) _InstantaneoLote$
        +reconstruir() LoteDeIngresso
    }

    class HistoricoEvento {
        -_historico: list~EventoMemento~
        +quantidade_estados: int
        +salvar(evento: Evento) EventoMemento
        +desfazer(evento: Evento) EventoMemento
    }

    HistoricoEvento o-- EventoMemento : armazena pilha
    HistoricoEvento ..> Evento : solicita salvar/desfazer
    Evento ..> EventoMemento : cria e restaura
    EventoMemento *-- _InstantaneoLote : compõe cópia dos lotes
```

## Teste

Os testes unitários em `tests/unit/test_evento.py` exercitam diretamente o padrão:
- `test_gof_memento_restaura_catalogo_de_lotes_e_dados_do_evento`: salva o estado de um `Evento` planejado no `HistoricoEvento`, realiza alterações de nome, modificação de lote existente, adição de novo lote e início do evento, e comprova que `historico.desfazer(evento)` restaura integralmente o estado anterior.
- `test_gof_memento_isola_instantaneo_contra_mutacoes_internas_no_lote`: comprova que a cópia profunda em `_InstantaneoLote` protege o memento mesmo quando o objeto `LoteDeIngresso` sofre mutação interna (`lote.venda()`) após o salvamento.
- `test_gof_memento_bloqueia_restauracao_em_evento_encerrado_ou_id_divergente`: verifica as invariantes de domínio no `Originator` (impedir restauração de memento de outro evento ou reversão de um evento já `ENCERRADO`, preservando a pilha do histórico).
- `test_gof_memento_historico_vazio_rejeita_desfazer`: garante que `HistoricoEvento.desfazer` sinaliza `OperacaoInvalidaError` quando não há estados salvos.

## Custo da aplicação

- **Custo:** criação de três novas estruturas (`_InstantaneoLote`, `EventoMemento` e `HistoricoEvento`) e dois métodos em `Evento` (`criar_memento` e `restaurar`), além do consumo adicional de memória proporcional ao número de instantâneos empilhados em `HistoricoEvento` e à quantidade de lotes copiados por instantâneo.
- **Por que compensa:** permite desfazer configurações de lotes e alterações de estado em `Evento` mantendo `self._lotes` totalmente encapsulado, protege o histórico contra mutações por referência nos objetos `LoteDeIngresso` e preserva total compatibilidade com o mapeamento imperativo do SQLAlchemy (`map_imperatively`), já que a restauração atualiza a lista `_lotes` *in-place* (`self._lotes[:] = ...`) sem substituir a coleção instrumentada pelo ORM nem alterar o esquema do banco.
