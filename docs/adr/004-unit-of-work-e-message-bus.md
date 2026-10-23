# ADR-004 - Mover a fronteira transacional para a camada de serviço com Unit of Work e preparar o Message Bus

- **Status:** Proposto
- **Data:** 23/10/2026
- **Autor:** Samuel Carvalho Dias (@SamuelCDiias)

## Contexto

Na Fase 1, a camada de serviço recebe repositórios avulsos e a rota Flask é quem confirma a transação: `flask_app.py` chama `session.commit()` em cada endpoint de escrita e instancia diretamente `SqlAlchemyInscricaoRepository`, `SqlAlchemyPagamentoRepository`, `SqlAlchemyEventoRepository` e `SqlAlchemyLoteDeIngressoRepository`. Isso contraria a intenção registrada em `DECISIONS.md` (Checkpoint 2) de deixar o controle de transação com a camada de serviço.

No agregado `Inscricao`, a consequência é concreta: `services.criar_inscricao` cria a inscrição sem chamar `LoteDeIngresso.venda()`, e `lote` é persistido como texto. Não há uma unidade atômica que garanta "inscrição criada ⇔ vaga consumida", e a invariante "não é possível inscrever em lote esgotado" (`PROPOSTA.md`, 4.2) não é aplicada no fluxo real. Além disso, a confirmação da inscrição após o pagamento depende de o cliente chamar manualmente `POST /pagamentos/<id>/confirmar-inscricao`.

A Fase 2 exige eventos de domínio e message bus atravessando pelo menos dois agregados (`PagamentoAprovado` → `InscricaoConfirmada`).

## Decisão

1. Introduzir o padrão **Unit of Work** em `src/eventos/service_layer/unit_of_work.py`, com `AbstractUnitOfWork` (repositórios `eventos`, `inscricoes`, `pagamentos`, e métodos `commit()`/`rollback()`, usado como gerenciador de contexto), `SqlAlchemyUnitOfWork` e `FakeUnitOfWork` para testes.
2. Os serviços passam a receber a UoW e chamam `uow.commit()` ao final; em caso de exceção, a UoW faz `rollback()`. As rotas Flask deixam de chamar `session.commit()` e de conhecer as classes SQLAlchemy.
3. `criar_inscricao` passa a carregar o lote pela UoW, chamar `lote.venda()` e persistir inscrição e lote na mesma transação.
4. Em seguida, as entidades passam a registrar eventos de domínio (`PagamentoAprovado`, `InscricaoConfirmada`, `LoteEsgotado`, `CheckinRealizado`), coletados pela UoW após o commit e despachados por um `MessageBus` em processo.

## Alternativas consideradas

1. **Manter o commit nas rotas (status quo):**
   - *Descarte:* deixa a regra de atomicidade fora dos testes unitários e obriga cada nova rota a lembrar de confirmar a sessão; não resolve o estoque de lote.
2. **Passar a `Session` do SQLAlchemy diretamente para os serviços:**
   - *Descarte:* resolveria o commit, mas acoplaria `services.py` ao SQLAlchemy, violando a medida do atributo de modificabilidade (zero importações de `sqlalchemy` na camada de serviço) e impedindo testes com Fakes.
3. **Message Bus antes da Unit of Work:**
   - *Descarte:* os handlers continuariam sem fronteira transacional própria; adicionaria indireção sem fechar a lacuna atual.
4. **Active Record (entidades herdando do ORM declarativo):**
   - *Descarte:* reduziria código, mas acabaria com a persistência ignorante do domínio e com os testes em memória, que são o atributo de qualidade de maior prioridade.

## Consequências

- **Positivas:**
  - A transação passa a ser responsabilidade do caso de uso e pode ser verificada em testes unitários (`FakeUnitOfWork.committed`).
  - O entrypoint Flask passa a depender apenas de uma fábrica de UoW, completando a inversão de dependência descrita em `docs/arquitetura.md`.
  - Inscrição e consumo de vaga do lote ficam atômicos; uma falha em `venda()` desfaz a inscrição.
  - Abre caminho direto para os eventos de domínio e o message bus da Fase 2.
- **Negativas / Limitações:**
  - Exige alterar a assinatura de todas as funções de `services.py`, os testes de serviço e as rotas, o que precisa ser coordenado entre os seis integrantes para evitar conflitos.
  - Com eventos, handlers disparados após o commit rodam em transações separadas; uma falha no handler de confirmação deixa o pagamento aprovado e a inscrição pendente até haver reprocessamento.
  - O fluxo entre agregados fica menos explícito no código, o que dificulta a depuração.
