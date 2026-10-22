# ADR-002: Uso de conjunto nativo (`set`) em repositórios em memória (Fake Repository)

- **Status:** Aceito e implementado
- **Data:** 22/10/2026
- **Autora:** Gabriela Bitencourt Freire da Silva (@gabibitencourt)

## Contexto
Para executar os testes unitários e de integração de forma rápida e sem dependência de um banco de dados relacional real, foi necessária a criação de repositórios em memória (*Fake Repositories*). Era preciso escolher uma estrutura de dados Python adequada para armazenar e manipular as instâncias sem permitir duplicatas acidentais.

## Decisão
Utilizar conjuntos nativos do Python (`set`) para armazenar os objetos nos repositórios em memória (como no `FakeEventoRepository` e `FakePagamentoRepository`) e simular a unicidade de registros com base na identidade das instâncias em memória.

## Alternativas consideradas
1. **Lista nativa (`list`):** Permitiria salvar acidentalmente duas referências idênticas do mesmo objeto sem sinalizar erro no ambiente de testes.
2. **Dicionário nativo (`dict`):** Utilizado pontualmente quando a busca primária ocorre estritamente por chave primária (como no `FakeInscricaoRepository`), porém exige gerenciamento manual de chaves.

## Consequências
- **Positivas:** O `set` impede a inclusão duplicada da mesma instância em memória, simulando o comportamento de restrição de chave primária do banco de dados relacional; permite execução ultrarrápida da suíte de testes unitários.
- **Negativas:** Para buscas por atributos específicos (como ID), exige percorrer o conjunto com geradores/filtros.