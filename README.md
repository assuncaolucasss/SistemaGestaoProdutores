# Sistema de Gestão de Produtores

## Descrição

Este é um sistema completo de gestão para produtores agrícolas em Canaã dos Carajás, desenvolvido para facilitar o processo de inscrição, submissão e gerenciamento de fomentos (programas de incentivo) agrícolas. O sistema permite que produtores se cadastrem, preencham formulários dinâmicos, submetam propostas para diferentes modalidades de fomentos e acompanhem o status de suas submissões.

O projeto é dividido em duas partes principais:
- **Backend**: API REST desenvolvida com FastAPI em Python
- **Frontend**: Interface web desenvolvida com Vue.js 3 e Vite

## Funcionalidades Principais

### Gestão de Produtores
- Cadastro e atualização de dados pessoais dos produtores
- Importação de produtores via arquivo XLSX
- Validação de CPF e dados obrigatórios
- Gerenciamento de informações complementares (RG, telefone, email, etc.)

### Sistema de Fomentos
- Criação e configuração de programas de fomento
- Definição de modalidades com classes e subclasses
- Configuração de entidades responsáveis e técnicos
- Ativação/desativação de fomentos

### Formulários Dinâmicos
- Sistema de formulários configuráveis por fomento
- Campos dinâmicos com validações
- Suporte a diferentes tipos de campos (texto, número, data, seleção, etc.)
- Hierarquia de características para formulários complexos

### Submissões e Processos
- Submissão de propostas por produtores
- Vinculação automática a fomentos e modalidades
- Geração de números de processo
- Acompanhamento de status das submissões

### Autenticação e Autorização
- Sistema de login com JWT
- Recuperação de senha via email
- Diferentes níveis de permissão (superusuário, administrador, usuário comum)
- Controle de acesso baseado em papéis

### Relatórios e Exportação
- Geração de PDFs das submissões
- Exportação de dados em diferentes formatos
- Relatórios administrativos

## Tecnologias Utilizadas

### Backend
- **Python 3.8+**
- **FastAPI**: Framework web para APIs REST
- **SQLModel**: ORM baseado em SQLAlchemy e Pydantic
- **PostgreSQL**: Banco de dados relacional
- **Alembic**: Migrações de banco de dados
- **Pydantic**: Validação de dados
- **JWT**: Autenticação baseada em tokens
- **Gmail API**: Envio de emails

### Frontend
- **Vue.js 3**: Framework JavaScript progressivo
- **Vite**: Build tool e dev server
- **Pinia**: Gerenciamento de estado
- **Vue Router**: Roteamento para SPA
- **Tailwind CSS**: Framework CSS utilitário
- **Axios**: Cliente HTTP para APIs
- **Lucide Vue**: Ícones vetoriais
- **jsPDF & html2pdf.js**: Geração de PDFs
- **html2canvas**: Captura de screenshots

### Testes
- **Pytest**: Framework de testes para Python
- **Playwright**: Testes end-to-end para frontend
- **Vitest**: Framework de testes para Vue.js

## Pré-requisitos

- Python 3.8 ou superior
- Node.js 16 ou superior
- PostgreSQL 12 ou superior
- Git

## Instalação

### 1. Clonagem do Repositório

```bash
git clone https://github.com/assuncaolucasss/SistemaGestaoProdutores.git
cd SistemaGestaoProdutores
```

### 2. Configuração do Backend

```bash
cd backend

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 3. Configuração do Banco de Dados

Crie um banco de dados PostgreSQL e configure as variáveis de ambiente.

### 4. Configuração do Frontend

```bash
cd ../frontend

# Instalar dependências
npm install
```

## Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na pasta `backend` com as seguintes variáveis:

```env
DATABASE_URL=postgresql://usuario:senha@localhost:5432/nome_do_banco
SECRET_KEY=sua_chave_secreta_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

