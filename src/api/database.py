from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from src.utils.config import settings
from src.utils.logger import logger

engine = create_async_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Alert(Base):
    __tablename__ = "alerts"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    timestamp      = Column(DateTime, default=datetime.utcnow, index=True)
    attack_type    = Column(String(64), nullable=False)
    severity_score = Column(Integer, nullable=False)
    severity_label = Column(String(16), nullable=False)
    confidence     = Column(Float, nullable=False)
    is_attack      = Column(Boolean, default=True)
    source_ip      = Column(String(45), nullable=True)
    dest_ip        = Column(String(45), nullable=True)
    is_acknowledged = Column(Boolean, default=False)
    raw_result     = Column(Text, nullable=True)


class AnalysisLog(Base):
    __tablename__ = "analysis_log"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    timestamp   = Column(DateTime, default=datetime.utcnow, index=True)
    is_attack   = Column(Boolean, nullable=False)
    attack_type = Column(String(64), nullable=False)
    confidence  = Column(Float, nullable=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialised")


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session