# Figma MCP Local Cache

本项目是一个本地代理和缓存服务，旨在减少 Figma API 的调用次数，通过本地数据库或文件系统缓存 Figma 数据，并提供管理界面。

## 项目结构

- `backend/`: Python FastAPI 后端，提供 MCP 服务和管理 API。
- `frontend/`: Vue 3 + Element Plus 前端，提供数据管理界面。

## 核心功能

1.  **MCP 服务**: 实现 `get_figma_data` 和 `download_figma_images` 工具，供 AI Agent 使用。
2.  **双模存储**: 支持 **MySQL 数据库** 或 **本地文件系统 (JSON)** 存储缓存数据。
3.  **管理界面**: 提供搜索、查看、同步和删除缓存数据的功能 (仅限数据库模式)。

## 存储模式

本项目支持两种存储模式：

### 1. 数据库模式 (MySQL)
- **适用场景**: 需要使用 Web 管理后台进行数据浏览、搜索、管理。
- **配置**: 需配置 MySQL 数据库及 `DB_HOST` 等环境变量。
- **特性**: 支持完整的管理后台功能。

### 2. 文件系统模式 (File System)
- **适用场景**: 仅作为 MCP Server 使用，无需安装 MySQL，即插即用。
- **配置**: 
    - **默认**: 不做任何配置时，数据保存在 `backend/data_cache` 目录。
    - **自定义**: 配置环境变量 `FIGMA_FILE_DATA_FOLDER` 可指定数据持久化目录。
- **特性**: 轻量级，数据以 JSON 文件格式存储，文件名包含元数据信息。

## 环境要求

- Python 3.8+
- Node.js 16+ (仅前端开发需要)
- MySQL 数据库 (仅数据库模式需要)

## 快速开始

### 1. 最小化配置 (作为 MCP Server 使用)

如果您只需要在 Cursor/Trae 中使用 MCP 功能，无需安装 MySQL。

1.  安装依赖：
    ```bash
    cd backend
    pip install -r requirements.txt
    ```
2.  配置环境变量：
    在 `.env` 文件中仅需配置：
    ```
    FIGMA_ACCESS_TOKEN=your_token_here
    # 可选：指定数据保存路径
    # FIGMA_FILE_DATA_FOLDER=D:/my_figma_data
    ```
3.  配置 AI Agent (MCP)：
    **Command**:
    ```bash
    python /absolute/path/to/backend/mcp_server.py
    ```

### 2. 完整模式 (含管理后台)

如果需要使用 Web 管理界面，请按以下步骤配置 MySQL。

#### 数据库配置

1.  确保 MySQL 服务已启动。
2.  创建数据库 `figma_mcp_cache` 并初始化表结构：
    ```bash
    mysql -u root -p < init_db.sql
    ```

#### 后端配置

1.  进入 `backend` 目录并安装依赖。
2.  配置 `.env` 文件，填入数据库配置：
    ```
    FIGMA_ACCESS_TOKEN=...
    DB_HOST=localhost
    DB_USER=root
    DB_PASSWORD=...
    DB_NAME=figma_mcp_cache
    ```
3.  启动后端服务：
    ```bash
    uvicorn app.main:app --reload --port 8000
    ```

#### 前端配置

1.  进入 `frontend` 目录并安装依赖：`npm install`
2.  启动开发服务器：`npm run dev`
3.  访问 http://localhost:5173 打开管理界面。

## 使用说明

1.  **AI 获取数据**: 当 AI Agent 调用 `get_figma_data` 时，系统会先检查本地缓存（数据库或文件）。
2.  **文件存储命名规则**: 在文件系统模式下，缓存文件命名格式为 `{file_key}__{node_id}.json` (无 node_id 则为 ROOT)。
3.  **强制同步**: 在前端页面点击“同步”按钮，或在 MCP 工具调用时指定 `force_refresh=True`。
