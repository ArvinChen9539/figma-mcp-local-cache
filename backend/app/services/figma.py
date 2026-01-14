import requests
import json
from typing import Optional, Dict, Any, List
import os

class FigmaService:
    def __init__(self, token: str):
        self.base_url = "https://api.figma.com/v1"
        self.headers = {"X-Figma-Token": token}

    def get_file(self, file_key: str, depth: Optional[int] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/files/{file_key}"
        params = {}
        if depth:
            params["depth"] = depth
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_file_nodes(self, file_key: str, node_ids: str, depth: Optional[int] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/files/{file_key}/nodes"
        params = {"ids": node_ids}
        if depth:
            params["depth"] = depth
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_image_fills(self, file_key: str) -> Dict[str, str]:
        url = f"{self.base_url}/files/{file_key}/images"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json().get("meta", {}).get("images", {})

    def get_node_render_urls(self, file_key: str, node_ids: str, format: str = "png", scale: float = 2.0) -> Dict[str, str]:
        url = f"{self.base_url}/images/{file_key}"
        params = {
            "ids": node_ids,
            "format": format,
            "scale": scale
        }
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json().get("images", {})
    
    def download_image(self, url: str, save_path: str):
        response = requests.get(url, stream=True)
        response.raise_for_status()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

def simplify_figma_node(node: Dict[str, Any], depth: int = 0, max_depth: Optional[int] = None) -> Optional[Dict[str, Any]]:
    if max_depth is not None and depth > max_depth:
        return None
    
    if not node.get("visible", True):
        return None

    # Basic metadata
    simple_node = {
        "id": node.get("id"),
        "name": node.get("name"),
        "type": node.get("type")
    }
    
    if node.get("type") == "VECTOR":
        simple_node["type"] = "IMAGE-SVG"

    # Layout & Geometry
    if "absoluteBoundingBox" in node:
        simple_node["absoluteBoundingBox"] = node["absoluteBoundingBox"]
    
    # Text
    if "characters" in node:
        simple_node["characters"] = node["characters"]
        if "style" in node:
            simple_node["style"] = node["style"]

    # Fills (simplified)
    if "fills" in node:
        simple_node["fills"] = node["fills"]
    
    # Component info
    if "componentId" in node:
        simple_node["componentId"] = node["componentId"]

    # Children
    if "children" in node:
        children = []
        for child in node["children"]:
            simplified_child = simplify_figma_node(child, depth + 1, max_depth)
            if simplified_child:
                children.append(simplified_child)
        if children:
            simple_node["children"] = children

    return simple_node

def process_figma_response(data: Dict[str, Any], max_depth: Optional[int] = None) -> Dict[str, Any]:
    # Extract document or nodes
    result = {
        "metadata": {
            "name": data.get("name"),
            "lastModified": data.get("lastModified"),
            "thumbnailUrl": data.get("thumbnailUrl"),
        },
        "nodes": [],
        "components": data.get("components", {}),
        "styles": data.get("styles", {}),
        "globalVars": {"styles": {}} # Placeholder for globalVars if we were to implement full extraction
    }

    if "document" in data:
        # GetFileResponse - usually document root
        root = data["document"]
        # We process the children of the document (Canvases/Pages)
        if "children" in root:
             for child in root["children"]:
                 simplified = simplify_figma_node(child, 0, max_depth)
                 if simplified:
                     result["nodes"].append(simplified)
    elif "nodes" in data:
        # GetFileNodesResponse
        for node_id, node_data in data["nodes"].items():
            if "document" in node_data:
                simplified_node = simplify_figma_node(node_data["document"], 0, max_depth)
                if simplified_node:
                    result["nodes"].append(simplified_node)
    
    return result
