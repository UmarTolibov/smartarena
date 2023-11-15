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
        message = f"""Your verification link:
        http://localhost:8000/auth/verify/?e={user.email.replace('@', '%40')}&code={code}""" if email_var is True else \
            f"""Your link for resetting password:
        http://localhost:8000/auth/change-password/?user={user.id}&c={code}"""
    except AttributeError as e:
        raise HTTPException(status_code=404, detail=e)
    msg = EmailMessage()
    msg.set_content(message)
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
