[//]: # (# 模块化 MCP 客户端)

[//]: # ()
[//]: # (这是一个模块化、可扩展的 MCP &#40;Model Control Protocol&#41; 客户端实现，用于连接大模型 API 和多个工具服务器。)





## 结构说明：

1. **配置管理** (`config.py`)
   - 负责从环境变量加载和验证配置

2. **MCP服务器类型连接器** (`server_connector.py`)
   - 负责连接和管理多个 MCP 服务器
   - 支持连接本地脚本和 NPX 包

3. **模型客户端** (`model_client.py`)
   - 负责与大模型 API 交互
   - 处理流式响应、工具调用和结果处理

4. **存放本地MCP服务(py)** (`mcpserver`)
   - 存放本地python的mcp服务，可自行扩展开发

5. **MCP配置信息加载器** (`mcp_config_loader.py`)
   - 解析`mcp_servers.json`文件的配置信息

6. **MCP配置文件** (`mcp_servers.json`)
   - 功能和Cursor的MCP文件一致的配置文件
   
7. **主应用** (`main.py`)
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




## 环境配置：

1. 拉取项目后 进到根目录下
```
# 创建虚拟环境
uv venv

# 激活虚拟环境
.venv/bin/activate

# 安装依赖
uv pip install -r requirements.txt
uv add dotenv 
```


2. 根目录下复制 `.env example`  改名为`.env` 文件并设置必要的环境变量：

```
# 阿里百练的apikey
DASHSCOPE_API_KEY=your_dashscope_api_key 

# 阿里百练的地址
BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# 选择模型
MODEL=xxxx

```


## 添加MCP

基于JSON文件统一管理

复制 `mcp_servers.json example`  改名为`mcp_servers.json` 文件

1. 新增的MCP服务如果是自己写的py，则参考weather_server.py，

2. 如果是其他远程MCP则复制对应MCP的JSON，添加进mcp_servers.json（和cursor的配置一致）

```json
{
  "mcpServers": {

    "YourMcpName": {
      "disabled": false,
      "command": "xxx",
      "args": ["xxx"],
      "env": {}
    }
     
  }
}
```


### 运行 （1或者2都可以）


1、命令行

激活虚拟环境后

```bash
python src/main.py
```

2、PyCharm
也可PyCharm运行





