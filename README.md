# Barbearia V2

Aplicação Flask para gestão de uma barbearia, incluindo agendamentos, serviços, clientes e barbeiros.

## Estrutura do Projeto

```
barbearia_v2/
├── app/
│   ├── static/       # Arquivos estáticos (CSS, JS, imagens)
│   ├── templates/    # Templates HTML
│   └── app.py        # Aplicação Flask e modelos de dados
├── barbearia.db      # Banco de dados SQLite (será criado automaticamente)
└── requirements.txt  # Dependências do projeto
```

## Modelos de Dados

- **Servico**: Serviços oferecidos pela barbearia
- **Barbeiro**: Profissionais da barbearia
- **Cliente**: Clientes cadastrados
- **HorarioFuncionamento**: Horários de trabalho dos barbeiros
- **UsuarioAdmin**: Usuários administrativos do sistema
- **Agendamento**: Agendamentos de serviços

## Instalação

1. Clone o repositório:

```bash
git clone <url-do-repositorio>
cd barbearia_v2
```

2. Crie um ambiente virtual e ative-o:

```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Inicialize o banco de dados:

```bash
cd app
flask db init
flask db migrate -m "Criação inicial dos modelos"
flask db upgrade
```

5. Execute a aplicação:

```bash
flask run
```

A aplicação estará disponível em `http://127.0.0.1:5000/`.

## Funcionalidades

- Gestão de serviços oferecidos
- Cadastro e gestão de barbeiros
- Cadastro e gestão de clientes
- Configuração de horários de funcionamento
- Sistema de agendamentos
- Painel administrativo