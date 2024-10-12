from pydantic import BaseModel

# Pydantic model for table creation
class TableCreate(BaseModel):
    name: str
    database_id: int

    class Config:
        orm_mode = True  # This allows Pydantic to work with SQLAlchemy models

class DependencyCreate(BaseModel):
    source_table_id: int
    target_table_id: int