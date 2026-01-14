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

from app.services.mcp_tools import get_figma_data_tool, download_figma_images_tool
from app.repository import FileSystemRepository, MySQLRepository

load_dotenv()

mcp = FastMCP("Figma MCP Cache")

def get_repo_and_session():
    """
    Determine which repository to use based on environment variables.
    Returns (repo, db_session). db_session is None if not using DB.
    """
    # 1. External File Persistence
    data_folder = os.getenv("FIGMA_FILE_DATA_FOLDER")
    if data_folder:
        return FileSystemRepository(data_folder), None
    
    # 2. MySQL Configuration (Check if explicitly configured)
    # We check for DB_HOST or DB_PASSWORD to decide if we should use MySQL.
    # Default behavior in database.py is localhost/root/no-pass, so if user relies on that,
    # they might need to ensure DB_HOST is set or we fallback to file.
    # Given the requirement "No config -> internal cache", we assume MySQL usage implies explicit config.
    if os.getenv("DB_HOST") or os.getenv("DB_PASSWORD"):
        try:
            from app.database import SessionLocal
            db = SessionLocal()
            return MySQLRepository(db), db
        except Exception as e:
            logging.error(f"Failed to connect to MySQL: {e}. Falling back to internal cache.")
    
    # 3. Internal Cache (Default)
    internal_cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_cache")
    return FileSystemRepository(internal_cache_path), None

@mcp.tool()
def get_figma_data(file_key: str, node_id: str = None, depth: int = None) -> str:
    """
    Get comprehensive Figma file data including layout, content, visuals, and component information.
    """
    token = os.getenv("FIGMA_ACCESS_TOKEN")
    if not token:
        return "Error: FIGMA_ACCESS_TOKEN not set"
    
    repo, db_session = get_repo_and_session()
    
    try:
        data = get_figma_data_tool(repo, token, file_key, node_id, depth)
        return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        if db_session:
            db_session.close()

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
