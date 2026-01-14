# Figma MCP Local Cache

本项目是一个本地代理和缓存服务，旨在减少 Figma API 的调用次数，通过本地数据库缓存 Figma 数据，并提供管理界面。

## 项目结构

- `backend/`: Python FastAPI 后端，提供 MCP 服务和管理 API。
- `frontend/`: Vue 3 + Element Plus 前端，提供数据管理界面。

## 核心功能

1.  **MCP 服务**: 实现 `get_figma_data` 和 `download_figma_images` 工具，供 AI Agent 使用。
2.  **本地缓存**: 将获取的 Figma 数据存储在 MySQL 数据库中，优先读取缓存。
3.  **管理界面**: 提供搜索、查看、同步和删除缓存数据的功能。

## 环境要求

- Python 3.8+
- Node.js 16+
- MySQL 数据库

## 快速开始

### 1. 数据库配置

1.  确保 MySQL 服务已启动。
2.  创建数据库 `figma_mcp_cache` 并初始化表结构：
    ```bash
    mysql -u root -p < init_db.sql
    ```

### 2. 后端配置

1.  进入 `backend` 目录：
    ```bash
    cd backend
    ```
2.  安装依赖：
    ```bash
    pip install -r requirements.txt
    ```
3.  配置环境变量：
    复制 `.env.example` 为 `.env`，并填入 Figma Token 和数据库配置。
    ```bash
    cp ../.env.example ../.env
    # 编辑 ../.env 文件
    ```
4.  启动后端服务：
    ```bash
    # 启动 FastAPI 服务 (提供管理 API)
    uvicorn app.main:app --reload --port 8000
    ```

### 3. 前端配置

1.  进入 `frontend` 目录：
    ```bash
    cd frontend
    ```
2.  安装依赖：
    ```bash
    npm install
    ```
3.  启动开发服务器：
    ```bash
    npm run dev
    ```
    访问 http://localhost:5173 打开管理界面。

### 4. 配置 AI Agent (MCP)

在您的 AI 编辑器（如 Cursor、Trae）中配置 MCP Server。

**Command**:
```bash
python .../figma-mcp-local-cache/backend/mcp_server.py
```
(请使用绝对路径，并确保 python 环境已安装依赖)

## 使用说明

1.  **AI 获取数据**: 当 AI Agent 调用 `get_figma_data` 时，系统会先检查本地数据库。
2.  **查看缓存**: 打开前端页面，可以看到所有缓存的 Figma 文件和节点。
3.  **强制同步**: 在前端页面点击“同步”按钮，强制从 Figma API 更新数据。
4.  **删除缓存**: 在前端页面点击“删除”按钮，移除本地缓存。
