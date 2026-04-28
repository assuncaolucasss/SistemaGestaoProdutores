import sys
sys.path.append(".")

from sqlmodel import Session
from app.models.base import engine
from app.models.usuario import Usuario, PapelUsuario
from app.core.security import hash_senha

with Session(engine) as session:
    admin = Usuario(
        nome="Administrador",
        email="admin@carajas.gov.br",
        senha_hash=hash_senha("senha_segura_aqui"),
        papel=PapelUsuario.superusuario
    )
    session.add(admin)
    session.commit()
    print("Superusuário criado com sucesso!")