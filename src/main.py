# main.py
import asyncio
import sys
import logging
from contextlib import AsyncExitStack

# 导入自定义模块
from config.config import Config
from serverconnector.server_connector import ServerConnector
from modelclient.model_client import ModelClient
from config.mcp_config_loader import MCPConfigLoader  # 导入配置加载器

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPApp:
    """MCP应用主类，整合配置、连接器和模型客户端"""

    def __init__(self, config_file_path="mcp_servers.json"):
        self.exit_stack = AsyncExitStack()
        self.config = Config()
        self.server_connector = ServerConnector(self.config, self.exit_stack)
        self.model_client = ModelClient(self.config)
        self.mcp_config = MCPConfigLoader(config_file_path)

    async def initialize(self):
        """初始化应用，连接到配置文件中启用的所有服务器"""
        enabled_servers = self.mcp_config.get_enabled_servers()
        connected_count = 0

        if not enabled_servers:
            logger.warning("没有找到已启用的MCP服务器配置")
            return False

        for server_id, server_config in enabled_servers.items():
            try:
                await self.server_connector.connect_to_server(server_id, server_config)
                print(f"✅ 已连接到服务器: {server_id}")
                connected_count += 1
            except Exception as e:
                logger.error(f"连接到服务器 {server_id} 失败: {str(e)}")
                print(f"⚠️ 连接到服务器 {server_id} 失败: {str(e)}")

        return connected_count > 0

    async def chat_loop(self):
        """运行交互式聊天循环"""
        print("\n🤖 MCP 客户端已启动！输入 'quit' 或 'exit' 或 'q'退出")

        while True:
            try:
                # 使用清晰的提示符
                user_input = input("\n👤 > ").strip()

                # 检查输入是否为退出命令
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 正在退出...")
                    break

                # 检查输入是否为空或只包含特殊字符
                if not user_input or all(c in '=- \t\n' for c in user_input):
                    continue  # 跳过空白或只含特殊字符的输入

                # 处理有效输入
                await self.model_client.process_query(user_input, self.server_connector)
            except KeyboardInterrupt:
                print("\n👋 程序被中断，正在退出...")
                break
            except Exception as e:
                logger.error(f"处理查询时出错: {e}", exc_info=True)
                print(f"\n⚠️ 发生错误: {str(e)}")

    async def cleanup(self):
        """清理资源"""
        print("🧹 正在清理资源...")
        await self.exit_stack.aclose()
        print("✅ 资源已清理完毕")


async def main():
    """主函数"""
    # 允许用户指定配置文件路径
    config_file = "mcp_servers.json"
    if len(sys.argv) > 1:
        config_file = sys.argv[1]

    app = MCPApp(config_file)
    try:
        connected = await app.initialize()
        if not connected:
            print("⚠️ 未能成功连接到任何服务器，程序将退出")
            return

        await app.chat_loop()
    except Exception as e:
        logger.error(f"程序运行时出错: {e}", exc_info=True)
        print(f"⚠️ 程序出现错误: {str(e)}")
    finally:
        await app.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 程序被中断，已退出")