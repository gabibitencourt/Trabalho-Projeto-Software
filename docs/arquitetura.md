## Escopo

O sistema é uma plataforma para gestão completa de eventos, englobando a criação e organização de eventos, controle de estoque de lotes de ingressos, inscrições de participantes, processamento de pagamentos e verificação de check-in no dia do evento. Ele atende a dois perfis principais de usuários:

1. **Organizadores:** responsáveis pela criação e gestão dos eventos e pela definição dos lotes de ingressos (preços e quantidades).
2. **Participantes:** usuários que se inscrevem em lotes disponíveis, realizam o pagamento e efetuam o check-in na entrada do evento.

A arquitetura do sistema foi projetada para garantir a integridade das regras de negócio (como limitação de vagas por lote, validação cadastral de participantes e bloqueio de check-in para inscrições pendentes), assegurando que as invariantes de domínio permaneçam isoladas dos detalhes de infraestrutura (banco de dados SQLite e API HTTP em Flask).

# Arquitetura do sistema

## Requisitos arquiteturais

### Objetivos da arquitetura

A arquitetura foi estruturada com três objetivos centrais para o domínio de gestão de eventos, lotes de ingressos, inscrições, pagamentos e check-in:

1. **Isolar as regras e invariantes de negócio da infraestrutura:** garantir que as entidades dos três agregados (`Evento`, `Inscricao` e `Pagamento`) protejam suas próprias transições de estado e validações sem depender de banco de dados relacional ou de transporte HTTP.
2. **Viabilizar testes rápidos e determinísticos em múltiplos níveis:** permitir que regras de domínio e fluxos da camada de serviço sejam verificados em memória por meio de repositórios *Fake* (`FakeEventoRepository`, `FakeInscricaoRepository`, `FakePagamentoRepository`), reservando o uso de SQLAlchemy/SQLite e do cliente HTTP Flask para os testes de integração e ponta a ponta (E2E).
3. **Permitir evolução paralela por agregado:** organizar o código em camadas com fronteiras definidas (`domain/`, `service_layer/`, `adapters/` e `entrypoints/`) para que seis integrantes possam trabalhar simultaneamente nos agregados de `Evento`/`LoteDeIngresso`, `Inscricao`/`Participante`/`Organizador` e `Pagamento`/`CheckIn` reduzindo conflitos de integração.

### Restrições

- **Stack tecnológica obrigatória:** uso de Python 3 (3.10 na pipeline de CI), Flask para exposição da API REST, SQLAlchemy para persistência relacional e `pytest` para automação de testes, conforme definido pelas regras da disciplina.
- **Estrutura de diretórios padronizada:** organização do pacote em `src/eventos/` seguindo o Apêndice B do livro-texto (*Architecture Patterns with Python*), separando explicitamente `domain/`, `service_layer/`, `adapters/` e `entrypoints/`.
- **Mapeamento ORM não intrusivo:** adoção de mapeamento imperativo (clássico) via `mapper_registry.map_imperatively` em `src/eventos/adapters/orm.py`, de modo que as classes de `model.py` não herdem de classes base do SQLAlchemy.
- **Execução e verificação contínua em ambiente autossuficiente:** toda a suíte (`unit`, `integration` e `e2e`) deve executar no GitHub Actions sem serviços externos de infraestrutura, utilizando SQLite em memória (`sqlite:///:memory:`).
- **Divisão organizacional do grupo:** seis integrantes distribuídos entre três agregados, com exigência de rastreabilidade de autoria por commits e manutenção da CI verde a cada entrega.

### Atributos de qualidade e cenários (em ordem de prioridade)

#### 1. Testabilidade (Prioridade Alta)

A capacidade de exercitar regras de negócio e orquestrações de casos de uso de forma isolada, rápida e sem infraestrutura externa foi o principal motivador para a combinação de modelo de domínio rico, *Service Layer* e *Fake Repositories*.

