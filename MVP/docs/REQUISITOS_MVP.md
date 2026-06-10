# Requisitos do MVP

## Visão do produto

Sistema web para pequenas oficinas e serviços automotivos, com foco em organização operacional, redução de falhas de agendamento e apoio inteligente à alocação de técnicos.

## Product backlog inicial

### Épico 1: Acesso e perfis

- Como usuário, quero fazer login para acessar o sistema com segurança.
- Como administrador, quero cadastrar atendentes e técnicos para controlar permissões.
- Como administrador, quero registrar especialidades dos técnicos para melhorar recomendações da IA.

### Épico 2: Cadastro operacional

- Como atendente, quero cadastrar clientes para recuperar rapidamente seus dados.
- Como atendente, quero cadastrar veículos vinculados ao cliente para manter histórico por placa.
- Como administrador, quero cadastrar serviços com tempo estimado e preço base.

### Épico 3: Agenda inteligente

- Como atendente, quero criar agendamentos com cliente, veículo, serviço e técnico.
- Como atendente, quero ser alertado sobre conflitos de agenda.
- Como atendente, quero receber sugestões de horário e técnico com justificativa da IA.

### Épico 4: Ordem de serviço

- Como atendente, quero gerar uma OS a partir de um agendamento.
- Como técnico, quero atualizar status e diagnóstico da OS.
- Como gestor, quero visualizar OS abertas, em execução e concluídas.

### Épico 5: Estoque e venda

- Como atendente, quero cadastrar produtos e quantidades.
- Como atendente, quero registrar entradas e saídas de estoque.
- Como atendente, quero registrar vendas e reduzir o estoque automaticamente.
- Como gestor, quero receber alerta de produtos abaixo do mínimo.

### Épico 6: Indicadores

- Como gestor, quero visualizar dashboard com KPIs operacionais.
- Como gestor, quero comparar os indicadores esperados do artigo com dados reais futuramente.

## Requisitos funcionais priorizados

| Prioridade | Requisito |
|---|---|
| Alta | Login |
| Alta | CRUD de clientes |
| Alta | CRUD de veículos |
| Alta | CRUD de serviços |
| Alta | Agendamento com verificação de conflito |
| Alta | Sugestão de agendamento por IA |
| Alta | Ordem de serviço |
| Média | Estoque |
| Média | Venda |
| Média | Dashboard |
| Baixa | Relatórios avançados |
| Baixa | Integrações externas |

## Requisitos não funcionais

- O sistema deve usar banco relacional MySQL.
- A aplicação deve ser executável via Docker Compose.
- As senhas devem ser armazenadas com hash.
- A interface deve ser responsiva.
- O código deve ser organizado em módulos.
- O sistema deve registrar recomendações de IA para auditoria.

## Fora do escopo do MVP

- Emissão de nota fiscal.
- Integração com gateways de pagamento.
- Integração com WhatsApp.
- Integração com equipamentos automotivos.
- Treinamento de modelos complexos de machine learning.
- Multiempresa/multifilial.
