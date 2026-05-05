import sys
import os
import asyncio
from typing import Dict
from api_client import MiMoAgentClient
from file_utils import collect_python_files, chunk_code
from report_generator import save_markdown_report

class CodeReviewAgent:
    """
    代码审查Agent，负责协调多文件审查流程。
    利用MiMo-V2.5的强代码理解能力完成审查任务。
    """

    def __init__(self, api_key: str = None):
        self.client = MiMoAgentClient(api_key=api_key)
        self.model = "mimo-v2.5-pro"
        self.review_results: Dict[str, str] = {}

    async def review_file(self, filepath: str) -> str:
        """异步审查单个文件"""
        print(f"🔍 审查中：{filepath}")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            return f"❌ 读取文件失败：{str(e)}"

        # 拆分大文件
        chunks = chunk_code(code, max_lines=200)
        reports = []
        for idx, chunk in chunks:
            report = self.client.review_code(chunk)
            reports.append(f"### 代码块 {idx}\n{report}")

        full_report = f"## 文件：`{filepath}`\n\n" + "\n\n".join(reports)
        self.review_results[filepath] = full_report
        print(f"✅ 完成审查：{filepath}")
        return full_report

    async def run(self, target_dir: str = "."):
        """并发审查目标目录下所有Python文件"""
        files = collect_python_files(target_dir)
        if not files:
            print("⚠️ 未找到Python文件")
            return

        print(f"🚀 开始审查 {len(files)} 个文件...\n")
        tasks = [self.review_file(f) for f in files]
        await asyncio.gather(*tasks)

        # 保存报告
        report_path = save_markdown_report(self.review_results, target_dir)
        print(f"\n📄 审查报告已保存至：{report_path}")


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    api_key = os.getenv("MIMO_API_KEY")
    if not api_key:
        print("❌ 请设置环境变量 MIMO_API_KEY")
        sys.exit(1)

    agent = CodeReviewAgent(api_key=api_key)
    asyncio.run(agent.run(target_dir=target))


if __name__ == "__main__":
    main()