| Elemento do cenário | Descrição |
|---|---|
| **Fonte** | Desenvolvedor do grupo ou pipeline de Integração Contínua (GitHub Actions). |
| **Estímulo** | Execução da suíte de testes unitários após criação ou alteração de regras de negócio no domínio ou na camada de serviço (ex.: bloqueio de encerramento de evento com inscrições pendentes ou confirmação de inscrição pós-pagamento). |
| **Ambiente** | Ambiente de desenvolvimento local ou runner de CI (`ubuntu-latest`), sem servidor HTTP ativo e sem instância de banco de dados inicializada. |
| **Artefato** | Modelo de domínio (`src/eventos/domain/model.py`) e camada de serviço (`src/eventos/service_layer/services.py`) operando sobre implementações em memória (`FakeEventoRepository`, `FakeInscricaoRepository`, `FakePagamentoRepository`). |
| **Resposta** | Os testes validam as invariantes das entidades e os fluxos de serviço inteiramente em memória, sem inicializar `create_app()` do Flask nem abrir sessões do SQLAlchemy. |
| **Medida da resposta** | 100% dos testes em `tests/unit/` executam sem I/O de rede ou banco de dados em tempo total inferior a 1 segundo, cobrindo tanto o caminho feliz quanto o lançamento de `OperacaoInvalidaError`, `ValueError` e exceções de não encontrado. |

#### 2. Integridade e Consistência das Regras de Negócio — Confiabilidade (Prioridade Média-Alta)

Como o domínio envolve controle de estoque de lotes, transições de status financeiros (`Pagamento`) e controle de acesso (`CheckIn`), o sistema precisa impedir que operações fora de ordem ou inválidas corrompam o estado dos agregados.

| Elemento do cenário | Descrição |
|---|---|
| **Fonte** | Cliente HTTP (participante ou organizador) via API Flask ou chamada direta a uma função de `services.py`. |
| **Estímulo** | Tentativa de executar uma transição ou operação inválida (ex.: encerrar `Evento` com inscrições `PENDENTE`, realizar check-in duplicado ou em inscrição não `CONFIRMADA`, vender ingresso além de `quant_total` do lote, ou estornar pagamento de inscrição que já realizou check-in). |
| **Ambiente** | Execução normal da aplicação com persistência SQLAlchemy sobre SQLite. |
| **Artefato** | Entidades de domínio (`Evento`, `LoteDeIngresso`, `Inscricao`, `Pagamento`, `Participante`, `Organizador`), serviços (`src/eventos/service_layer/services.py`) e tratadores de erro HTTP (`src/eventos/entrypoints/flask_app.py`). |
| **Resposta** | A operação é interrompida antes da confirmação da transação (`session.commit()`) por meio do lançamento de `OperacaoInvalidaError` ou `ValueError`, preservando o estado anterior das entidades e retornando erro estruturado em JSON. |
| **Medida da resposta** | Nenhuma (0) transição inválida é persistida no banco e 100% das requisições que violam invariantes de negócio retornam status HTTP `400 Bad Request` (ou `404 Not Found` quando a entidade referenciada não existe), conforme verificado nos testes de `tests/e2e/`. |

#### 3. Modificabilidade e Manutenibilidade (Prioridade Média)

A separação entre domínio, serviço, adaptadores de persistência e entrada HTTP busca isolar o impacto de mudanças para que evoluções nas regras de negócio não exijam reescrita da camada de persistência ou das rotas, e vice-versa.

| Elemento do cenário | Descrição |
|---|---|
| **Fonte** | Integrante do grupo responsável pela manutenção ou evolução de um agregado. |
| **Estímulo** | Alteração de uma regra de validação ou transição de estado no domínio (ex.: alterar critério de validação de documento em `Participante` ou regra de alteração de lote em `Evento`) ou substituição do adaptador de persistência de `Fake` para `SqlAlchemy`. |
| **Ambiente** | Tempo de desenvolvimento e refatoração do código-fonte no repositório. |
| **Artefato** | Camada de domínio (`src/eventos/domain/model.py`), camada de serviço (`src/eventos/service_layer/services.py`) e camada de adaptadores (`src/eventos/adapters/orm.py` e `repository.py`). |
| **Resposta** | Mudanças puras em invariantes de negócio permanecem localizadas no módulo de domínio (e nos respectivos testes), enquanto os serviços consomem qualquer implementação de repositório que respeite o contrato abstrato (`Abstract*Repository`). |
| **Medida da resposta** | Zero (0) importações de `flask` ou `sqlalchemy` nos módulos `src/eventos/domain/model.py` e `src/eventos/service_layer/services.py`, e alterações em regras internas de uma entidade afetam apenas a camada `domain/` sem exigir modificações em `orm.py` ou `repository.py`. |

