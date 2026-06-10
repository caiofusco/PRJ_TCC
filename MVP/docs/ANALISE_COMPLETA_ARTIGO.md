# Análise completa do artigo e transformação em MVP

## 1. Síntese executiva

O artigo propõe a modernização de uma pequena empresa de serviços automotivos por meio de um sistema web integrado com inteligência artificial. O problema central é a dependência de processos manuais para agendamento, controle de ordens de serviço, comunicação interna, estoque e registro de vendas. Essa operação manual causa conflitos de agenda, falhas de comunicação, perda de histórico, retrabalho e baixa previsibilidade operacional.

A solução defendida no artigo é um sistema web em camadas, com front-end, back-end e banco relacional, capaz de centralizar dados e oferecer recursos inteligentes para sugerir horários, priorizar atendimentos e otimizar a alocação dos técnicos.

O MVP entregue neste projeto traduz essa proposta em uma aplicação funcional usando Python, Flask e MySQL.

## 2. Problema de pesquisa identificado

A pergunta orientadora do artigo é: como o uso de um sistema web integrado com inteligência artificial pode melhorar a eficiência e o controle dos processos de agendamento e serviços?

Esse problema foi decomposto nos seguintes pontos operacionais:

1. Agendamentos feitos manualmente geram choque de horários.
2. A ausência de base única dificulta a recuperação do histórico de cliente e veículo.
3. Técnicos podem ser alocados sem considerar disponibilidade, carga de trabalho ou especialidade.
4. Ordens de serviço não integradas dificultam acompanhar execução e conclusão.
5. Estoque e vendas desconectados criam risco de inconsistência nos produtos usados.
6. A gestão não possui indicadores consolidados para tomada de decisão.

## 3. Objetivo convertido em produto

O objetivo acadêmico de analisar e propor um sistema web com IA foi convertido em objetivo de produto:

> Construir um MVP web para oficinas e serviços automotivos que centralize cadastros, veículos, serviços, agenda, ordens, estoque e vendas, com um módulo de IA capaz de sugerir horários e técnicos a partir de histórico, disponibilidade e especialidade.

## 4. Escopo funcional extraído do fluxograma

O fluxograma do artigo mostra os seguintes blocos de processo:

- login e dashboard;
- cadastro de cliente;
- cadastro de veículo vinculado ao cliente;
- agendamento com verificação de disponibilidade;
- sugestão de novo horário pela IA quando há conflito;
- criação de ordem de serviço;
- atribuição manual ou inteligente de técnico;
- execução do serviço;
- atualização de status da OS;
- registro de itens usados;
- venda a partir da OS;
- cálculo de valor total;
- atualização de estoque;
- alerta e sugestão de reposição;
- armazenamento em banco de dados;
- análise de histórico pela IA;
- geração de insights para decisão.

Todos esses blocos foram representados no MVP, com níveis diferentes de profundidade adequados ao estágio inicial do produto.

## 5. Entidades principais extraídas do MER

O MER do artigo indicou as seguintes entidades essenciais:

- usuário;
- cliente;
- veículo;
- agendamento;
- ordem de serviço;
- serviço;
- produto;
- venda;
- item de venda;
- item de ordem de serviço.

O MVP manteve essas entidades e adicionou duas tabelas de apoio:

- `stock_movements`, para rastrear entradas, saídas e ajustes de estoque;
- `ai_recommendation_logs`, para auditar recomendações do módulo de IA.

## 6. Perfis de usuário

### Administrador

Responsável por manter usuários, técnicos, serviços, produtos e visualizar toda a operação.

### Atendente

Responsável por cadastrar clientes, veículos, agendamentos, vendas e iniciar ordens de serviço.

### Técnico

Responsável por acompanhar e atualizar ordens de serviço, registrar diagnóstico e concluir execução.

## 7. Requisitos funcionais implementados

| Código | Requisito | Implementação |
|---|---|---|
| RF01 | Autenticar usuário | Login com Flask-Login |
| RF02 | Gerenciar clientes | CRUD de clientes com inativação |
| RF03 | Gerenciar veículos | CRUD de veículos vinculados ao cliente |
| RF04 | Gerenciar serviços | Cadastro com preço, categoria e tempo estimado |
| RF05 | Gerenciar usuários/técnicos | CRUD restrito ao administrador |
| RF06 | Criar agendamento | Tela com cliente, veículo, serviço, técnico, data e duração |
| RF07 | Verificar conflitos | Validação por técnico, início e fim do atendimento |
| RF08 | Sugerir agenda com IA | Endpoint `/api/ai/schedule` e painel na tela de agendamento |
| RF09 | Criar OS a partir de agendamento | Ação direta na lista de agendamentos |
| RF10 | Gerenciar OS | Listagem, detalhe, edição, status e itens de serviço |
| RF11 | Controlar estoque | Produtos, saldo mínimo, movimentações e alerta |
| RF12 | Registrar venda | Venda de produto com baixa automática de estoque |
| RF13 | Sugerir reposição | Endpoint `/api/ai/restock` e alertas no dashboard |
| RF14 | Exibir indicadores | Dashboard com KPIs, agenda, OS e métricas do artigo |

