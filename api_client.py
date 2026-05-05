import os
from openai import OpenAI

class MiMoAgentClient:
    """
    小米MiMo大模型API客户端（兼容OpenAI格式）
    文档参考：https://platform.xiaomimimo.com/
    """

    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or os.getenv("MIMO_API_KEY")
        self.base_url = base_url or os.getenv("MIMO_BASE_URL", "https://api.xiaomimimo.com/v1")
        if not self.api_key:
            raise ValueError("❌ 请设置 MIMO_API_KEY 环境变量或直接传入 api_key")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    def chat(self, model: str, messages: list, temperature: float = 0.3, max_tokens: int = 4096) -> str:
        """
        封装Chat请求，返回模型回复文本。
        可切换思考模式（deepseek-r1-风格）设置 `reasoning=True` 增加链式推理。
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ API调用失败：{str(e)}"

    def review_code(self, code: str, language: str = "Python") -> str:
        """
        对给定代码进行审查，返回结构化建议。
        利用MiMo强大的代码理解与推理能力。
        """
        system_prompt = f"""你是一位资深{language}代码审查专家，擅长发现代码缺陷、安全隐患和性能问题。
请对以下代码进行详细审查，并按以下格式输出报告：

## 📋 代码审查报告

### 1. 严重问题（Critical）
- 可能导致程序崩溃或安全漏洞的问题

### 2. 代码异味（Code Smell）
- 不符合最佳实践的写法

### 3. 性能优化建议
- 可提升运行效率的改进点

### 4. 重构推荐
- 给出具体的代码修改示例

请保持客观、具体，避免空泛评价。"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"请审查以下代码：\n\n```{language}\n{code}\n```"}
        ]
        return self.chat(model="mimo-v2.5-pro", messages=messages)

    def suggest_refactor(self, code: str, issue_desc: str) -> str:
        """
        基于具体问题建议，给出重构后的代码。
        MiMo在代码生成方面表现突出，适合该场景。
        """
        prompt = f"""根据以下问题描述，对代码进行优化重构，并返回完整的重构后代码：

【问题描述】
{issue_desc}

【原始代码】
```python
{code}
请输出可直接复制使用的完整重构代码。"""
messages = [
{"role": "system", "content": "你是一位代码重构专家，输出干净、可运行的Python代码。"},
{"role": "user", "content": prompt}
]
return self.chat(model="mimo-v2.5-pro", messages=messages)

---- 使用示例 ----
if name == "main":
client = MiMoAgentClient(api_key="your-api-key-here")
sample_code = """
def calc(a,b):
return a+b
"""
report = client.review_code(sample_code)
print(report)
