import random
from fastmcp import FastMCP

# Create a FastMCP server instance
mcp = FastMCP(name="Expense Tracker")

@mcp.tool
def roll_dice(n_dice: int = 1) -> list[int]:
    """Roll n_dice 6-sided dice and return the results."""
    return [random.randint(1, 6) for _ in range(n_dice)]

@mcp.tool
def add_numbers(a: float, b: float) -> str:
    """Add two numbers together."""
    result = a + b
    return f"jafar bhai\n{a} + {b} = {result}"

@mcp.tool
def mobile_name()->str:
    return f"One+ 13R"
    

if __name__ == "__main__":
    mcp.run()