# mcp_config_loader.py
import json
import os
import logging

logger = logging.getLogger(__name__)


class MCPConfigLoader:
    """MCP服务器配置加载器"""

    def __init__(self, config_file_path="mcp_servers.json"):
        self.config_file_path = config_file_path
        self.mcp_servers = {}
        self._load_config()

    def _load_config(self):
        """从配置文件加载服务器信息"""
        try:
            if os.path.exists(self.config_file_path):
                with open(self.config_file_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    self.mcp_servers = config_data.get("mcpServers", {})
                logger.info(f"成功从 {self.config_file_path} 加载了 {len(self.mcp_servers)} 个MCP服务器配置")
            else:
                logger.warning(f"配置文件 {self.config_file_path} 不存在，将使用空配置")
        except Exception as e:
            logger.error(f"加载配置文件 {self.config_file_path} 失败: {str(e)}")
            raise

    def get_enabled_servers(self):
        """获取所有已启用的服务器配置"""
        enabled_servers = {}
        for server_id, config in self.mcp_servers.items():
            if not config.get("disabled", False):  # 默认为启用
                enabled_servers[server_id] = config
        return enabled_servers

    def get_server_config(self, server_id):
        """获取指定服务器的配置"""
        return self.mcp_servers.get(server_id)