from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import FigmaData
from app.schemas import FigmaDataResponse
from app.services.mcp_tools import get_figma_data_tool
from app.repository import MySQLRepository
import os
import json

router = APIRouter(prefix="/api", tags=["api"])

@router.get("/cache")
def list_cache(
    skip: int = 0,
    limit: int = 10,
    search: str = None,
    created_from: str = None,
    created_to: str = None,
    db: Session = Depends(get_db),
):
    query = db.query(FigmaData)
    if search:
        query = query.filter(
            (FigmaData.file_key.contains(search))
            | (FigmaData.node_id.contains(search))
            | (FigmaData.name.contains(search))
        )

    # 记录时间范围过滤（按 updated_at）
    from datetime import datetime

    def _parse_dt(value: str):
        try:
            # 兼容 'YYYY-MM-DD' 或 ISO 字符串
            v = value.strip()
            if "T" in v:
                # 去掉毫秒和时区部分
                v = v.split(".")[0].replace("Z", "")
            return datetime.fromisoformat(v)
        except Exception:
            return None

    if created_from:
        dt_from = _parse_dt(created_from)
        if dt_from:
            query = query.filter(FigmaData.updated_at >= dt_from)

    if created_to:
        dt_to = _parse_dt(created_to)
        if dt_to:
            query = query.filter(FigmaData.updated_at <= dt_to)
    
    total = query.count()
    items = (
        query.order_by(FigmaData.updated_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    # Transform items to include parsed data or summary
    result_items = []
    for item in items:
        result_items.append({
            "id": item.id,
            "file_key": item.file_key,
            "node_id": item.node_id,
            "depth": item.depth,
            "name": item.name,
            "last_modified": item.last_modified,
            "created_at": item.created_at,
            "updated_at": item.updated_at,
            # "data": json.loads(item.data) if item.data else None # Exclude heavy data for list view
        })
    
    return {
        "total": total,
        "items": result_items
    }

@router.delete("/cache/{id}")
def delete_cache(id: int, db: Session = Depends(get_db)):
    item = db.query(FigmaData).filter(FigmaData.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"message": "Deleted successfully"}

@router.post("/sync/{id}")
def sync_cache(id: int, db: Session = Depends(get_db)):
    item = db.query(FigmaData).filter(FigmaData.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    token = os.getenv("FIGMA_ACCESS_TOKEN")
    if not token:
        raise HTTPException(status_code=500, detail="FIGMA_ACCESS_TOKEN not set")
        
    try:
        repo = MySQLRepository(db)
        get_figma_data_tool(
            repo=repo,
            token=token,
            file_key=item.file_key,
            node_id=item.node_id,
            depth=item.depth,
            force_refresh=True,
        )
        return {"message": "Synced successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cache/{id}")
def get_cache_detail(id: int, db: Session = Depends(get_db)):
    item = db.query(FigmaData).filter(FigmaData.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return {
        "id": item.id,
        "file_key": item.file_key,
        "node_id": item.node_id,
        "depth": item.depth,
        "name": item.name,
        "last_modified": item.last_modified,
        "updated_at": item.updated_at,
        "data": json.loads(item.data) if item.data else None
    }
