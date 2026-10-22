# Architecture Decision Records

Este arquivo reúne decisões de arquitetura registradas durante a Fase 1 e decisões de implementação que já orientam o código. Os autores foram atribuídos conforme o histórico de contribuições em `DECISIONS.md`. As consequências registram também as limitações observáveis na implementação atual.

## ADR-001 - Validar dados de participante e organizador no domínio

- **Status:** Aceito e implementado
- **Autora:** Gabriela Bitencourt Freire da Silva

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