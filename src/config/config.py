# config.py
import os
from dotenv import load_dotenv
import logging

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()


class Config:
    """配置管理类，负责从环境变量加载所有配置"""

    def __init__(self):
        # DashScope 配置
        # 阿里百练的apikey
        self.dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")
        # 阿里百练的地址
        self.base_url = os.getenv("BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        # 如果没配置 默认用qwq-plus
        self.model = os.getenv("MODEL", "qwq-plus")



        # 验证必要配置
        self._validate_config()

    def _validate_config(self):
        """验证必要的配置是否存在"""
        if not self.dashscope_api_key:
            raise ValueError("❌ 未找到 DASHSCOPE API Key，请在 .env 文件中设置 DASHSCOPE_API_KEY")

    # def get_tool_env(self, tool_name):
    #     """根据工具名称返回需要的环境变量 apikey 弃用"""
    #     tool_env_map = {
    #         "tavily-mcp": {"TAVILY_API_KEY": os.getenv("TAVILY_API_KEY")},
    #
    #     }
    #
    #     return {k: v for k, v in tool_env_map.get(tool_name, {}).items() if v is not None}