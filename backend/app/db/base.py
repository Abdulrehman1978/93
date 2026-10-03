"""Canonical SQLAlchemy Declarative Base & Metadata Naming Convention.

Enforces deterministic constraint naming across PostgreSQL migrations and prevents
unnamed constraints in Alembic schema reflections.
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Standard naming conventions for constraints to ensure deterministic migration generation
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=naming_convention)


class Base(DeclarativeBase):
    """Authoritative SQLAlchemy Declarative Base for SAMBAL Core Domain."""

    metadata = metadata