## Visão geral

O sistema é uma aplicação Python organizada em camadas, com separação inspirada em **Ports & Adapters (Arquitetura Hexagonal)**. O domínio concentra entidades e regras de negócio; a camada de serviço coordena casos de uso; adapters implementam persistência; e o entrypoint Flask expõe a API HTTP. A separação é parcial: a API instancia adapters concretos e controla transações, portanto a infraestrutura ainda atravessa a fronteira de entrada.

```mermaid
flowchart TD
    Cliente[Cliente HTTP]
    subgraph Entry["Entry points - src/eventos/entrypoints/"]
        Flask[Flask API<br/>rotas, validação de entrada e serialização]
    end
    subgraph Service["Service Layer - src/eventos/service_layer/"]
        UseCases[Casos de uso<br/>orquestração]
    end
    subgraph Domain["Domínio - src/eventos/domain/"]
        Model[Modelo de domínio<br/>Evento, Lote, Inscrição, Pagamento, Participante]
    end
    subgraph Adapters["Adapters - src/eventos/adapters/"]
        Repositories[Contratos e implementações<br/>Fake e SQLAlchemy]
        Mapper[Data Mapper imperativo<br/>mapeamentos e metadados]
    end
    Frameworks[Flask / SQLAlchemy]
    Database[(SQLite nos padrões atuais)]

    Cliente --> Flask
    Flask --> UseCases
    Flask --> Model
    Flask --> Repositories
    UseCases --> Model
    Repositories --> Model
    Mapper --> Model
    Flask --> Frameworks
    Repositories --> Frameworks
    Mapper --> Frameworks
    Frameworks --> Database
```

As setas indicam dependência/uso: o consumidor aponta para o componente de que depende. O banco SQLite em memória é criado por `create_app()` quando nenhuma sessão é fornecida; os testes também usam SQLite em memória. O diagrama representa a implementação atual, não uma arquitetura alvo.

## Componentes e responsabilidades

| Componente | Mapeamento | Responsabilidade e evidências |
|---|---|---|
| Entry point HTTP | `src/eventos/entrypoints/` | `flask_app.py` define rotas, converte JSON, serializa entidades, mapeia erros HTTP, cria os repositórios SQLAlchemy e chama `session.commit()`. |
| Camada de aplicação | `src/eventos/service_layer/` | `services.py` implementa casos de uso como criar/encerrar evento, confirmar inscrição e registrar/aprovar pagamento. Coordena repositórios e operações do domínio. |
| Modelo de domínio | `src/eventos/domain/` | `model.py` define entidades, enums e invariantes: transições de estado de Evento, Inscrição e Pagamento, validação de Participante e controle de estoque no Lote. |
| Adapters e persistência | `src/eventos/adapters/` | `repository.py` contém contratos abstratos e implementações Fake e SQLAlchemy. `orm.py` define tabelas e mapeia imperativamente as classes de domínio com SQLAlchemy. |
| Testes | `tests/unit/`, `tests/integration/`, `tests/e2e/` | Testam regras de domínio, repositórios com SQLite e a API via cliente Flask. Fakes permitem testes sem banco em parte da suíte. |

## Estilos e padrões

