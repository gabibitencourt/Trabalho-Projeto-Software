# Registro de Decisões de Arquitetura e Autorrelato
Este documento registra as contribuições individuais e as decisões de projeto tomadas por cada integrante ao longo dos checkpoints.

## Fase 1 (Semana 1 a 4)

### Gabriela Bitencourt Freire da Silva (@gabibitencourt)

#### Checkpoint 1 (Semana 2) - Modelo de Domínio
- **Arquivos sob minha responsabilidade:**
- **Intervalo/Hashes de Commits:**
- **O que implementei:**
- **Justificativa de decisão de projeto:** 
- **Uso de IA Generativa (conforme Seção 2.5):** 
- **Simplificações conscientes:** 

#### Checkpoint 2 (Semana 3) - Repositórios e Persistência
- **Arquivos sob minha responsabilidade:**
- **Intervalo/Hashes de Commits:**
- **O que implementei:**
- **Justificativa de decisão de projeto:**
- **Uso de IA Generativa:** 

#### Entrega da Fase 1 (Semana 4) - Serviço e API
- **Arquivos sob minha responsabilidade:** 
- **Intervalo/Hashes de Commits:** 
- **O que implementei:**
- **Justificativa de decisão de projeto:**
- **Uso de IA Generativa:**

---

### Arthur Siqueira Campos Alexandrino (@devalexandrino)

#### Checkpoint 1 (Semana 2) - Modelo de Domínio
- **Arquivos sob minha responsabilidade:**
src/eventos/domain/model.py e tests/unit/test_evento.py — agregado Evento
- **Intervalo/Hashes de Commits:**
8f0f937 e 53a858b
- **O que implementei:**
implementei classe evento, enum StatusEvento e os testes pertinentes
- **Justificativa de decisão de projeto:** 
Unica decisão um pouco diferente que tive que tomar fazer a função alterar_lote 
localizar o lote pelo identificador, em vez de substituir todos os lotes do 
evento por um lote novo, assim podendo ter lotes simuntaneos.
- **Uso de IA Generativa (conforme Seção 2.5):** 
Usei ia para tirar duvidas de sintaxe, já que nao uso python com frequencia, e 
apoio conceitual de como usar o DDD da melhor forma.
- **Simplificações conscientes:** 
encerrar recebe a quantidade de inscriçoes pendentes como parametro 
inteiro em vez de consultar o agregado Inscrição diretamente

#### Checkpoint 2 (Semana 3) - Repositórios e Persistência
- **Arquivos sob minha responsabilidade:**
- **Intervalo/Hashes de Commits:**
- **O que implementei:**
- **Justificativa de decisão de projeto:**
- **Uso de IA Generativa:** 

#### Entrega da Fase 1 (Semana 4) - Serviço e API
- **Arquivos sob minha responsabilidade:** 
- **Intervalo/Hashes de Commits:** 
- **O que implementei:**
- **Justificativa de decisão de projeto:**
- **Uso de IA Generativa:**

---

### Felipe Gomes de Mello (@FelipeGMello)

#### Checkpoint 1 (Semana 2) - Modelo de Domínio
- **Arquivos sob minha responsabilidade:** 
entitys/LoteDeIngresso.py, teste_ingresso.py e pytest.ini
- **Intervalo/Hashes de Commits:** 
[6bb76b258869c7376fc3ebfe196fa0c6098c0a83, 4f907848fa8c81a05675a949b9840857700072f9, 1d3af982f79f0f25323d46ff88ff3d84ae424e3b, 2bf2b2e5fdd367ecc8bde21712aa662ba670beed, 5d04323b67bbe513643940956a5f1d8aecafda5a]
- **O que implementei:** Classe LoteDeIngresso e funções de teste para criação e o método venda() da classe.
- **Justificativa de decisão de projeto:** 
Só criei uma classe e uns testes, não foi tanta coisa.
- **Uso de IA Generativa (conforme Seção 2.5):** 
Utilizada apenas para consulta.
- **Simplificações conscientes:** 
Nenhuma.

#### Checkpoint 2 (Semana 3) - Repositórios e Persistência
- **Arquivos sob minha responsabilidade:**
- **Intervalo/Hashes de Commits:**
- **O que implementei:**
- **Justificativa de decisão de projeto:**
- **Uso de IA Generativa:** 

#### Entrega da Fase 1 (Semana 4) - Serviço e API
- **Arquivos sob minha responsabilidade:** 
- **Intervalo/Hashes de Commits:** 
- **O que implementei:**
- **Justificativa de decisão de projeto:**
- **Uso de IA Generativa:**

---

### João Marcello da Costa (@JoaoMarcelloCosta2000)

