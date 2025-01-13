# 多轮对话
def chat():
    messages = [
        {"role": "system", "content": "You are a helpful assistant that can manage memories."},
        {"role": "system", "content": ""}  # 占位符，用于动态更新记忆概览
    ]
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        # 更新 messages[1] 为当前记忆概览
        memory_summary = memory_manager.get_summary()
        messages[1] = {"role": "system", "content": f"Your memory: {json.dumps(memory_summary, indent=2)}"}

        # 添加用户输入到消息历史
        messages.append({"role": "user", "content": user_input})

        # 发送消息并获取响应
        response = send_messages(messages, tools=tools)

        # 处理 LLM 的工具调用
        if response.tool_calls:
            for tool_call in response.tool_calls:
                function_name = tool_call.function.name
                function_args = eval(tool_call.function.arguments)

                logging.info(f"Calling function: {function_name} with args: {function_args}")

                if function_name == "add_memory":
                    memory_manager.add_memory(**function_args)
                    messages.append({"role": "function", "name": "add_memory", "content": json.dumps({"status": "success"})})
                elif function_name == "retrieve_memory":
                    memory = memory_manager.retrieve_memory(**function_args)
                    messages.append({"role": "function", "name": "retrieve_memory", "content": json.dumps(memory)})
                elif function_name == "update_memory":
                    memory_manager.update_memory(**function_args)
                    messages.append({"role": "function", "name": "update_memory", "content": json.dumps({"status": "success"})})
                elif function_name == "list_memories":
                    memories = memory_manager.list_memories(**function_args)
                    messages.append({"role": "function", "name": "list_memories", "content": json.dumps(memories)})

        # 添加 LLM 响应到消息历史
        if response.content:
            messages.append({"role": "assistant", "content": response.content})
            print(f"Assistant: {response.content}")