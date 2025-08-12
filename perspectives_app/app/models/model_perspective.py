# Defines the SQLAlchemy ORM model for the 'perspectives' table.
#
from sqlalchemy import Column, Integer, String, JSON, DateTime, text
from sqlalchemy.sql import func
from ..database.database import Base

class Perspective(Base):
    """
    SQLAlchemy ORM model for the 'perspectives' table in the 'recsui' schema.
    This model maps to the data structure provided in the user's JSON.
    """
    __tablename__ = "perspectives"
    __table_args__ = {"schema": "recsui"}

    # id is the primary key and is auto-incremented
    id = Column(Integer, primary_key=True, index=True)

    # These fields are required and are validated to not be empty strings.
    username = Column(String, nullable=False)
    layout_name = Column(String, nullable=False)
    updated_by = Column(String, nullable=False)

    # These fields store JSON data. JSONB is used for efficient storage and querying.
    column_state = Column(JSON, nullable=False, default=text("'[]'::jsonb"))
    sort_model = Column(JSON, nullable=False, default=text("'[]'::jsonb"))
    filter_model = Column(JSON, nullable=False, default=text("'{}'::jsonb"))

    # updated_time is automatically populated with the current timestamp
    updated_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())