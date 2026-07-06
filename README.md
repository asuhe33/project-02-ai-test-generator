# AI 测试用例生成器

利用 **Prompt Engineering + AI** 智能生成结构化测试用例的工具。

## 功能特性

- **AI 驱动生成** — 描述功能特征，自动生成涵盖正常流程、边界值、等价类、异常场景和安全测试的结构化用例
- **预置模板** — 登录、搜索、表单、文件上传、支付等常见场景
- **多种导出格式** — 支持 CSV、JSON
- **离线模式** — 无需 API Key，内置模板可直接使用
- **中文界面** — 全中文交互

## 技术栈

| 组件 | 技术 |
|------|------|
| 前端 | Streamlit |
| 核心逻辑 | Python |
| LLM 集成 | OpenAI / Claude API（可选） |
| 数据导出 | CSV、JSON（基于 pandas） |

## 快速开始

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 使用方法

1. 在左侧边栏**选择场景模板**（登录、搜索、表单等）
2. **编辑功能描述**（越详细生成越精准）
3. 点击 **"生成测试用例"**
4. **浏览结果** — 按类别和优先级分类展示
5. **导出**为 CSV 或 JSON，用于测试管理工具

## LLM 集成（可选）

如需使用真实的 AI 生成（而非内置模板），配置 API Key：

```python
# 在 test_generator.py 中取消 LLM 调用的注释
import openai
openai.api_key = "your-api-key"
```

## 项目亮点

本项目展示了：
- ✅ 测试用例设计方法论（等价类划分、边界值分析）
- ✅ AI/LLM 集成能力（Prompt Engineering）
- ✅ 全栈开发（Python + Streamlit）
- ✅ 软件测试基础知识
- ✅ Vibe Coding / AI 辅助开发
