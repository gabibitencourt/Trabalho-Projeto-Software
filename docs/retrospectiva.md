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