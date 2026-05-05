import os
import asyncio
from typing import List, Tuple

def collect_python_files(root_dir: str = ".") -> List[str]:
    """递归收集所有Python文件路径"""
    py_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for f in filenames:
            if f.endswith(".py"):
                py_files.append(os.path.join(dirpath, f))
    return py_files

def chunk_code(code: str, max_lines: int = 300) -> List[Tuple[int, str]]:
    """
    将超过 max_lines 的代码拆成多个块，
    返回列表元素为 (块编号, 代码文本)。
    MiMo支持256k上下文窗口，非常充裕。
    """
    lines = code.split('\n')
    if len(lines) <= max_lines:
        return [(1, code)]
    chunks = []
    for i in range(0, len(lines), max_lines):
        chunks.append((i // max_lines + 1, '\n'.join(lines[i:i + max_lines])))
    return chunks
