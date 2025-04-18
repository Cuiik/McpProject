# main.py
import asyncio
import sys
import logging
from contextlib import AsyncExitStack

# 导入自定义模块
from config.Config import Config
from serverconnector.ServerConnector import ServerConnector
from modelclient.ModelClient import ModelClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPApp:
    """MCP应用主类，整合配置、连接器和模型客户端"""

    def __init__(self):
        self.exit_stack = AsyncExitStack()
        self.config = Config()
        self.server_connector = ServerConnector(self.config, self.exit_stack)
        self.model_client = ModelClient(self.config)

    async def initialize(self, server_identifiers):
        """初始化应用，连接到所有指定的服务器"""
        connected_count = 0
        for server_id in server_identifiers:
            try:
                await self.server_connector.connect_to_server(server_id)
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
    if len(sys.argv) < 2:
        print("Usage: python main.py <server1> [server2 ...]")
        print("Example: python main.py npx:tavily-mcp@0.1.4 ./local_server.py")
        sys.exit(1)

    # 获取所有服务器标识符
    server_identifiers = sys.argv[1:]

    app = MCPApp()
    try:
        connected = await app.initialize(server_identifiers)
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