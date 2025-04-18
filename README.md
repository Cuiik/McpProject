[//]: # (# 模块化 MCP 客户端)

[//]: # ()
[//]: # (这是一个模块化、可扩展的 MCP &#40;Model Control Protocol&#41; 客户端实现，用于连接大模型 API 和多个工具服务器。)





## 包名结构

分为以下几个核心模块：

1. **配置管理** (`config`)
   - 负责从环境变量加载和验证配置
   - 管理不同工具所需的特定环境变量

2. **MCP服务器类型连接器** (`serverconnector`)
   - 负责连接和管理多个 MCP 服务器
   - 支持连接本地脚本和 NPX 包
   - 提供跨服务器的工具查找和调用功能

3. **模型客户端** (`modelclient`)
   - `ModelClient.py`是参考阿里百练的qwq-plus的function calling例子改的
   - 负责与大模型 API 交互
   - 处理流式响应、工具调用和结果处理

4. **本地MCP服务** (`mcpserver`)
   - 存放本地python的mcp服务，可自行扩展开发

5. **主应用** (`main.py`)
   - 整合上述所有模块
   - 提供命令行界面和交互式聊天

[//]: # (## 特性)

[//]: # ()
[//]: # (- 支持连接多个 MCP 服务器)

[//]: # (- 模块化设计便于扩展)

[//]: # (- 统一的工具调用接口)

[//]: # (- 改进的错误处理和日志记录)

[//]: # (- 支持流式输出和推理过程显示)

## 使用方法

### 环境设置

根目录下复制 `.env example`  改名为`.env` 文件并设置必要的环境变量：

```
# 阿里百练的apikey
DASHSCOPE_API_KEY=your_dashscope_api_key
# 阿里百练的地址
BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
# 选择模型
MODEL=qwq-plus
# TAVILY_API_KEY
TAVILY_API_KEY=your_tavily_api_key_if_needed
# openweather 天气的apikey
WEATHER_API_KEY=your_weather_api_key_if_needed
```

### 运行
1、命令行

可以同时连接多个服务器：(后续增加注意中间空格隔开)
目前就一个天气的，

```bash
python src/main.py src/mcpserver/WeatherServer.py npx:tavily-mcp@0.1.4 
```

2、PyCharm
添加对应的启动参数即可
如图

## 扩展指南

### 添加新的服务器类型(注意不是添加新的MCP，而是添加新的 MCP服务类型，MCP支持多语言类型的，比如java、py、c)

修改 `serverConnector.py` 中的 `connect_to_server` 方法：

```python
async def connect_to_server(self, server_identifier):
    # 现有的处理逻辑...
    
    # 添加新的服务器类型支持
    if server_identifier.startswith("new-type:"):
        _, params = server_identifier.split(":", 1)
        return await self.connect_to_new_type(params)
```



### 新加MCP工具服务
1、如果是本地python，则参考WeatherServer.py，丢同一个路径下，然后在运行启动参数配置上对应路径即可

2、如果是npx的MCP服务（node包这种），直接加进启动参数即可 ps：注意node版本，tavily的要求node 20+




PS：如果是对应是需要apikey的如下添加： 修改 `Config.py` 中的 `get_tool_env` 方法：

```python
def get_tool_env(self, tool_name):
    tool_env_map = {
        "tavily-mcp": {"TAVILY_API_KEY": self.tavily_api_key},
        "new-tool": {"NEW_TOOL_API_KEY": os.getenv("NEW_TOOL_API_KEY")}
    }
    
    return {k: v for k, v in tool_env_map.get(tool_name, {}).items() if v is not None}
```
