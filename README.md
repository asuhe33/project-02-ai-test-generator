# AI 测试用例生成器 (AI Test Case Generator)

An intelligent test case generation tool that leverages **Prompt Engineering + AI** to automatically produce comprehensive test cases from feature descriptions.

## Features

- **AI-powered generation** — Describe a feature, get structured test cases covering normal flow, boundaries, equivalence classes, errors, and security
- **Pre-built templates** — Login, search, forms, file upload, payment scenarios
- **Multiple export formats** — CSV, JSON
- **Offline mode** — Works without API keys using built-in templates
- **中文界面** — Full Chinese UI for local teams

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit |
| Core Logic | Python |
| LLM Integration | OpenAI / Claude API (optional) |
| Export | CSV, JSON (via pandas) |

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Usage

1. **Select a scenario template** from the sidebar (Login, Search, Forms, etc.)
2. **Review/edit the feature description** in the text area
3. **Click "生成测试用例"** to generate
4. **Browse the results** — categorized by type with priority levels
5. **Export** to CSV or JSON for test management tools

## LLM Integration (Optional)

To use real AI generation instead of built-in templates, set your API key:

```python
# In test_generator.py, uncomment the real LLM call:
import openai
openai.api_key = "your-api-key"
```

## Resume Highlight

This project demonstrates:
- ✅ Test case design methodology (equivalence partitioning, boundary value analysis)
- ✅ AI/LLM integration skills (Prompt Engineering)
- ✅ Full-stack development (Python + Streamlit)
- ✅ Software testing fundamentals
- ✅ Vibe Coding / AI-assisted development
