from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.

    All models must inherit from this Base so that Alembic can discover
    them via Base.metadata. Import all models in app/db/models.py to
    ensure they are registered before metadata operations.
    """
