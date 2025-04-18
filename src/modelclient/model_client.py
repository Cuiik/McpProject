# model_client.py
import json
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)


class ModelClient:
    """负责与大模型交互的类"""

    def __init__(self, config):
        self.config = config
        self.client = OpenAI(
            api_key=config.dashscope_api_key,
            base_url=config.base_url,
            timeout=300
        )

    async def process_query(self, query, server_connector):
        """处理用户查询并调用工具"""
        messages = [{"role": "user", "content": query}]
        logger.info(f"处理查询: {query}")

        # 获取可用工具列表
        available_tools = await server_connector.get_all_tools()

        # 记录完整回复
        final_answer = ""
        tool_calls_detected = False

        try:
            # 调用 OpenAI API（启用流式输出）
            stream_response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                tools=available_tools,
                stream=True  # 启用流式输出
            )

            print("=" * 20 + "思考过程" + "=" * 20)

            # 收集模型回复和工具调用
            full_response_text = ""  # 用于记录回复内容
            reasoning_content = ""  # 记录思考过程
            current_tool_calls = []  # 当前收集到的工具调用
            is_answering = False  # 是否已经开始回答

            for chunk in stream_response:
                # 跳过没有choices的chunk
                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta

                # 处理思考过程
                if hasattr(delta, 'reasoning_content') and delta.reasoning_content is not None:
                    print(delta.reasoning_content, end="", flush=True)
                    reasoning_content += delta.reasoning_content
                    continue

                # 处理工具调用
                if hasattr(delta, 'tool_calls') and delta.tool_calls:
                    # 首次收到工具调用时切换到回复模式
                    if not is_answering:
                        is_answering = True
                        print("\n" + "=" * 20 + "回复内容" + "=" * 20)

                    tool_calls_detected = True
                    # 扩展工具调用列表以适应索引
                    while len(current_tool_calls) <= max([t.index for t in delta.tool_calls]):
                        current_tool_calls.append({"function": {}})

                    # 收集每个工具调用的信息
                    for tool_call in delta.tool_calls:
                        index = tool_call.index
                        if tool_call.id:
                            current_tool_calls[index]["id"] = tool_call.id

                        if tool_call.function:
                            if tool_call.function.name:
                                current_tool_calls[index]["function"]["name"] = tool_call.function.name

                            if tool_call.function.arguments:
                                if "arguments" not in current_tool_calls[index]["function"]:
                                    current_tool_calls[index]["function"]["arguments"] = ""
                                current_tool_calls[index]["function"]["arguments"] += tool_call.function.arguments

                # 处理普通文本内容
                if delta.content is not None:
                    if not is_answering:
                        is_answering = True
                        print("\n" + "=" * 20 + "回复内容" + "=" * 20)

                    print(delta.content, end="", flush=True)
                    full_response_text += delta.content
                    final_answer += delta.content

                # 如果已经到达工具调用的结束
                if chunk.choices[0].finish_reason == "tool_calls":
                    break

            # 完成所有工具调用并收集结果
            if tool_calls_detected:
                print(f"\n" + "=" * 20 + "工具调用信息" + "=" * 20)

                # 收集所有工具调用的结果
                tool_results = []

                # 向最终消息记录添加带有tool_calls的助手消息
                assistant_message = {
                    "role": "assistant",
                    "content": full_response_text,
                    "tool_calls": current_tool_calls
                }
                messages.append(assistant_message)

                # 处理每个工具调用
                for i, tool_call in enumerate(current_tool_calls):
                    if "function" in tool_call and "name" in tool_call["function"] and "arguments" in tool_call[
                        "function"]:
                        tool_name = tool_call["function"]["name"]
                        try:
                            # 解析参数JSON
                            tool_args_str = tool_call["function"]["arguments"]
                            tool_args = json.loads(tool_args_str)

                            # 执行工具调用
                            print(f"[调用工具 {tool_name} 参数: {tool_args}]")
                            result = await server_connector.call_tool(tool_name, tool_args)

                            # 检查工具返回结果
                            if result and result.content and result.content[0].text:
                                tool_result = result.content[0].text
                                print(f"[工具返回: {tool_result}]")

                                # 创建工具返回消息
                                tool_message = {
                                    "role": "tool",
                                    "tool_call_id": tool_call["id"],
                                    "content": tool_result
                                }
                                messages.append(tool_message)
                                tool_results.append(tool_result)
                            else:
                                print(f"⚠️ 工具 {tool_name} 返回为空")
                        except json.JSONDecodeError:
                            print(f"⚠️ 无法解析工具 {tool_name} 的参数: {tool_call['function']['arguments']}")
                        except Exception as e:
                            print(f"⚠️ 工具调用错误 {tool_name}: {str(e)}")

                # 如果有工具返回结果，继续让模型处理
                if tool_results:
                    print("\n" + "=" * 20 + "处理工具返回结果" + "=" * 20)

                    # 创建新的对话流来处理工具返回
                    final_stream = self.client.chat.completions.create(
                        model=self.config.model,
                        messages=messages,
                        tools=available_tools,
                        stream=True
                    )

                    # 处理最终响应
                    final_answer = ""  # 重置最终回答
                    for chunk in final_stream:
                        if not chunk.choices:
                            continue

                        delta = chunk.choices[0].delta
                        if delta.content is not None:
                            print(delta.content, end="", flush=True)
                            final_answer += delta.content

            return final_answer
        except Exception as e:
            logger.error(f"⚠️ 发生错误: {str(e)}")
            print(f"\n⚠️ 发生错误: {str(e)}")
            return ""