#### Checkpoint 1 (Semana 2) - Modelo de Domínio
- **Arquivos sob minha responsabilidade:** `src/eventos/domain/model.py` e `tests/unit/test_inscricao.py`, no que tange a entidade CheckIn
- **Intervalo/Hashes de Commits:** `dd14888` e o atual commit.
- **O que implementei:** Entidade `CheckIn`, lógica em `Inscricao.realizar_checkin()`, validação de status `CONFIRMADA`, bloqueio de duplicidade e proibição de cancelamento pós-check-in.
- **Justificativa de decisão de projeto:** Regras mantidas na raiz do agregado `Inscricao` para proteger as invariantes de negócio.
- **Uso de IA Generativa (conforme Seção 2.5):** Apoio conceitual em DDD, comandos Git e depuração de testes no Python.
- **Simplificações conscientes:** Lógica mantida em memória, sem banco de dados.

#### Checkpoint 2 (Semana 3) - Repositórios e Persistência
- **Arquivos sob minha responsabilidade:**
- **Intervalo/Hashes de Commits:**
- **O que implementei:**
- **Justificativa de decisão de projeto:**
- **Uso de IA Generativa:** 

#### Entrega da Fase 1 (Semana 4) - Serviço e API
- **Arquivos sob minha responsabilidade:** 
- **Intervalo/Hashes de Commits:** 
- **O que implementei:**
- **Justificativa de decisão de projeto:**
- **Uso de IA Generativa:**

---

### Lucas Paixao de Lima Costa (@LucasLimmm2000)

#### Checkpoint 1 (Semana 2) - Modelo de Domínio
- **Arquivos sob minha responsabilidade:** src/eventos/domain/model.py (StatusPagamento e Pagamento), tests/unit/test_pagamento.py
- **Intervalo/Hashes de Commits:** 81c04b0, a395bf9, 4afea2c
- **O que implementei:** Classe Pagamento com status (pendente, aprovado, recusado, estornado) e os metodos aprovar, recusar e estornar. Nao deixa aprovar pagamento duas vezes, so aprova/recusa se estiver pendente, e nao deixa estornar se a inscricao ja fez check-in. Fiz 9 testes cobrindo isso.
- **Justificativa de decisão de projeto:** Usei enum pra status em vez de string pra nao deixar valor errado entrar. A regra do check-in fica dentro do Pagamento mesmo, porque ele ja tem acesso a inscricao.
- **Uso de IA Generativa (conforme Seção 2.5):** 
- **Simplificações conscientes:** Pagamento ainda usa a Inscricao direto em memoria, sem repositorio/banco.

#### Checkpoint 2 (Semana 3) - Repositórios e Persistência
- **Arquivos sob minha responsabilidade:**
- **Intervalo/Hashes de Commits:**
- **O que implementei:**
- **Justificativa de decisão de projeto:**
- **Uso de IA Generativa:** 

#### Entrega da Fase 1 (Semana 4) - Serviço e API
- **Arquivos sob minha responsabilidade:** 
- **Intervalo/Hashes de Commits:** 
- **O que implementei:**
- **Justificativa de decisão de projeto:**
- **Uso de IA Generativa:**

---

### Samuel Carvalho Dias (@SamuelCDiias)

#### Checkpoint 1 (Semana 2) - Modelo de Domínio
- **Arquivos sob minha responsabilidade:** src/eventos/domain/model.py e tests/unit/test_inscricao.py.
- **Intervalo/Hashes de Commits:** 678b3af.
- **O que implementei:** O agregado Inscricao, associado a participante e lote, com o estado inicial PENDENTE e os estados CONFIRMADA e CANCELADA. Implementei as operações de confirmação, cancelamento e check-in, além de testes unitários para o estado inicial e as transições permitidas e inválidas.
- **Justificativa de decisão de projeto:** As regras de transição foram mantidas no próprio agregado para preservar as invariantes de negócio: uma inscrição cancelada não pode ser confirmada; o check-in exige inscrição confirmada e não pode ser repetido; e uma inscrição com check-in não pode ser cancelada. As operações inválidas sinalizam erro por meio de OperacaoInvalidaError.
- **Uso de IA Generativa (conforme Seção 2.5):** Nenhum.
- **Simplificações conscientes:** Participante e lote são armazenados como referências recebidas pelo construtor, e o check-in é representado por um booleano em memória, sem entidade própria ou persistência nesta etapa.

#### Checkpoint 2 (Semana 3) - Repositórios e Persistência
- **Arquivos sob minha responsabilidade:**
- **Intervalo/Hashes de Commits:**
- **O que implementei:**
- **Justificativa de decisão de projeto:**
- **Uso de IA Generativa:** 

#### Entrega da Fase 1 (Semana 4) - Serviço e API
- **Arquivos sob minha responsabilidade:** 
- **Intervalo/Hashes de Commits:** 
- **O que implementei:**
- **Justificativa de decisão de projeto:**
- **Uso de IA Generativa:**