import argparse
import asyncio
import getpass
import sys


async def _create_superuser(email: str, password: str) -> None:
    from sqlalchemy import select

    from app.core.database import AsyncSessionFactory
    from app.core.security import hash_password
    from app.models.user import CustomerType, User

    async with AsyncSessionFactory() as db:
        result = await db.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            print(f"Erro: já existe um usuário com o e-mail '{email}'.", file=sys.stderr)
            sys.exit(1)

        user = User(
            email=email,
            hashed_password=hash_password(password),
            is_admin=True,
            is_active=True,
            customer_type=CustomerType.pessoa_fisica,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    print(f"Superusuário criado com sucesso.")
    print(f"  E-mail : {user.email}")
    print(f"  ID     : {user.id}")


def create_superuser() -> None:
    parser = argparse.ArgumentParser(
        prog="create-superuser",
        description="Cria um superusuário administrador do GarageHub.",
    )
    parser.add_argument("--email", help="E-mail do superusuário")
    parser.add_argument(
        "--password",
        help="Senha em texto plano (evite em produção; prefira o prompt interativo)",
    )
    args = parser.parse_args()

    email = args.email or input("E-mail: ").strip()
    if not email:
        print("Erro: e-mail é obrigatório.", file=sys.stderr)
        sys.exit(1)

    if args.password:
        password = args.password
    else:
        while True:
            password = getpass.getpass("Senha: ")
            confirm = getpass.getpass("Confirme a senha: ")
            if password == confirm:
                break
            print("As senhas não coincidem. Tente novamente.")

    if len(password) < 8:
        print("Erro: a senha deve ter pelo menos 8 caracteres.", file=sys.stderr)
        sys.exit(1)

    asyncio.run(_create_superuser(email, password))
