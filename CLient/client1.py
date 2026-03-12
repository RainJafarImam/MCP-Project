import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage
import json

load_dotenv(r"C:\Users\DELL\Desktop\Client\.env")

SERVERS = {
    "Todo": {
        "transport": "stdio",
        "command": "C:\\Users\\DELL\\AppData\\Local\\Programs\\Python\\Python313\\Scripts\\uv.exe",
        "args": [
            "run",
            "fastmcp",
            "run",
            "D:\\MCP\\Project\\MCP-Project\\ToDo-LocalMCP\\main.py"
        ]
    },
    "manim-server": {
        "command": "C:\\Users\\DELL\\AppData\\Local\\Programs\\Python\\Python313\\python.exe",
        "args": [
            "D:\\MCP\\manim-mcp-server\\src\\manim_server.py"
        ],
        "env": {
            "MANIM_EXECUTABLE": "C:\\Users\\DELL\\AppData\\Local\\Programs\\Python\\Python313\\Scripts\\manim.exe"
        },
        "transport": "stdio"  # ✅ removed extra keys like type, cwd, timeout etc
    },
}


async def is_todo_related(prompt: str, llm) -> bool:
    messages = [
        SystemMessage(content="You are a classifier. Respond with only 'yes' or 'no'. Is the following message asking to add, manage, or track a task or todo item?"),
        HumanMessage(prompt)
    ]
    response = await llm.ainvoke(messages)
    return 'yes' in response.content.lower()


async def is_tool_related(prompt: str, llm, tool_names: list) -> bool:
    messages = [
        SystemMessage(content=f"You are a classifier. Respond with only 'yes' or 'no'. Is the following message asking to use one of these tools: {', '.join(tool_names)}?"),
        HumanMessage(prompt)
    ]
    response = await llm.ainvoke(messages)
    return 'yes' in response.content.lower()


async def main():
    client = MultiServerMCPClient(SERVERS)
    tools = await client.get_tools()

    named_tools = {}
    for tool in tools:
        named_tools[tool.name] = tool

    print("Available tools:", named_tools.keys())

    llm = ChatGroq(model='llama-3.3-70b-versatile')
    llm_with_tools = llm.bind_tools(tools)

    prompt = "today i will go gym in evening add it in todo list"

    if await is_todo_related(prompt, llm):
        print("📝 Routing to Todo Handler...")
        messages = [
            SystemMessage(content="""You are a Todo assistant. Only use the provided todo tools.
When calling add_todo, ALWAYS provide ALL fields:
- title: short title of the task
- description: must not be empty, write a meaningful description
- priority: must be one of 'low', 'medium', 'high'
- tag: must be one of 'personal', 'work', 'learning', 'travel'
- due_date: use format YYYY-MM-DD, if not specified use '2026-03-11'"""),
            HumanMessage(prompt)
        ]
        response = await llm_with_tools.ainvoke(messages)

        if not getattr(response, "tool_calls", None):
            print("\nLLM Reply:", response.content)
            return

        tool_messages = []
        for tc in response.tool_calls:
            selected_tool = tc["name"]
            selected_tool_args = tc.get("args") or {}
            selected_tool_id = tc["id"]
            result = await named_tools[selected_tool].ainvoke(selected_tool_args)
            tool_messages.append(ToolMessage(tool_call_id=selected_tool_id, content=json.dumps(result)))

        final_response = await llm_with_tools.ainvoke([*messages, response, *tool_messages])
        print(f"Final response: {final_response.content}")

    elif await is_tool_related(prompt, llm, list(named_tools.keys())):
        print("🛠️  Routing to Tool Handler...")
        messages = [
            SystemMessage(content=f"You are a helpful assistant. Use the appropriate tool to fulfill the request. Available tools: {', '.join(named_tools.keys())}"),
            HumanMessage(prompt)
        ]
        response = await llm_with_tools.ainvoke(messages)

        if not getattr(response, "tool_calls", None):
            print("\nLLM Reply:", response.content)
            return

        tool_messages = []
        for tc in response.tool_calls:
            selected_tool = tc["name"]
            selected_tool_args = tc.get("args") or {}
            selected_tool_id = tc["id"]
            result = await named_tools[selected_tool].ainvoke(selected_tool_args)
            tool_messages.append(ToolMessage(tool_call_id=selected_tool_id, content=json.dumps(result)))

        final_response = await llm_with_tools.ainvoke([*messages, response, *tool_messages])
        print(f"Final response: {final_response.content}")

    else:
        print("🌐 Routing to General Assistant...")
        messages = [
            SystemMessage(content="You are a helpful general assistant. Answer clearly."),
            HumanMessage(prompt)
        ]
        response = await llm.ainvoke(messages)
        print(f"\nLLM Reply: {response.content}")


if __name__ == '__main__':
    asyncio.run(main())