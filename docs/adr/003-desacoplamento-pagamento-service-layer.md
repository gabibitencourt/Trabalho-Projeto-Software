# ADR-003 - Orquestração do agregado Pagamento na Camada de Serviço com Injeção de Repositórios

- **Status:** Aceito e implementado
- **Data:** 22/10/2026
- **Autor:** João Marcell (@costa)

## Contexto

A entidade `Pagamento` no modelo de domínio (`model.py`) necessita de uma referência válida à entidade `Inscricao` em seu construtor e protege regras de negócio críticas (como bloquear a aprovação de pagamentos não pendentes via `OperacaoInvalidaError` ou validar ausência de check-in antes de um estorno). 

Fazer o endpoint HTTP Flask instanciar repositórios e consultar a inscrição diretamente acoplaria as regras de fluxo à camada web. Por outro lado, permitir que o domínio `Pagamento` busque sua própria inscrição no banco violaria a separação de responsabilidades e as fronteiras de agregados do DDD.

## Decisão

Isolar os casos de uso de pagamento na Camada de Serviço (`src/eventos/service_layer/services.py`) através das funções:
- `registrar_pagamento(identificador, inscricao_id, valor, repositorio_pagamento, repositorio_inscricao)`
- `obter_pagamento(identificador, repositorio_pagamento)`
- `aprovar_pagamento(identificador, repositorio_pagamento)`

O serviço recebe os repositórios por injeção de dependência, busca a `Inscricao` correspondente pelo identificador primitivo, levanta `InscricaoNaoEncontradaError` caso ela não exista, instancia a entidade pura `Pagamento(identificador, inscricao, valor)` e a persiste através de `repositorio_pagamento.adicionar()`. No fluxo de aprovação, delega a transição de estado ao método de domínio `pagamento.aprovar()`.

## Alternativas consideradas

1. **Lógica de orquestração direta na rota Flask (`POST /pagamentos`):** A rota faria o `session.query(Inscricao)` e criaria o pagamento diretamente.
   - *Descarte:* Inviabilizaria a escrita de testes unitários isolados da regra de negócio sem instanciar o cliente HTTP e a infraestrutura web.
2. **Entidade `Pagamento` acessar a persistência:** A própria entidade receberia a sessão ou o repositório para validar a inscrição.
   - *Descarte:* Violaria o princípio de persistência ignorante (*Persistence Ignorance*) e os limites de agregação do DDD.

## Consequências

- **Positivas:**
  - Alta testabilidade: os fluxos de sucesso e exceções de pagamento são testados unitariamente em frações de segundo com repositórios dublê (`FakePagamentoRepository` e `FakeInscricaoRepository`) em `tests/unit/test_services_pagamento.py`.
  - Mapeamento limpo: alinha-se perfeitamente com o Data Mapper imperativo configurado em `orm.py` (`properties={"inscricao": relationship(Inscricao)}`).
- **Negativas / Limitações:**
  - O controle transacional definitivo (`session.commit()`) permanece delegado ao endpoint Flask até a eventual introdução do padrão *Unit of Work*.