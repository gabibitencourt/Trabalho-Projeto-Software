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