from fastmcp import FastMCP

mcp = FastMCP("Arithmetic")


@mcp.tool()
def add(a: float, b: float) -> dict:
    """Add two numbers together.

    Args:
        a: First number.
        b: Second number.
    """
    return {"operation": "add", "a": a, "b": b, "result": a + b}


@mcp.tool()
def subtract(a: float, b: float) -> dict:
    """Subtract b from a.

    Args:
        a: First number.
        b: Second number to subtract.
    """
    return {"operation": "subtract", "a": a, "b": b, "result": a - b}


@mcp.tool()
def multiply(a: float, b: float) -> dict:
    """Multiply two numbers together.

    Args:
        a: First number.
        b: Second number.
    """
    return {"operation": "multiply", "a": a, "b": b, "result": a * b}


@mcp.tool()
def divide(a: float, b: float) -> dict:
    """Divide a by b.

    Args:
        a: Numerator.
        b: Denominator (cannot be zero).
    """
    if b == 0:
        return {"status": "error", "message": "Division by zero is not allowed."}
    return {"operation": "divide", "a": a, "b": b, "result": a / b}


@mcp.tool()
def modulus(a: float, b: float) -> dict:
    """Get the remainder of a divided by b.

    Args:
        a: Dividend.
        b: Divisor (cannot be zero).
    """
    if b == 0:
        return {"status": "error", "message": "Modulus by zero is not allowed."}
    return {"operation": "modulus", "a": a, "b": b, "result": a % b}


@mcp.tool()
def power(base: float, exponent: float) -> dict:
    """Raise base to the power of exponent.

    Args:
        base: The base number.
        exponent: The exponent.
    """
    return {"operation": "power", "base": base, "exponent": exponent, "result": base ** exponent}


if __name__ == "__main__":
    mcp.run()