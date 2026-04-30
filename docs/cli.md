# CLI de Gerenciamento

O GarageHub expõe comandos de gerenciamento via terminal, registrados como entry points do pacote. Após instalar o projeto com `pip install -e .`, os comandos ficam disponíveis globalmente no virtualenv.

---

## `create-superuser`

Cria o usuário root administrador do sistema. Equivalente ao `createsuperuser` do Django.

O usuário criado tem `is_admin = true` e `is_active = true`, o que garante acesso a todos os endpoints protegidos da API.

### Uso interativo (recomendado)

```bash
create-superuser
```

```
E-mail: admin@garagehub.com
Senha:
Confirme a senha:
Superusuário criado com sucesso.
  E-mail : admin@garagehub.com
  ID     : 3fa85f64-5717-4562-b3fc-2c963f66afa6
```

A senha é solicitada sem eco no terminal via `getpass`.

### Flags disponíveis

```bash
create-superuser --email admin@garagehub.com
# senha solicitada de forma segura no prompt
```

```bash
create-superuser --email admin@garagehub.com --password senha123
# não-interativo — útil em scripts de seed e ambientes de CI
```

!!! warning "Segurança"
    Passar `--password` em linha de comando deixa a senha visível no histórico do shell (`~/.bash_history`). Prefira o modo interativo em ambientes de produção.

### Opções

| Opção | Descrição |
|---|---|
| `--email EMAIL` | E-mail do superusuário. Se omitido, será solicitado interativamente. |
| `--password PASSWORD` | Senha em texto plano. Se omitida, será solicitada com confirmação. |

### Validações

- **E-mail único** — retorna erro se o e-mail já estiver cadastrado.
- **Senha mínima** — mínimo de 8 caracteres.
- **Confirmação de senha** — no modo interativo, a senha deve ser digitada duas vezes.

### Erros comuns

| Mensagem | Causa |
|---|---|
| `Erro: já existe um usuário com o e-mail '...'` | E-mail já cadastrado no banco |
| `Erro: a senha deve ter pelo menos 8 caracteres` | Senha muito curta |
| `As senhas não coincidem. Tente novamente.` | Confirmação de senha divergente (pede novamente) |

### Em Docker

```bash
docker compose exec app create-superuser --email admin@garagehub.com
# senha solicitada de forma segura no prompt
```

### Em ambiente de CI / seed

```bash
create-superuser --email "$ADMIN_EMAIL" --password "$ADMIN_PASSWORD"
```

Defina `ADMIN_EMAIL` e `ADMIN_PASSWORD` como variáveis de ambiente seguras na pipeline.
