from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from jinja2 import Environment, FileSystemLoader
import os


conf = ConnectionConfig(
    MAIL_USERNAME = "info@ecogis.tech",
    MAIL_PASSWORD = "*NH}F9I3RnGW",
    MAIL_FROM = "info@ecogis.tech",
    MAIL_PORT = 465,
    MAIL_SERVER = "ecogis.tech",
    # MAIL_TLS = False,
    # MAIL_SSL = True,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS = True,
    TEMPLATE_FOLDER = os.path.join(os.path.dirname(__file__), "templates"),
)

env = Environment(loader=FileSystemLoader(conf.TEMPLATE_FOLDER))

async def register_email(email: str, staff_id: str, temp_password: str):
    template = env.get_template("register.html")
    html_body = template.render(staff_id=staff_id, temp_password=temp_password)

    message = MessageSchema(
        subject="Your Guard Account Created",
        recipients=[email],
        body=html_body,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)