- **Arquitetura em camadas:** entrypoint, serviço, domínio e persistência têm responsabilidades reconhecíveis. O fluxo normal é HTTP → serviço → domínio/repositório → persistência.
- **Ports & Adapters, de forma incompleta:** contratos abstratos de repositório e fakes dão ao serviço uma fronteira substituível para persistência. Porém, os contratos estão no pacote `adapters`, não no domínio/aplicação, e o Flask escolhe diretamente implementações SQLAlchemy. Assim, o entrypoint conhece detalhes de infraestrutura.
- **Repository:** interfaces abstratas descrevem operações de armazenamento, com implementações fake e SQLAlchemy para Evento, Inscrição e Pagamento. Há também um contrato e implementação SQLAlchemy para Lote, mas não um Fake de Lote.
- **Service Layer:** funções de serviço coordenam entidades e repositórios sem colocar a lógica das rotas dentro do modelo. Exemplo: `confirmar_inscricao_apos_pagamento` verifica o pagamento e atualiza a inscrição.
- **Data Mapper clássico:** `orm.py` associa tabelas a classes existentes com `map_imperatively`, em vez de fazer as entidades herdarem de classes ORM. Isso reduz o acoplamento direto do modelo ao SQLAlchemy, embora o adapter dependa do modelo.
- **Regras no domínio:** transições e invariantes locais são métodos das entidades, como `Inscricao.realizar_checkin()` e `Pagamento.estornar()`. Regras que atravessam entidades são coordenadas pelos serviços.

## Fluxo de uma requisição

1. Uma rota Flask interpreta a requisição e chama a função de serviço correspondente.
2. O serviço consulta ou altera entidades por meio dos repositórios e invoca operações de domínio.
3. O repositório SQLAlchemy opera sobre a sessão compartilhada com a aplicação.
4. A rota confirma a sessão e serializa o resultado em JSON.

Nos testes, o cliente Flask recebe uma sessão SQLite em memória, o que permite percorrer o fluxo HTTP sem um serviço de banco externo. Os testes unitários também usam repositórios fake em alguns casos.

## Limitações observadas

- **Fronteira de transação no entrypoint:** as rotas fazem `commit()` diretamente, de modo que o serviço não é dono da transação e depende de coordenação do Flask. Isso diverge da intenção registrada de deixar o controle transacional na camada de serviço.
- **Contratos de repositório incompletos/inconsistentes:** `encerrar_evento` requer `listar_por_evento`, mas esse método não está no contrato nem na implementação SQLAlchemy de Inscrição. O endpoint detecta a ausência e responde `501`; `tests/e2e/test_eventos_api.py` documenta esse comportamento.
- **Composição de Evento e Lote não é uniforme:** o mapeamento ORM associa lotes ao evento, mas o serviço chamado pela rota de criação não associa o lote ao Evento nem chama o repositório de Lote para persistência. Além disso, o serializador da rota acessa `lote.evento_id`, atributo que `LoteDeIngresso` não define. O estoque do lote também não é atualizado pelo fluxo de criação de inscrição.
- **Associação da inscrição ao lote simplificada:** a tabela de inscrições persiste `lote` como texto, não como referência à tabela `lotes`. Isso limita integridade referencial e operações conjuntas sobre vaga, inscrição e pagamento.
- **Dependências de infraestrutura expostas:** `repository.py` importa SQLAlchemy para definir as implementações concretas; o entrypoint instancia essas classes e também cria engine/sessão. A inversão de dependência existe em parte, não de ponta a ponta.
- **Escopo ainda monolítico e síncrono:** Flask, serviço, domínio e persistência rodam no mesmo processo. Eventos de domínio, mensageria e CQRS aparecem na proposta da Fase 2, mas não estão implementados na estrutura atual.

## Avaliação

A escolha por camadas, entidades com invariantes e repositórios é adequada para o porte atual e facilita testes focados. A evidência não sustenta, porém, que o sistema já esteja plenamente hexagonal ou pronto para crescer como um fluxo transacional consistente: o entrypoint seleciona infraestrutura, o commit está nas rotas e contratos entre agregados estão incompletos. A prioridade arquitetural mais valiosa é completar os contratos de persistência necessários aos casos de uso e tornar explícita a fronteira transacional; introduzir mensageria ou CQRS antes disso aumentaria o custo sem resolver as lacunas atuais.

## Referências no código

- `src/eventos/domain/model.py`
- `src/eventos/service_layer/services.py`
- `src/eventos/adapters/repository.py`
- `src/eventos/adapters/orm.py`
- `src/eventos/entrypoints/flask_app.py`
- `tests/e2e/test_eventos_api.py`
- `DECISIONS.md`
- `PROPOSTA.md`