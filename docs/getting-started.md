# Guia de Instalação

## Pré-requisitos

- Python 3.12+
- pip

## Instalação local

**1. Clone o repositório**

```bash
git clone <url-do-repositorio>
cd garagehub-backend
```

**2. Crie e ative o virtualenv**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**3. Instale as dependências**

```bash
# produção
pip install -e .

# desenvolvimento (inclui pytest, ruff, mkdocs)
pip install -e ".[dev]"
```

**4. Configure as variáveis de ambiente**

```bash
cp .env.example .env
```

Edite o `.env` conforme necessário. Veja a página de [Configuração](configuration.md) para detalhes.

**5. Inicie o servidor de desenvolvimento**

```bash
fastapi dev app/main.py
```

A API estará disponível em `http://localhost:8000`.

Com `APP_DEBUG=true` no `.env`, o Swagger estará em `http://localhost:8000/docs`.
