
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)


async def enviar_email_recuperacao(email: str, codigo: str):
    mensagem = MessageSchema(
        subject="Recuperação de Senha — Sistema de Gestão de Assentamentos",
        recipients=[email],
        body=f"""
        <h2>Recuperação de Senha</h2>
        <p>Seu código de recuperação é:</p>
        <h1 style="letter-spacing: 8px; color: #2563eb;">{codigo}</h1>
        <p>Este código expira em <strong>15 minutos</strong>.</p>
        <p>Se você não solicitou a recuperação, ignore este email.</p>
        """,
        subtype="html",
    )
    fm = FastMail(conf)
    await fm.send_message(mensagem)
