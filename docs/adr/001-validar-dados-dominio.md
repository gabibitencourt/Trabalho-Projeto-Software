# Architecture Decision Records

Este arquivo reúne decisões de arquitetura registradas durante a Fase 1 e decisões de implementação que já orientam o código. Os autores foram atribuídos conforme o histórico de contribuições em `DECISIONS.md`. As consequências registram também as limitações observáveis na implementação atual.

## ADR-001 - Validar dados de participante e organizador no domínio

- **Status:** Aceito e implementado
- **Autor:** Felipe Gomes de Mello

### Contexto

Participantes e organizadores não devem ser criados com dados cadastrais obviamente inválidos. Se a validação ficar apenas nos endpoints, outros consumidores poderão instanciar objetos inválidos e as regras ficarão duplicadas.

### Decisão

Validar os dados obrigatórios nos construtores de `Participante` e `Organizador`. O domínio normaliza nome, e-mail e documento, e valida o papel do organizador.

### Alternativas consideradas

- Validar os dados somente na API Flask.
- Criar um serviço/validador separado e permitir que as entidades aceitem dados não validados.

### Consequências

- Qualquer caminho de criação passa pelas mesmas verificações e os testes unitários não precisam de Flask.
- O construtor mistura criação e validação, e a validação atual de e-mail é deliberadamente simples (presença de `@`); regras mais completas exigiriam evolução explícita.

## ADR-002 - Desacoplar encerramento de evento do agregado de inscrição via camada de serviço

- **Status:** Aceito e implementado (parcialmente nos adapters)
- **Autor:** Arthur Siqueira Campos Alexandrino

### Contexto

Pelas invariantes de negócio do sistema, um `Evento` não pode ser encerrado enquanto houver inscrições com status `PENDENTE`. No entanto, `Evento` e `Inscricao` pertencem a agregados distintos (`Evento` e `Inscricao`), e fazer a entidade `Evento` consultar repositórios ou manter referências diretas a todas as instâncias de `Inscricao` violaria as fronteiras de agregado e acoplaria o modelo de domínio ao mecanismo de busca.

### Decisão

Manter a regra de invariante dentro de `Evento.encerrar(inscricoes_pendentes)`, recebendo apenas a contagem inteira de inscrições pendentes como parâmetro, e delegar à camada de serviço (`services.encerrar_evento`) a coordenação entre `repositorio_evento` e `repositorio_inscricao.listar_por_evento(identificador_evento)` para apurar essa quantidade antes de invocar o domínio.

### Alternativas consideradas

- Passar a coleção de objetos `Inscricao` ou o próprio `AbstractInscricaoRepository` para dentro do método `Evento.encerrar()`.
- Validar a existência de inscrições pendentes apenas na camada de serviço ou na rota Flask, transformando `Evento.encerrar()` em um simples *setter* de status.

### Consequências

- A entidade `Evento` permanece simples, coesa e testável unitariamente sem depender de `Inscricao` nem de dublês de repositório (`tests/unit/test_evento.py`).
- A operação completa de encerramento passa a depender de um contrato transversal (`listar_por_evento`) no repositório de inscrições; como `SqlAlchemyInscricaoRepository` ainda não implementa esse método, a rota `POST /eventos/<id>/encerrar` precisa tratar a ausência retornando HTTP `501 Not Implemented`.
