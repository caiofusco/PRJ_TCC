# Oficina AI MVP

MVP de um sistema web para serviços automotivos integrado com um módulo de inteligência artificial para sugestão de agendamentos, priorização operacional e apoio à alocação de técnicos.

O projeto foi construído a partir do artigo **"Otimização de Processos em Serviços Automotivos através de um Sistema Web Integrado com Inteligência Artificial"**, contemplando os módulos de cadastro, veículos, agendamentos, ordens de serviço, execução, estoque, vendas, dashboard e IA.

## Stack técnica

- **Python 3.11+**
- **Flask** como framework web
- **SQLAlchemy** como ORM
- **MySQL 8** como banco relacional
- **PyMySQL** como driver MySQL
- **HTML, CSS e JavaScript** no front-end
- **Docker Compose** para subir aplicação + banco
- **Módulo de IA heurístico-preditivo** para prever duração de serviço, evitar conflitos e sugerir melhor técnico/horário

## Principais funcionalidades

- Login com perfis: administrador, atendente e técnico.
- Dashboard operacional com indicadores, próximos agendamentos, ordens abertas e alertas de estoque.
- Cadastro de clientes e veículos vinculados.
- Cadastro de serviços com preço base e tempo estimado.
- Gestão de usuários/técnicos, incluindo especialidades.
- Agendamento com verificação de conflitos.
- Sugestão inteligente de agenda por IA.
- Criação e acompanhamento de ordens de serviço.
- Controle de estoque com movimentações.
- Venda de produtos vinculada ou não a uma ordem de serviço.
- API JSON para integração futura com aplicativo móvel, WhatsApp ou painéis externos.

## Como rodar com Docker

1. Copie o arquivo de ambiente:

```bash
cp .env.example .env
```

2. Suba o ambiente:

```bash
docker compose up --build
```

3. Acesse:

```text
http://localhost:5000
```

4. Credenciais iniciais:

```text
E-mail: admin@oficina.local
Senha: admin123
```

O comando de inicialização cria as tabelas e insere dados de demonstração automaticamente.

## Como rodar sem Docker

1. Crie um banco MySQL:

```sql
CREATE DATABASE oficina_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'oficina_user'@'localhost' IDENTIFIED BY 'oficina_pass';
GRANT ALL PRIVILEGES ON oficina_ai.* TO 'oficina_user'@'localhost';
FLUSH PRIVILEGES;
```

2. Crie o ambiente Python:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Configure a conexão:

```bash
cp .env.example .env
export DATABASE_URL="mysql+pymysql://oficina_user:oficina_pass@localhost:3306/oficina_ai"
export SECRET_KEY="troque-esta-chave"
```

4. Inicialize o banco e execute:

```bash
flask --app run.py init-db
flask --app run.py run --host 0.0.0.0 --port 5000
```

## Módulo de IA do MVP

O MVP não depende de serviços externos de IA. O arquivo `app/ai_scheduler.py` implementa uma camada inteligente baseada em dados históricos:

- calcula a duração prevista do serviço com base em ordens concluídas;
- usa o tempo estimado do cadastro quando ainda não há histórico suficiente;
- verifica conflitos de agenda por técnico;
- pontua técnicos por especialidade, carga de trabalho e disponibilidade;
- retorna as melhores opções de horário, técnico, duração prevista e justificativa.

Essa abordagem é adequada para MVP porque funciona com poucos dados, é auditável, não exige custo de API e prepara a base para evolução futura com modelos de machine learning.

## Estrutura do projeto

```text
oficina_ai_mvp/
├── app/
│   ├── routes/
│   ├── static/
│   ├── templates/
│   ├── ai_scheduler.py
│   ├── config.py
│   ├── extensions.py
│   └── models.py
├── db/
│   ├── schema.sql
│   └── seed.sql
├── docs/
│   ├── ANALISE_COMPLETA_ARTIGO.md
│   ├── API.md
│   ├── DER.md
│   └── REQUISITOS_MVP.md
├── scripts/
│   └── wait_for_db.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── run.py
```

## Próximas evoluções recomendadas

- Validação em ambiente real com dados da oficina.
- Notificações automáticas por WhatsApp/e-mail.
- Aplicativo móvel para técnicos.
- Treinamento de modelo de ML com histórico real.
- Relatórios financeiros e de produtividade.
- Integração com emissão fiscal, pagamentos e IoT automotivo.
