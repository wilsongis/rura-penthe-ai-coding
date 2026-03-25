# src/rura_penthe/optimizer/execution_boundary.py

def compress_execution_result(stdout: str, stderr: str, exit_code: int) -> str:
    """
    Filters and truncates containerized output. Prioritizes capturing
    the top of stack traces and the final failure modes.
    """
    result = f"Exit Code: {exit_code}\\n"
    
    # Process STDOUT
    if len(stdout) > 2000:
        head = stdout[:500]
        tail = stdout[-1000:]
        result += f"STDOUT (Compressed):\\n{head}\\n\\n...[TRUNCATED OUTPUT]...\\n\\n{tail}\\n"
    elif stdout:
        result += f"STDOUT:\\n{stdout}\\n"
        
    # Process STDERR
    if len(stderr) > 1500:
        head = stderr[:500]
        tail = stderr[-1000:]
        result += f"STDERR (Compressed):\\n{head}\\n\\n...[TRUNCATED TRACE]...\\n\\n{tail}\\n"
    elif stderr:
        result += f"STDERR:\\n{stderr}\\n"
        
    if exit_code == 0 and not stderr and len(stdout) > 500:
        return f"{result}\\n(Note: Large stdout safely truncated by middleware.)"
        
    return result
