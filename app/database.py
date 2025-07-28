from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker, declarative_base

# from config import settings

# # Use the correct async engine
# engine = create_async_engine(settings.DATABASE_URL, echo=True)

# # Create a session factory
# AsyncSessionLocal = sessionmaker(
#     bind=engine,
#     class_=AsyncSession,
#     expire_on_commit=False,
#     autoflush=False,
#     autocommit=False
# )

# Base = declarative_base()

# # Dependency for getting DB session
# async def get_db():
#     async with AsyncSessionLocal() as session:
#         yield session
