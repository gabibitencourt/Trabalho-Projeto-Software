# Proposta — Sistema de Eventos com Inscrições e Lotes de Ingressos

## 1. Integrantes do grupo

| Nome | Usuário GitHub |
|---|---|
| Arthur Siqueira Campos Alexandrino | @devalexandrino | 
| Felipe Gomes de Mello | @FelipeGMello | 
| Gabriela Bitencourt Freire da Silva | @gabibitencourt | 
| João Marcello da Costa | @JoaoMarcelloCosta2000 | 
| Lucas Paixao de Lima Costa | @LucasLimmm2000 | 
| Samuel Carvalho Dias | @SamuelCDiias | 

## 2. Domínio escolhido

Sistema de gestão de eventos com inscrições, lotes de ingressos e check-in. O sistema permite que organizadores criem eventos com múltiplos lotes de ingresso (preços e quantidades diferentes por lote), participantes se inscrevam e paguem por um ingresso, e a organização faça o controle de check-in no dia do evento.

O domínio não é um CRUD simples porque envolve controle de concorrência sobre estoque limitado (lotes), consistência entre pagamento e confirmação de inscrição, e regras de acesso (check-in) que dependem do estado de outras entidades.

## 3. Entidades de negócio (7)

1. **Evento** — nome, data, local, status (planejado / em andamento / encerrado)
2. **Lote de Ingresso** — nome (ex.: "1º lote"), preço, quantidade total, quantidade vendida
3. **Participante** — nome, e-mail, documento
4. **Inscrição** — vincula participante a um lote de um evento, com status (pendente / confirmada / cancelada)
5. **Pagamento** — vinculado a uma inscrição, valor, status (pendente / aprovado / recusado / estornado)
6. **Check-in** — registro de entrada de uma inscrição confirmada no evento
7. **Organizador** — responsável pelo evento (pode ser só um papel de usuário, sem necessariamente virar agregado próprio)

## 4. Agregados (3) e invariantes

### 4.1 Agregado `Evento` (raiz: Evento, contém Lotes)
Responsável por: **Arthur Siqueira e Felipe Gomes**

- Não é possível vender além da quantidade total de um lote (`vendidos <= quantidade_total`).
- Não é possível criar ou alterar um lote depois que o evento já começou.
- Não é possível reduzir a quantidade de um lote para um valor menor do que já foi vendido.
- Não é possível encerrar o evento com inscrições em status "pendente" (pagamento não resolvido) — precisam ser canceladas antes.

### 4.2 Agregado `Inscrição` (raiz: Inscrição, contém Participante e Organizador)
Responsável por: **Samuel Carvalho e Gabriela Bitencourt**

- Não é possível inscrever um participante em um lote esgotado.
- Não é possível criar uma inscrição sem um participante válido vinculado.
- Não é possível alterar os dados do participante após a confirmação da inscrição.
- O organizador é responsável pela liberação e gestão de novos lotes e inscrições.

### 4.3 Agregado `Pagamento e Check-in` (raiz: Pagamento / Checkin)
Responsável por: **Lucas Paixao e João Marcello**

- Um pagamento aprovado não pode ser reprocessado (idempotência — evita cobrança duplicada).
- Só é possível fazer check-in se a inscrição vinculada estiver com status "confirmada" e pagamento aprovado.
- Não é possível fazer check-in duplicado da mesma inscrição.
- Estorno de pagamento só é permitido se a inscrição ainda não tiver realizado check-in.

## 5. Casos de uso / transações de serviço (10)

1. Criar evento
2. Criar lote de ingressos para um evento
3. Inscrever participante em um lote (reserva de vaga)
4. Processar pagamento de uma inscrição
5. Confirmar inscrição (acionado após aprovação do pagamento)
6. Cancelar inscrição e estornar pagamento
7. Realizar check-in de uma inscrição
8. Encerrar evento
9. Consultar vagas disponíveis por lote (read model — CQRS, Fase 2)
10. Relatório de check-ins realizados por evento (read model — CQRS, Fase 2)

## 6. Divisão inicial de responsabilidades

## 6. Divisão inicial de responsabilidades

| Agregado | Integrante | Entidade / Foco | Semana 2 — Domínio | Semana 3 — Repositório | Semana 4 — Serviço + API | Usuário GitHub |
|---|---|---|---|---|---|---|
| **Evento** | Arthur Siqueira | `Evento` | Classe `Evento` + invariantes | `SqlAlchemyEventoRepository` | Casos de uso e rotas de Evento | @devalexandrino |
| | Felipe Gomes | `Lote` | Classe `Lote` + validação de estoque | `FakeEventoRepository` + testes | Endpoints de Lotes | @FelipeGMello |
| **Inscrição** | Samuel Carvalho | `Inscricao` | Classe `Inscricao` + status | `SqlAlchemyInscricaoRepository` | Casos de uso de Inscrição | @SamuelCDiias |
| | Gabriela Bitencourt | `Participante` e `Organizador` | Classes `Participante` e `Organizador` | `FakeInscricaoRepository` + testes | Endpoints de Inscrição e Participantes | @gabibitencourt |
| **Pagamento & Check-in** | Lucas Paixao | `Pagamento` | Classe `Pagamento` + idempotência | `SqlAlchemyPagamentoRepository` | Casos de uso de Pagamento | @LucasLimmm2000 |
| | João Marcello | `Checkin` | Classe `Checkin` + validação duplicidade | Suporte/testes de integração | Endpoints de Check-in (`POST /checkin`) | @JoaoMarcelloCosta2000 |

## 7. Observações sobre a Fase 2

- Os **eventos de domínio** naturais aqui são: `PagamentoAprovado`, `InscricaoConfirmada`, `LoteEsgotado`, `CheckinRealizado` — cobrindo pelo menos dois agregados (Pagamento → Inscrição → Evento), o que atende ao requisito do checkpoint de eventos/message bus.
- Os **comandos** que atravessam mais de um agregado incluem `ConfirmarInscricaoAposPagamento` (Pagamento → Inscrição) e `EncerrarEvento` (Evento → Inscrição, para bloquear pendências).
- A simulação de "serviço externo" (Seção 6 do enunciado) pode ser um `FakeNotifier` que "envia" e-mail de confirmação de inscrição ou de lote quase esgotado.