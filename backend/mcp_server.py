from mcp.server.fastmcp import FastMCP
import os
import sys
import json
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)

# Ensure app can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.services.mcp_tools import get_figma_data_tool, download_figma_images_tool

load_dotenv()

mcp = FastMCP("Figma MCP Cache")

@mcp.tool()
def get_figma_data(file_key: str, node_id: str = None, depth: int = None) -> str:
    """
    Get comprehensive Figma file data including layout, content, visuals, and component information.
    """
    token = os.getenv("FIGMA_ACCESS_TOKEN")
    if not token:
        return "Error: FIGMA_ACCESS_TOKEN not set"
    
    db = SessionLocal()
    try:
        data = get_figma_data_tool(db, token, file_key, node_id, depth)
        return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        db.close()

@mcp.tool()
def download_figma_images(file_key: str, nodes: str, local_path: str, png_scale: float = 2.0) -> str:
    """
    Download SVG and PNG images used in a Figma file based on the IDs of image or icon nodes.
    nodes: JSON string of list of objects {nodeId, fileName, imageRef, ...}
    """
    token = os.getenv("FIGMA_ACCESS_TOKEN")
    if not token:
        return "Error: FIGMA_ACCESS_TOKEN not set"
        
    try:
        parsed_nodes = nodes
        if isinstance(nodes, str):
            try:
                parsed_nodes = json.loads(nodes)
            except:
                pass # Try as object if passed by python SDK?
            
        return download_figma_images_tool(token, file_key, parsed_nodes, local_path, png_scale)
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()
