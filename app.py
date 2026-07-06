"""AI Test Case Generator — Streamlit Web App.

A user-friendly interface for generating test cases from feature descriptions
using AI prompts. Works offline with built-in templates.
"""

import streamlit as st
import pandas as pd
from test_generator import (
    generate_test_cases,
    export_to_csv,
    export_to_json,
    get_scenario_types,
)

st.set_page_config(
    page_title="AI Test Case Generator",
    page_icon="🧪",
    layout="wide",
)

st.title("🧪 AI 测试用例生成器")
st.markdown("输入功能描述，AI 自动生成涵盖 **正常流程、边界值、等价类、异常场景、安全测试** 的完整测试用例。")

# ---------------------------------------------------------------------------
# Sidebar — Settings
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("⚙️ 设置")

    scenario_type = st.selectbox(
        "选择场景模板",
        ["通用（全类别）"] + get_scenario_types(),
        help="选择预定义的场景类型以获得更精准的用例，或选择通用模式",
    )

    st.markdown("---")
    st.markdown("### 💡 使用提示")
    st.markdown("""
    - **功能描述**越详细，生成的测试用例越精准
    - 建议包含：输入条件、限制规则、预期行为
    - 生成后可 **导出 CSV** 用于测试管理工具
    - 支持 **人工审核修改** 后再执行
    """)

    st.markdown("---")
    st.markdown("### 🚀 Vibe Coding 模式")
    st.info(
        "此工具本身即由 AI 辅助开发（Claude/Copilot），"
        "体现了'用 AI 加速测试工程'的理念。"
    )

# ---------------------------------------------------------------------------
# Main area — Input & Output
# ---------------------------------------------------------------------------

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 功能描述")

    default_description = {
        "登录/认证": "用户登录功能：用户输入用户名和密码进行登录，需要校验：\n"
                     "- 用户名不能为空\n- 密码不能为空且长度6-20位\n"
                     "- 连续5次失败锁定账户30分钟\n- 支持'记住我'功能",
        "搜索功能": "商品搜索功能：用户输入关键词搜索商品，要求：\n"
                   "- 支持模糊匹配\n- 搜索结果分页显示，每页20条\n"
                   "- 支持按价格/销量排序\n- 搜索词高亮显示",
        "表单验证": "用户注册表单：包含用户名、邮箱、密码、手机号字段：\n"
                   "- 用户名：3-20位字母数字\n- 邮箱：有效邮箱格式\n"
                   "- 密码：8-30位，含大小写+数字\n- 手机号：11位数字",
        "文件上传": "头像上传功能：用户上传头像图片：\n"
                   "- 支持 JPG/PNG/GIF 格式\n- 文件大小不超过5MB\n"
                   "- 自动裁剪为 200x200 像素\n- 上传后实时预览",
        "支付流程": "订单支付功能：用户使用信用卡支付订单：\n"
                   "- 支持 Visa/MasterCard\n- 需要输入卡号、有效期、CVV\n"
                   "- 支付成功后更新订单状态\n- 支付失败显示具体原因",
    }

    # Pre-fill description based on scenario type
    if scenario_type != "通用（全类别）" and scenario_type in default_description:
        desc_placeholder = default_description[scenario_type]
    else:
        desc_placeholder = default_description["登录/认证"]

    feature_input = st.text_area(
        "请描述待测试的功能（越详细越好）：",
        value=desc_placeholder,
        height=250,
        placeholder="例如：用户登录功能要求用户名不超过20个字符，密码必须包含大小写字母和数字...",
    )

    generate_btn = st.button("🚀 生成测试用例", type="primary", use_container_width=True)

with col2:
    st.subheader("📋 生成的测试用例")

    if generate_btn and feature_input.strip():
        with st.spinner("AI 正在分析功能描述并生成测试用例..."):
            scenario = scenario_type if scenario_type != "通用（全类别）" else None
            test_cases = generate_test_cases(feature_input, scenario)

        # Display summary
        categories = [tc["category"] for tc in test_cases]
        st.success(f"✅ 成功生成 **{len(test_cases)}** 条测试用例")

        # Category breakdown
        col_a, col_b, col_c, col_d, col_e = st.columns(5)
        breakdown = {
            "normal": ("正常流程", "🟢"),
            "boundary": ("边界值", "🟡"),
            "equivalence": ("等价类", "🔵"),
            "error": ("异常场景", "🔴"),
            "security": ("安全测试", "🟣"),
        }
        for col, (cat, (label, emoji)) in zip(
            [col_a, col_b, col_c, col_d, col_e], breakdown.items()
        ):
            count = categories.count(cat)
            col.metric(f"{emoji} {label}", count)

        # DataFrame display
        df_data = []
        for tc in test_cases:
            df_data.append({
                "ID": tc["id"],
                "标题": tc["title"],
                "类别": {"normal": "正常流程", "boundary": "边界值",
                        "equivalence": "等价类", "error": "异常场景",
                        "security": "安全测试"}.get(tc["category"], tc["category"]),
                "前置条件": tc["preconditions"],
                "预期结果": tc["expected_result"],
                "优先级": tc["priority"],
            })
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Expandable details
        with st.expander("📖 查看详细步骤"):
            for tc in test_cases:
                st.markdown(f"**#{tc['id']} — {tc['title']}** ({tc['priority'].upper()})")
                st.markdown(f"*类别：{tc['category']}*")
                for i, step in enumerate(tc["steps"], 1):
                    st.markdown(f"{i}. {step}")
                st.markdown(f"**期望结果：** {tc['expected_result']}")
                st.markdown("---")

        # Export buttons
        st.subheader("📤 导出")
        export_col1, export_col2, export_col3 = st.columns(3)

        csv_data = export_to_csv(test_cases)
        json_data = export_to_json(test_cases)

        with export_col1:
            st.download_button(
                "📥 导出 CSV",
                data=csv_data,
                file_name="test_cases.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with export_col2:
            st.download_button(
                "📥 导出 JSON",
                data=json_data,
                file_name="test_cases.json",
                mime="application/json",
                use_container_width=True,
            )
        with export_col3:
            # Show raw JSON for copying
            st.code(json_data[:500] + "...\n(完整内容已导出)", language="json")
    else:
        st.info("👈 在左侧输入功能描述，然后点击「生成测试用例」")

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.markdown("---")
st.markdown(
    "💡 **Vibe Coding 说明**：此工具展示了如何利用 AI 辅助测试工程。"
    "核心 Prompt Engineering + 结构化输出，可集成到测试流程中。"
    "当配置 LLM API Key 后，生成质量会进一步提升。"
)
