from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class FigmaDataBase(BaseModel):
    file_key: str
    node_id: Optional[str] = None
    depth: Optional[int] = None

class FigmaDataCreate(FigmaDataBase):
    data: str # JSON string

class FigmaDataResponse(FigmaDataBase):
    id: int
    data: Any # Parsed JSON
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class SyncRequest(BaseModel):
    id: int
