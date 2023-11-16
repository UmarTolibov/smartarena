import random
from email.message import EmailMessage

import aiosmtplib
from fastapi.exceptions import HTTPException
from sqlalchemy.sql import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import Session, engine, Config, Base


async def send_email(user, email_var: bool = True):
    code = random.randint(100000, 999999)
    sender_email = "tolibovumar13@gmail.com"
    password = "rkxubwzmmbefmijf"
    try:
        if email_var:
            message = f"""
            <html>
            <head>
                <style>
                    body {{
                        font-family: 'Arial', sans-serif;
                        background-color: #f4f4f4;
                        margin: 0;
                        padding: 20px;
                    }}
                    .container {{
                        background-color: #fff;
                        border-radius: 8px;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                        padding: 20px;
                    }}
                    h1 {{
                        color: #333;
                    }}
                    p {{
                        color: #666;
                        margin-bottom: 15px;
                    }}
                    a {{
                        color: #007bff;
                        text-decoration: none;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>SmartArena Account Verification</h1>
                    <p>Thank you for registering with SmartArena! To verify your email and activate your account, please click on the following link:</p>
                    <p><a href="https://smartarena-bbff190dd374.herokuapp.com/auth/verify/?e={user.email.replace('@', '%40')}&code={code}">Verification Link</a></p>
                    <p>If you did not register with SmartArena, please ignore this email.</p>
                    <p>Best regards,<br>The SmartArena Team</p>
                </div>
            </body>
            </html>
            """
        else:
            message = f"""
            <html>
            <head>
                <style>
                    body {{
                        font-family: 'Arial', sans-serif;
                        background-color: #f4f4f4;
                        margin: 0;
                        padding: 20px;
                    }}
                    .container {{
                        background-color: #fff;
                        border-radius: 8px;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                        padding: 20px;
                    }}
                    h1 {{
                        color: #333;
                    }}
                    p {{
                        color: #666;
                        margin-bottom: 15px;
                    }}
                    a {{
                        color: #007bff;
                        text-decoration: none;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>SmartArena Password Reset</h1>
                    <p>We received a request to reset the password for your SmartArena account. If you did not make this request, please disregard this email.</p>
                    <p>To reset your password, click on the following link:</p>
                    <p><a href="https://smartarena-bbff190dd374.herokuapp.com/auth/change-password/?user={user.id}&c={code}">Reset Password Link</a></p>
                    <p>This link will expire after a certain period for security reasons.</p>
                    <p>Best regards,<br>The SmartArena Team</p>
                </div>
            </body>
            </html>
            """
    except AttributeError as e:
        raise HTTPException(status_code=404, detail=e)
    msg = EmailMessage()
    msg.add_alternative(message, subtype='html')
    msg['Subject'] = 'Email Verification'
    msg['From'] = sender_email
    msg['To'] = user.email

    try:
        smtp = aiosmtplib.SMTP(hostname="smtp.gmail.com", port=587)
        await smtp.connect()
        await smtp.login(sender_email, password)
        await smtp.send_message(msg)
        await smtp.quit()
        return code
    except Exception as e:
        print(f"Error sending email: {e}")
        return None


async def get_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # db = Session()

    async with AsyncSession(engine) as session:
        try:
            yield session
        finally:
            await session.close()


async def update_config_value(key, value):
    async with Session() as session:
        async with session.begin():
            # Retrieve the config row
            config = await session.execute(select(Config).where(Config.key == key))
            row = config.scalars().first()

            # Update the value of the config row
            if row:
                row.value = value


async def get_jwt_key():
    async with Session() as session:
        async with session.begin():
            q = select(Config).where(Config.key == "jwt_secret_key")
            result = await session.execute(q)
            print(result)
            return result
