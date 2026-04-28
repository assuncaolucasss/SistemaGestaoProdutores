import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

def enviar_email_recuperacao(destinatario: str, codigo: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Código de Recuperação de Acesso"
    msg["From"] = settings.GMAIL_USER
    msg["To"] = destinatario

    corpo = f"""
    <html><body>
      <div style="font-family: sans-serif; max-width: 400px; margin: auto; padding: 24px; border: 1px solid #e5e7eb; border-radius: 12px;">
        <h2 style="color: #16a34a;">Recuperação de Acesso</h2>
        <p>Seu código de verificação é:</p>
        <div style="font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #16a34a; margin: 16px 0;">
          {codigo}
        </div>
        <p style="color: #6b7280; font-size: 13px;">Este código expira em <strong>5 minutos</strong>.</p>
        <p style="color: #6b7280; font-size: 13px;">Se você não solicitou isso, ignore este e-mail.</p>
      </div>
    </body></html>
    """

    msg.attach(MIMEText(corpo, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(settings.GMAIL_USER, settings.GMAIL_APP_PASSWORD)
        smtp.sendmail(settings.GMAIL_USER, destinatario, msg.as_string())