import asyncio

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import AsyncAdaptedQueuePool
from sqlalchemy import event

from .models import AvailableHour, Order

pg = "postgresql+asyncpg://postgres:getout04@localhost:5432/postgres"
slite = {"url": "sqlite+aiosqlite:///database/db.sqlite3", "connect_args": {"check_same_thread": False}}
mysql = "mysql+aiomysql://sql:$Money04@localhost/smartarena"
engine = create_async_engine(pg, poolclass=AsyncAdaptedQueuePool)
Session = async_sessionmaker(engine)


@event.listens_for(Order, "after_insert")
def create_available_hours_for_order(mapper, session, target):
    if target.start_time is not None and target.hour is not None:
        available_hour = AvailableHour(
            available_hour_start=target.start_time,
            available_hour_end=target.end_time,
            stadium=target.stadium
        )
        try:
            session.execute(available_hour.__table__.insert().values({
                "available_hour_start": target.start_time,
                "available_hour_end": target.end_time,
                "stadium_id": target.stadium_id
            }))
        except Exception as e:
            print(e)
