from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
from datetime import datetime
import json
import os
import re
from sqlalchemy.orm import Session
from app.models import FigmaData

class FigmaDataRepository(ABC):
    @abstractmethod
    def get_data(self, file_key: str, node_id: Optional[str] = None) -> Optional[Any]:
        """
        Get cached data. Returns the full data object (including metadata if possible, 
        but the main requirement is the 'data' field content).
        For simplicity, let's return the FigmaData-like object or dict that has a .data attribute or key.
        """
        pass

    @abstractmethod
    def save_data(self, file_key: str, node_id: Optional[str], data: Any, name: Optional[str], depth: Optional[int], last_modified: Optional[datetime]):
        """
        Save data to cache.
        """
        pass

class MySQLRepository(FigmaDataRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_data(self, file_key: str, node_id: Optional[str] = None) -> Optional[FigmaData]:
        query = self.db.query(FigmaData).filter(FigmaData.file_key == file_key)
        if node_id:
            query = query.filter(FigmaData.node_id == node_id)
        else:
            query = query.filter(FigmaData.node_id.is_(None))
        return query.first()

    def save_data(self, file_key: str, node_id: Optional[str], data: Any, name: Optional[str], depth: Optional[int], last_modified: Optional[datetime]):
        cached_item = self.get_data(file_key, node_id)
        
        json_data = json.dumps(data) if not isinstance(data, str) else data
        
        if cached_item:
            cached_item.data = json_data
            cached_item.depth = depth
            cached_item.name = name
            cached_item.last_modified = last_modified
        else:
            new_cache = FigmaData(
                file_key=file_key,
                node_id=node_id,
                depth=depth,
                name=name,
                last_modified=last_modified,
                data=json_data
            )
            self.db.add(new_cache)
        self.db.commit()

class FileSystemRepository(FigmaDataRepository):
    def __init__(self, data_folder: str):
        self.data_folder = data_folder
        os.makedirs(self.data_folder, exist_ok=True)

    def _get_filename(self, file_key: str, node_id: Optional[str]) -> str:
        # Sanitize node_id for filename
        safe_node_id = "ROOT"
        if node_id:
            # Replace characters invalid in filenames
            safe_node_id = re.sub(r'[<>:"/\\|?*]', '_', node_id)
        
        return os.path.join(self.data_folder, f"{file_key}__{safe_node_id}.json")

    def get_data(self, file_key: str, node_id: Optional[str] = None) -> Optional[Any]:
        filepath = self._get_filename(file_key, node_id)
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                file_content = json.load(f)
            
            # Convert to an object that mimics FigmaData for compatibility
            class FileDataWrapper:
                def __init__(self, d):
                    self.file_key = d.get('file_key')
                    self.node_id = d.get('node_id')
                    self.name = d.get('name')
                    self.depth = d.get('depth')
                    self.last_modified = d.get('last_modified') # This is likely a string in JSON
                    self.data = d.get('data') # This is the JSON string of figma data
                    
                    # Convert last_modified back to datetime if needed, 
                    # but the consumer might expect it. 
                    # For consistency with SQLAlchemy model which returns datetime object:
                    if self.last_modified and isinstance(self.last_modified, str):
                        try:
                            self.last_modified = datetime.fromisoformat(self.last_modified)
                        except:
                            pass

            return FileDataWrapper(file_content)
        except Exception as e:
            print(f"Error reading cache file {filepath}: {e}")
            return None

    def save_data(self, file_key: str, node_id: Optional[str], data: Any, name: Optional[str], depth: Optional[int], last_modified: Optional[datetime]):
        filepath = self._get_filename(file_key, node_id)
        
        json_data = json.dumps(data) if not isinstance(data, str) else data
        
        file_content = {
            "file_key": file_key,
            "node_id": node_id,
            "name": name,
            "depth": depth,
            "last_modified": last_modified.isoformat() if last_modified else None,
            "data": json_data,
            "updated_at": datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(file_content, f, indent=2, ensure_ascii=False)
