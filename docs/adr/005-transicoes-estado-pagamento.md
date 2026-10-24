# ADR-005 - Transições de estado do Pagamento como métodos guardados por enum

- **Status:** Aceito e implementado
- **Data:** 23/10/2026
- **Autor:** Lucas Paixao de Lima Costa (@LucasLimmm2000)

## Contexto

A entidade `Pagamento` carrega um status (`StatusPagamento`: `PENDENTE` / `APROVADO` / `RECUSADO` / `ESTORNADO`) que decide quais transições são permitidas e protege duas invariantes do agregado (`PROPOSTA.md`, 4.3): idempotência de aprovação (um pagamento aprovado não pode ser reprocessado) e a regra de estorno (só permitido se a inscrição vinculada ainda não teve check-in). Se `status` fosse um atributo público e livremente atribuível, qualquer código em qualquer camada poderia fazer `pagamento.status = StatusPagamento.APROVADO` diretamente, sem passar pela checagem de pré-condição, e a invariante deixaria de ser garantida pelo próprio objeto.

## Decisão

Cada transição válida é um método da entidade (`aprovar()`, `recusar()`, `estornar()`) que primeiro compara `self.status` contra os valores aceitos do enum `StatusPagamento` e levanta `OperacaoInvalidaError` quando a pré-condição não é satisfeita, só então atribuindo o novo status. `estornar()` também verifica `inscricao.checkin_realizado` antes de mudar o estado. O construtor fixa `status=StatusPagamento.PENDENTE` por padrão e não existe nenhum setter público de `status` fora desses três métodos.

## Alternativas consideradas

1. **Campo `status` livre, validado só na camada de serviço ou na rota Flask antes de atribuir.**
   - *Descarte:* duplicaria a validação em cada ponto de entrada e deixaria o estado vulnerável sempre que um caminho novo (outro serviço, um script administrativo) esquecesse de repetir a checagem.
2. **Máquina de estados genérica, com tabela de transições configurável e reaproveitada pelos três agregados que têm status (`Evento`, `Inscricao`, `Pagamento`).**
   - *Descarte:* os três agregados não compartilham as mesmas transições nem as mesmas pré-condições — a de `Pagamento.estornar()` depende de outro agregado (`Inscricao.checkin_realizado`); a de `Evento.encerrar()` depende de uma contagem externa de inscrições pendentes. Generalizar agora custaria indireção sem reaproveitamento real.

## Consequências

- **Positivas:** a idempotência de aprovação e a regra de estorno são garantidas no mesmo lugar que define o enum, e testadas inteiramente em memória, sem repositório nem sessão (`tests/unit/test_pagamento.py`: `test_nao_reprocessa_pagamento_ja_aprovado`, `test_nao_estorna_pagamento_de_inscricao_com_checkin`). Na camada de serviço, `recusar_pagamento`/`estornar_pagamento` só propagam a `OperacaoInvalidaError` do domínio, sem reimplementar a checagem.
- **Negativas:** adicionar um novo status (por exemplo, um estado intermediário de "em análise" vindo de um gateway de pagamento externo) exige revisar os três métodos de transição e seus testes, em vez de atualizar uma única tabela; hoje `aprovar()`, `recusar()` e `estornar()` repetem a mesma estrutura de comparação e `raise` sem nenhuma abstração em comum entre eles.