## 8. Requisitos não funcionais implementados

- Arquitetura web em camadas.
- Banco relacional MySQL.
- Separação entre modelos, rotas, templates e arquivos estáticos.
- Interface responsiva em HTML, CSS e JavaScript.
- Senhas armazenadas com hash.
- Uso de variáveis de ambiente para conexão e segredo.
- Docker Compose para simplificar execução.
- Logs de recomendações de IA para auditoria.
- Estrutura preparada para expansão por API.

## 9. Módulo de IA do MVP

O artigo propõe análise preditiva baseada em dados históricos. Para o MVP, foi implementada uma IA heurística-preditiva, adequada a cenários com poucos dados iniciais.

A IA executa quatro etapas:

1. **Previsão de duração:** usa histórico de OS concluídas por serviço. Se houver poucos dados, mistura histórico e tempo estimado. Se não houver histórico, usa o tempo cadastrado.
2. **Verificação de disponibilidade:** descarta horários que conflitam com agendamentos existentes do técnico.
3. **Pontuação do técnico:** considera compatibilidade entre categoria do serviço e especialidades cadastradas no perfil do técnico.
4. **Balanceamento de carga:** penaliza técnicos com maior carga de agenda no dia.

A resposta da IA contém:

- início sugerido;
- fim sugerido;
- técnico recomendado;
- duração prevista;
- score;
- justificativa legível para o usuário.

## 10. Regras de negócio principais

1. Um cliente pode possuir vários veículos.
2. Um veículo pertence a um único cliente.
3. Um agendamento deve possuir cliente, veículo, serviço e técnico.
4. Um técnico não pode ter dois agendamentos sobrepostos.
5. Um agendamento pode gerar uma única ordem de serviço.
6. Uma ordem de serviço pode conter vários itens de serviço.
7. Ao concluir uma OS, a data de conclusão é registrada.
8. Produtos com quantidade menor ou igual ao mínimo entram em alerta de reposição.
9. Uma venda reduz automaticamente o estoque do produto vendido.
10. Usuários inativos não devem acessar o sistema.

## 11. Métricas do artigo representadas no dashboard

O artigo apresenta como resultados esperados:

- redução do tempo de agendamento de 15 para 5 minutos;
- redução dos erros de comunicação de 12 para 2 por semana;
- aumento de precisão na alocação de técnicos de 60% para 92%.

Essas métricas foram incluídas no dashboard como referência de validação futura. Em produção, esses indicadores devem ser calculados com dados reais.

## 12. Decisões técnicas adotadas

O artigo mencionava Java no back-end. O MVP foi desenvolvido em Python por solicitação do usuário e por permitir prototipação rápida com Flask. A mudança não altera a proposta arquitetural do artigo, pois a solução continua organizada em camadas:

- front-end: HTML, CSS e JavaScript;
- back-end: Python/Flask;
- persistência: MySQL;
- IA: módulo Python com regras preditivas e heurísticas;
- deploy: Docker Compose.

## 13. Limitações do MVP

- A IA usa heurísticas e histórico local, não um modelo treinado com grande massa de dados.
- As vendas aceitam um produto por lançamento para manter simplicidade inicial.
- Não há integração com WhatsApp, pagamento, emissão fiscal ou scanner automotivo.
- A validação de permissões por perfil é básica: usuários são autenticados e o cadastro de usuários é restrito a administradores.
- O sistema ainda não implementa testes automatizados completos.

## 14. Evoluções recomendadas

1. Implantar em ambiente real e coletar dados de uso.
2. Calcular métricas reais de tempo de atendimento, conflitos e produtividade.
3. Criar app móvel para técnicos.
4. Permitir múltiplos produtos por venda em uma única tela.
5. Integrar WhatsApp para lembretes de agenda.
6. Adicionar machine learning supervisionado quando houver histórico suficiente.
7. Criar relatórios financeiros por período.
8. Integrar estoque com itens usados na OS.
9. Implementar trilha de auditoria completa.
10. Criar permissões granulares por perfil.

## 15. Critérios de aceite do MVP

O MVP pode ser considerado validado quando o usuário conseguir:

- acessar o sistema com login;
- cadastrar cliente e veículo;
- cadastrar serviço;
- gerar sugestões de horário por IA;
- salvar agendamento sem conflito;
- criar OS a partir do agendamento;
- alterar status da OS até conclusão;
- cadastrar produto e movimentar estoque;
- registrar venda com baixa automática;
- visualizar indicadores no dashboard.
