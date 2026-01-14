import json
import logging
import os
import sys
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import FigmaData
from app.services.figma import FigmaService, process_figma_response

logger = logging.getLogger(__name__)

def get_figma_data_tool(
    db: Session,
    token: str,
    file_key: str,
    node_id: str = None,
    depth: int = None,
    force_refresh: bool = False,
):
    """
    获取 Figma 数据。
    优先查库，若无则调用 Figma API 并缓存。
    """
    # Check cache
    query = db.query(FigmaData).filter(FigmaData.file_key == file_key)
    if node_id:
        query = query.filter(FigmaData.node_id == node_id)
    else:
        query = query.filter(FigmaData.node_id.is_(None))
    
    cached_item = query.first()
    if cached_item and not force_refresh:
        print(
            f"\n{'='*50}\n[Figma MCP] 命中本地缓存 (Cache HIT)\nFile Key: {file_key}\nNode ID: {node_id}\n{'='*50}\n",
            file=sys.stderr,
        )
        logger.info(f"Cache hit for {file_key} {node_id}")
        return json.loads(cached_item.data)

    # Cache miss 或强制刷新
    if cached_item and force_refresh:
        print(
            f"\n{'='*50}\n[Figma MCP] 强制刷新缓存 (Force Refresh)\nFile Key: {file_key}\nNode ID: {node_id}\n{'='*50}\n",
            file=sys.stderr,
        )
        logger.info(f"Cache force refresh for {file_key} {node_id}")
    else:
        print(
            f"\n{'='*50}\n[Figma MCP] 未命中缓存，调用远程 API (Cache MISS)\nFile Key: {file_key}\nNode ID: {node_id}\n{'='*50}\n",
            file=sys.stderr,
        )
        logger.info(f"Cache miss for {file_key} {node_id}")
    service = FigmaService(token)
    
    try:
        if node_id:
            # node_id format 1:2,3:4
            raw_data = service.get_file_nodes(file_key, node_id, depth)
        else:
            raw_data = service.get_file(file_key, depth)
            
        # Process
        processed_data = process_figma_response(raw_data, depth)
        
        # Save to DB
        # Check if exists again (race condition) or use upsert logic if needed, but simple add is fine for now
        # Actually better to check if we should update an old record?
        # For now, just create new. The frontend has "delete" feature.
        # Or better: if exists update, else insert.
        
        meta = processed_data.get("metadata", {}) if isinstance(processed_data, dict) else {}
        name = meta.get("name")
        last_modified_str = meta.get("lastModified")
        last_modified_dt = None
        if isinstance(last_modified_str, str):
            try:
                # Example: 2026-01-14T05:57:11Z
                last_modified_dt = datetime.strptime(last_modified_str, "%Y-%m-%dT%H:%M:%SZ")
            except Exception:
                last_modified_dt = None
        if cached_item:
            cached_item.data = json.dumps(processed_data)
            cached_item.depth = depth
            cached_item.name = name
            cached_item.last_modified = last_modified_dt
        else:
            new_cache = FigmaData(
                file_key=file_key,
                node_id=node_id,
                depth=depth,
                name=name,
                last_modified=last_modified_dt,
                data=json.dumps(processed_data)
            )
            db.add(new_cache)
        
        db.commit()
        
        return processed_data
    except Exception as e:
        logger.error(f"Error fetching figma data: {e}")
        raise e

def download_figma_images_tool(
    token: str,
    file_key: str,
    nodes: list, 
    local_path: str,
    png_scale: float = 2.0
):
    """
    下载 Figma 图片。
    支持 node renders 和 image fills。
    """
    service = FigmaService(token)
    
    results = []
    
    # 1. Handle Node Renders (nodeId)
    render_nodes = [n for n in nodes if 'nodeId' in n and not n.get('imageRef')]
    if render_nodes:
        # Separate PNG and SVG
        png_nodes = [n for n in render_nodes if not n.get('fileName', '').endswith('.svg')]
        svg_nodes = [n for n in render_nodes if n.get('fileName', '').endswith('.svg')]
        
        # Process PNGs
        if png_nodes:
            ids = [n['nodeId'] for n in png_nodes]
            try:
                urls = service.get_node_render_urls(file_key, ",".join(ids), format='png', scale=png_scale)
                for node in png_nodes:
                    node_id = node['nodeId']
                    file_name = node['fileName']
                    if node_id in urls:
                        full_path = os.path.join(local_path, file_name)
                        service.download_image(urls[node_id], full_path)
                        results.append(f"Downloaded PNG: {file_name}")
                    else:
                        results.append(f"Failed to get URL for {node_id}")
            except Exception as e:
                results.append(f"Error downloading PNGs: {e}")

        # Process SVGs
        if svg_nodes:
            ids = [n['nodeId'] for n in svg_nodes]
            try:
                urls = service.get_node_render_urls(file_key, ",".join(ids), format='svg')
                for node in svg_nodes:
                    node_id = node['nodeId']
                    file_name = node['fileName']
                    if node_id in urls:
                        full_path = os.path.join(local_path, file_name)
                        service.download_image(urls[node_id], full_path)
                        results.append(f"Downloaded SVG: {file_name}")
                    else:
                        results.append(f"Failed to get URL for {node_id}")
            except Exception as e:
                results.append(f"Error downloading SVGs: {e}")

    # 2. Handle Image Fills (imageRef)
    fill_nodes = [n for n in nodes if 'imageRef' in n]
    if fill_nodes:
        try:
            fill_urls = service.get_image_fills(file_key)
            for node in fill_nodes:
                image_ref = node['imageRef']
                file_name = node['fileName']
                if image_ref in fill_urls:
                    full_path = os.path.join(local_path, file_name)
                    service.download_image(fill_urls[image_ref], full_path)
                    results.append(f"Downloaded Image Fill: {file_name}")
                else:
                    results.append(f"Image Ref not found: {image_ref}")
        except Exception as e:
            results.append(f"Error downloading Image Fills: {e}")

    return "\n".join(results)
