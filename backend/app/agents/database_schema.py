"""Pydantic schema for database blueprint generation."""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class DatabaseColumn(BaseModel):
    """Specification of a database table column."""

    name: str = Field(..., description="Column name")
    data_type: str = Field(..., description="Data type (Integer, String, Float, Boolean, DateTime)")
    primary_key: bool = Field(default=False, description="Whether this column is the primary key")
    nullable: bool = Field(default=True, description="Whether NULL is allowed")
    unique: bool = Field(default=False, description="Whether unique constraint is applied")
    default: str | None = Field(default=None, description="Default value if any")


class DatabaseTable(BaseModel):
    """Specification of a relational database table."""

    name: str = Field(..., description="Table name")
    model_name: str = Field(..., description="SQLAlchemy model class name")
    columns: list[DatabaseColumn] = Field(default_factory=list, description="Column definitions")
    foreign_keys: list[str] = Field(default_factory=list, description="Foreign key relationships")


class DatabaseBlueprint(BaseModel):
    """Structured database blueprint for a generated web application."""

    database_type: str = Field(..., description="Database system type (PostgreSQL / SQLite)")
    tables: list[str] = Field(default_factory=list, description="Database tables to be created")
    relationships: list[str] = Field(default_factory=list, description="Table relationships")
    indexes: list[str] = Field(default_factory=list, description="Database indexes")
    language: str = Field(default="en", description="Output language for schema metadata")

    entities: list[str] = Field(default_factory=list, description="Core domain entity names")
    table_details: list[DatabaseTable] = Field(default_factory=list, description="Detailed table column definitions")
    seed_records: list[str] = Field(default_factory=list, description="Initial seed data entities")
