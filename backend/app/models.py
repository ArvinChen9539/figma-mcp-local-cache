from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.sql import func
from .database import Base

class FigmaData(Base):
    __tablename__ = "figma_data"

    id = Column(Integer, primary_key=True, index=True)
    file_key = Column(String(255), nullable=False, index=True, comment="Figma 文件 Key")
    node_id = Column(String(255), nullable=True, index=True, comment="Figma 节点 ID")
    name = Column(String(255), nullable=True, index=True, comment="Figma 文件名称")
    depth = Column(Integer, nullable=True, default=None, comment="遍历深度")
    last_modified = Column(TIMESTAMP, nullable=True, comment="Figma 文件最后更新时间")
    data = Column(LONGTEXT, nullable=True, comment="缓存的 JSON 数据")
    created_at = Column(TIMESTAMP, server_default=func.now(), comment="创建时间")
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), comment="更新时间")
