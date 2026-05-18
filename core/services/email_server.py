from fastapi_mail import FastMail, config, MessageSchema


def message_config():

    return config.ConnectionConfig(
        MAIL_USERNAME="kwendacorp@gmail.com",
        MAIL_PASSWORD="ivbb barm kwio turk",
        MAIL_FROM="kwendacorp@gmail.com",
        MAIL_PORT=587,
        MAIL_FROM_NAME="Kwenda Tech",
        MAIL_SERVER="smtp.gmail.com",
        MAIL_SSL_TLS=False,
        MAIL_STARTTLS=True,
        USE_CREDENTIALS=True,
    )


async def send_email(body: str, subject: str, email: str):
    message = MessageSchema(
        subject=subject, body=body, recipients=[email], subtype="html"
    )

    fm = FastMail(message_config())

    await fm.send_message(message=message)
    print("Message Sender")