GMAIL_USER=seu-email@gmail.com
GMAIL_APP_PASSWORD=sua_senha_de_app
```

### Migrações do Banco de Dados

```bash
cd backend
alembic upgrade head
```

### Criação do Superusuário

```bash
python scripts/criar_superusuario.py
```

### Importação de Produtores (Opcional)

Se houver dados de produtores em XLSX:

```bash
python scripts/importar_produtores.py caminho/para/arquivo.xlsx
```

## Uso

### Executando o Backend

```bash
cd backend
uvicorn app.main:app --reload
```

A API estará disponível em `http://localhost:8000`

### Executando o Frontend

```bash
cd frontend
npm run dev
```

A aplicação estará disponível em `http://localhost:5173`

### Documentação da API

Acesse `http://localhost:8000/docs` para a documentação interativa da API gerada pelo Swagger.

## Estrutura do Projeto

```
.
├── backend/
│   ├── app/
│   │   ├── main.py                 # Ponto de entrada da API
│   │   ├── api/routes/             # Rotas da API
│   │   ├── core/                   # Configurações e utilitários
│   │   ├── db/                     # Conexão com banco de dados
│   │   ├── models/                 # Modelos de dados SQLModel
│   │   ├── schemas/                # Schemas Pydantic
│   │   └── services/               # Serviços (email, etc.)
│   ├── scripts/                    # Scripts utilitários
│   ├── tests/                      # Testes do backend
│   └── requirements.txt            # Dependências Python
├── frontend/
│   ├── src/
│   │   ├── components/             # Componentes Vue
│   │   ├── views/                  # Páginas da aplicação
│   │   ├── router/                 # Configuração de rotas
│   │   ├── stores/                 # Stores Pinia
│   │   └── services/               # Serviços (API calls)
│   ├── public/                     # Assets estáticos
│   └── package.json                # Dependências Node.js
└── testes_formulario/               # Testes específicos do formulário
```

## API Endpoints Principais

### Autenticação
- `POST /auth/login` - Login de usuário
- `POST /auth/recuperar-senha` - Solicitar recuperação de senha
- `POST /auth/verificar-codigo` - Verificar código de recuperação
- `POST /auth/nova-senha` - Definir nova senha

### Produtores
- `GET /produtores` - Listar produtores
- `POST /produtores` - Criar produtor
- `GET /produtores/{id}` - Detalhes do produtor
- `PUT /produtores/{id}` - Atualizar produtor

### Fomentos
- `GET /fomentos` - Listar fomentos ativos
- `POST /fomentos` - Criar fomento (admin)
- `GET /fomentos/{id}` - Detalhes do fomento

### Submissões
- `GET /submissoes` - Listar submissões
- `POST /submissoes` - Criar submissão
- `GET /submissoes/{id}` - Detalhes da submissão
- `PUT /submissoes/{id}` - Atualizar submissão

### Formulários
- `GET /formulario/{fomento_id}` - Obter estrutura do formulário
- `POST /formulario/submeter` - Submeter formulário preenchido

### Usuários (Admin)
- `GET /usuarios` - Listar usuários
- `POST /usuarios` - Criar usuário
- `PUT /usuarios/{id}` - Atualizar usuário

## Testes

### Backend

```bash
cd backend
pytest
```

### Frontend

```bash
cd frontend
npm run test
```

### Testes E2E

```bash
cd testes_formulario
npx playwright test
```

## Desenvolvimento

### Convenções de Código

- Backend: Seguir PEP 8 para Python
- Frontend: Seguir Vue.js Style Guide
- Commits: Usar conventional commits

### Branches

- `main`: Código de produção
- `develop`: Desenvolvimento ativo
- `feature/*`: Novas funcionalidades

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## Licença

Este projeto é proprietário - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Suporte

Para suporte, entre em contato com a equipe de desenvolvimento ou abra uma issue no repositório.

## Changelog

### v1.0.0
- Lançamento inicial
- Funcionalidades básicas de gestão de produtores e fomentos
- Sistema de autenticação
- Formulários dinâmicos
- Geração de PDFs
