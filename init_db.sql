CREATE DATABASE IF NOT EXISTS figma_mcp_cache;
USE figma_mcp_cache;

CREATE TABLE IF NOT EXISTS figma_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_key VARCHAR(255) NOT NULL COMMENT 'Figma 文件 Key',
    node_id VARCHAR(255) COMMENT 'Figma 节点 ID',
    name VARCHAR(255) NULL COMMENT 'Figma 文件名称',
    depth INT DEFAULT NULL COMMENT '遍历深度',
    last_modified DATETIME NULL COMMENT 'Figma 文件最后更新时间',
    data LONGTEXT COMMENT '缓存的 JSON 数据',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_file_key (file_key),
    INDEX idx_node_id (node_id)
) COMMENT='Figma 数据缓存表';
