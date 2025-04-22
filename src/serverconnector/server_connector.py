# 修改 ServerConnector.py
import os
import logging
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack

logger = logging.getLogger(__name__)


class ServerConnector:
    """负责连接和管理MCP服务器的类"""

    def __init__(self, config, exit_stack):
        self.config = config
        self.exit_stack = exit_stack
        self.servers = {}  # 存储多个服务器会话

    async def connect_to_server(self, server_id, server_config):
        """连接到JSON配置中定义的MCP服务器"""
        logger.info(f"正在连接到服务器: {server_id}")

        # 准备命令和参数
        command = server_config.get("command")
        args = server_config.get("args", [])

        # 准备环境变量
        env = os.environ.copy()
        config_env = server_config.get("env", {})
        if config_env:
            env.update(config_env)

        # 设置工具特定环境变量
        # tool_env = self.config.get_tool_env(server_id)
        # if tool_env:
        #     env.update(tool_env)

        # 创建服务器参数
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=config_env
        )

        return await self._connect_with_params(server_params, server_id)

    # 保留原有的方法但可能不再使用
    async def connect_to_script(self, script_path):
        """连接到本地脚本服务器"""
        # 检查脚本类型
        is_python = script_path.endswith('.py')
        is_js = script_path.endswith('.js')

        if not (is_python or is_js):
            raise ValueError("服务器脚本必须是 .py 或 .js 文件")

        # 根据脚本类型选择执行命令 其他类型则需自行适配
        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[script_path],
            env=None
        )

        server_id = f"script:{script_path}"
        return await self._connect_with_params(server_params, server_id)

    # 保留原有的方法但可能不再使用
    async def connect_to_npx_server(self, package_name,server_config):
        """连接到通过 npx 安装的 MCP 服务器"""
        logger.info(f"正在连接到 npx 包: {package_name}")

        # 设置环境变量
        env = os.environ.copy()
        config_env = server_config.get("env", {})

        # 检查是否有特定包需要特殊处理
        #  package_base = package_name.split('@')[0] if '@' in package_name else package_name
        # tool_env = self.config.get_tool_env(package_base)
        #
        # # 合并环境变量
        # if tool_env:
        #     env.update(tool_env)
        #     logger.info(f"为 {package_base} 配置了特定环境变量")

        server_params = StdioServerParameters(
            command="npx",
            args=["-y", package_name],
            env=config_env
        )

        server_id = f"npx:{package_name}"
        return await self._connect_with_params(server_params, server_id)

    async def _connect_with_params(self, server_params, server_id):
        """使用指定参数连接到 MCP 服务器并返回会话"""
        # 启动 MCP 服务器并建立通信
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        stdio, write = stdio_transport

        session = await self.exit_stack.enter_async_context(
            ClientSession(stdio, write)
        )
        await session.initialize()

        # 缓存会话
        self.servers[server_id] = session

        # 列出 MCP 服务器上的工具
        response = await session.list_tools()
        tools = response.tools
        logger.info(f"已连接到服务器 {server_id}，支持以下工具: {[tool.name for tool in tools]}")
        print(f"\n已连接到服务器 {server_id}，支持以下工具:", [tool.name for tool in tools])

        return session

    def get_all_sessions(self):
        """获取所有活跃的会话"""
        return list(self.servers.values())

    async def get_all_tools(self):
        """获取所有服务器支持的工具列表"""
        all_tools = []

        for server_id, session in self.servers.items():
            try:
                response = await session.list_tools()
                all_tools.extend([{
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                } for tool in response.tools])
            except Exception as e:
                logger.error(f"获取服务器 {server_id} 工具列表失败: {str(e)}")

        return all_tools

    async def call_tool(self, tool_name, tool_args):
        """在所有可用服务器中查找并调用指定工具"""
        for server_id, session in self.servers.items():
            try:
                # 检查此服务器是否支持该工具
                response = await session.list_tools()
                if any(tool.name == tool_name for tool in response.tools):
                    # 调用工具
                    result = await session.call_tool(tool_name, tool_args)
                    return result
            except Exception as e:
                logger.error(f"在服务器 {server_id} 上调用工具 {tool_name} 失败: {str(e)}")

        # 如果所有服务器都不支持该工具
        logger.warning(f"没有服务器支持工具: {tool_name}")
        return None