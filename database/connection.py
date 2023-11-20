from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import AsyncAdaptedQueuePool

pg = "postgresql+asyncpg://<db_username>:<db_secret>@<db_host>:<db_port>/<db_name>"
slite = "sqlite+aiosqlite:///database/db.sqlite3"

engine = create_async_engine(slite, connect_args={"check_same_thread": False}, poolclass=AsyncAdaptedQueuePool)
Session = async_sessionmaker(engine)
