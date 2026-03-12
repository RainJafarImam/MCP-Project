import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
import json
import os

load_dotenv()

SERVERS = {
    "Arithmetic": {
        "transport": "stdio",
        "command": "C:\\Users\\DELL\\AppData\\Local\\Programs\\Python\\Python313\\Scripts\\uv.exe",
        "args": [
            "--directory",
            os.path.dirname(__file__),
            "run",
            "python",
            "main.py"
        ]
    }
}


async def is_arithmetic(prompt: str, llm) -> bool:
    messages = [
        SystemMessage(content="You are a classifier. Respond with only 'yes' or 'no'. Is the following message asking to perform a math or arithmetic operation like add, subtract, multiply, divide, power, or modulus?"),
        HumanMessage(content=prompt)
    ]
    response = await llm.ainvoke(messages)
    return "yes" in response.content.lower()


async def run(prompt: str):
    # ✅ No more async with — use directly
    client = MultiServerMCPClient(SERVERS)
    tools = await client.get_tools()
    named_tools = {tool.name: tool for tool in tools}

    llm = ChatGroq(model="llama-3.3-70b-versatilegit")
    llm_with_tools = llm.bind_tools(tools)

    print(f"\n❓ You: {prompt}")

    # Route 1 — Arithmetic
    if await is_arithmetic(prompt, llm):
        print("🔢 Routing to Arithmetic Handler...")

        messages = [
            SystemMessage(content="""You are an arithmetic assistant.
Always use the provided tools to perform calculations.
Never calculate yourself — always call the appropriate tool.
Available tools: add, subtract, multiply, divide, modulus, power."""),
            HumanMessage(content=prompt)
        ]

        response = await llm_with_tools.ainvoke(messages)

        if not getattr(response, "tool_calls", None):
            print("💬 Reply:", response.content)
            return

        tool_messages = []
        for tc in response.tool_calls:
            tool_name = tc["name"]
            tool_args = tc.get("args") or {}
            tool_id = tc["id"]

            print(f"🛠️  Calling: {tool_name} → {tool_args}")
            result = await named_tools[tool_name].ainvoke(tool_args)
            print(f"✅ Result: {result}")

            tool_messages.append(
                ToolMessage(tool_call_id=tool_id, content=json.dumps(result))
            )

        final = await llm_with_tools.ainvoke([*messages, response, *tool_messages])
        print(f"\n🎯 Answer: {final.content}")

    # Route 2 — General
    else:
        print("🌐 Routing to General Assistant...")
        messages = [
            SystemMessage(content="You are a helpful general assistant. Answer clearly and concisely."),
            HumanMessage(content=prompt)
        ]
        response = await llm.ainvoke(messages)
        print(f"\n💬 Answer: {response.content}")


async def chat():
    print("=" * 50)
    print("🤖 Arithmetic + General Assistant")
    print("   Type 'exit' to quit")
    print("=" * 50)

    while True:
        prompt = input("\nYou: ").strip()
        if not prompt:
            continue
        if prompt.lower() == "exit":
            print("👋 Goodbye!")
            break
        await run(prompt)


if __name__ == "__main__":
    asyncio.run(chat())