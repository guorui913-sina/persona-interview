#!/usr/bin/env python3
"""
盖洛普优势解析器 - 从盖洛普优势报告中提取结构化信息

支持格式：PDF
输出格式：JSON

使用方法：
    python gallup_parser.py gallup_report.pdf
    python gallup_parser.py gallup_report.pdf --output gallup_data.json

依赖：
    PyPDF2>=3.0.0

注意：盖洛普报告的格式可能因版本不同而有所差异，此脚本基于常见格式设计。
如果解析失败，会回退到手动输入模式。
"""

import sys
import json
import re
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional


def parse_pdf(file_path: str) -> str:
    """解析 PDF 文件"""
    try:
        import PyPDF2
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ''
            for page in reader.pages:
                text += page.extract_text()
        return text
    except ImportError:
        print("错误：需要安装 PyPDF2")
        print("请运行：pip install PyPDF2")
        sys.exit(1)
    except Exception as e:
        print(f"PDF解析错误：{e}")
        return ""


def extract_with_claude(text: str) -> Optional[Dict[str, Any]]:
    """使用 Claude API 提取盖洛普信息"""
    try:
        import anthropic

        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            return None

        client = anthropic.Anthropic(api_key=api_key)

        prompt = f"""请从以下盖洛普优势报告文本中提取结构化信息，以 JSON 格式返回。

盖洛普报告文本：
{text}

请提取以下信息（如果找不到就留空）：
{{
  "tested_at": "测试日期（YYYY-MM-DD格式）",
  "top_themes": [
    {{
      "rank": 排名（1-5）,
      "name": "主题名称（中文）",
      "name_en": "主题名称（英文）",
      "domain": "所属领域（执行/影响/关系建立/战略思维）",
      "description": "主题描述"
    }}
  ],
  "domain_scores": {{
    "executing": 执行领域得分,
    "influencing": 影响领域得分,
    "relationship_building": 关系建立领域得分,
    "strategic_thinking": 战略思维领域得分
  }}
}}

只返回 JSON，不要有其他文字。"""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text

        # 尝试解析 JSON
        response_text = response_text.strip()
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]

        return json.loads(response_text)

    except Exception as e:
        print(f"⚠️  Claude API 调用失败：{e}")
        return None


def extract_with_rules(text: str) -> Dict[str, Any]:
    """
    使用规则和正则表达式从盖洛普报告中提取信息

    这是基础实现，当 LLM API 不可用时使用
    """
    info = {
        "raw_text": text,
        "extracted_at": datetime.now().isoformat(),
        "extraction_method": "规则提取",
        "tested_at": None,
        "top_themes": [],
        "domain_scores": {
            "executing": None,
            "influencing": None,
            "relationship_building": None,
            "strategic_thinking": None
        }
    }

    # 尝试提取测试日期
    date_patterns = [
        r'(\d{4})[年/-](\d{1,2})[月/-](\d{1,2})',
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
    ]
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                if '-' in match.group(0):
                    info["tested_at"] = match.group(0)
                else:
                    # 中文格式
                    info["tested_at"] = f"{match.group(1)}-{match.group(2).zfill(2)}-{match.group(3).zfill(2)}"
                break
            except:
                pass

    # 尝试提取前5大主题
    # 盖洛普报告格式通常是："1. 主题Name (ThemeName)"
    theme_pattern = r'(\d+)\.\s*([^\(]+)\s*(?:\(([^\)]+)\))?'
    themes_found = re.findall(theme_pattern, text)

    # 盖洛普34个主题的中文映射（用于识别）
    theme_domains = {
        # 执行领域
        "成就": "执行", "统筹": "执行", "信仰": "执行", "公平": "执行",
        "审慎": "执行", "专注": "执行", "纪律": "执行", "责任": "执行",
        # 影响领域
        "行动": "影响", "统率": "影响", "沟通": "影响", "竞争": "影响",
        "完美": "影响", "自信": "影响", "取悦": "影响",
        # 关系建立领域
        "适应": "关系建立", "关联": "关系建立", "个别": "关系建立",
        "搜集": "关系建立", "体谅": "关系建立", "交往": "关系建立",
        "和谐": "关系建立",
        # 战略思维领域
        "分析": "战略思维", "安排": "战略思维", "回顾": "战略思维",
        "前瞻": "战略思维", "理念": "战略思维", "学习": "战略思维",
        "战略": "战略思维", "思维": "战略思维"
    }

    for rank, theme_name, theme_name_en in themes_found[:5]:
        theme_name = theme_name.strip()
        domain = theme_domains.get(theme_name, "未知")

        info["top_themes"].append({
            "rank": int(rank),
            "name": theme_name,
            "name_en": theme_name_en.strip() if theme_name_en else "",
            "domain": domain,
            "description": ""
        })

    # 尝试提取四大领域得分
    # 格式可能是："执行: 22" 或 "Executing: 22"
    score_patterns = [
        r'执行[：:]\s*(\d+)',
        r'影响[：:]\s*(\d+)',
        r'关系建立[：:]\s*(\d+)',
        r'战略思维[：:]\s*(\d+)',
    ]

    domain_mapping = {
        "执行": "executing",
        "影响": "influencing",
        "关系建立": "relationship_building",
        "战略思维": "strategic_thinking"
    }

    for pattern in score_patterns:
        match = re.search(pattern, text)
        if match:
            domain_cn = pattern.split('[')[0].split('（')[0]
            domain_en = domain_mapping.get(domain_cn)
            if domain_en:
                info["domain_scores"][domain_en] = int(match.group(1))

    return info


def manual_input_mode() -> Dict[str, Any]:
    """
    手动输入模式

    当自动解析失败时，提供交互式输入
    """
    print("\n📝 盖洛普优势手动输入模式\n")

    info = {
        "tested_at": None,
        "top_themes": [],
        "domain_scores": {
            "executing": None,
            "influencing": None,
            "relationship_building": None,
            "strategic_thinking": None
        }
    }

    # 测试日期
    while True:
        date_input = input("测试日期（YYYY-MM-DD，直接回车跳过）：").strip()
        if not date_input:
            break
        try:
            # 验证日期格式
            datetime.strptime(date_input, "%Y-%m-%d")
            info["tested_at"] = date_input
            break
        except ValueError:
            print("❌ 日期格式不正确，请使用 YYYY-MM-DD 格式")

    # 前5大主题
    print("\n📊 前5大优势主题")
    domain_options = {
        "1": "执行",
        "2": "影响",
        "3": "关系建立",
        "4": "战略思维"
    }

    for i in range(1, 6):
        print(f"\n第{i}大主题：")
        theme_name = input("  主题名称（中文）：").strip()
        if not theme_name:
            break

        theme_name_en = input("  主题名称（英文，直接回车跳过）：").strip() or ""

        print("  所属领域：")
        print("    1. 执行")
        print("    2. 影响")
        print("    3. 关系建立")
        print("    4. 战略思维")
        domain_choice = input("  选择（1-4）：").strip()
        domain = domain_options.get(domain_choice, "未知")

        description = input("  主题描述（直接回车跳过）：").strip()

        info["top_themes"].append({
            "rank": i,
            "name": theme_name,
            "name_en": theme_name_en,
            "domain": domain,
            "description": description
        })

    # 四大领域得分
    print("\n📈 四大领域得分（如果不知道就留空）")

    domain_prompts = {
        "executing": "执行",
        "influencing": "影响",
        "relationship_building": "关系建立",
        "strategic_thinking": "战略思维"
    }

    for key, prompt in domain_prompts.items():
        while True:
            score_input = input(f"  {prompt}领域得分（直接回车跳过）：").strip()
            if not score_input:
                break
            try:
                score = int(score_input)
                info["domain_scores"][key] = score
                break
            except ValueError:
                print("  ❌ 请输入数字")

    return info


def save_json(data: Dict[str, Any], output_path: str):
    """保存为 JSON 文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 已保存到：{output_path}")


def print_summary(info: Dict[str, Any]):
    """打印提取摘要"""
    print("\n📊 提取摘要：")

    if info.get("tested_at"):
        print(f"  - 测试日期：{info['tested_at']}")

    top_themes = info.get("top_themes", [])
    if top_themes:
        print(f"  - 前5大主题：")
        for theme in top_themes:
            theme_name = theme.get("name", "未知")
            domain = theme.get("domain", "未知")
            print(f"    {theme.get('rank')}. {theme_name} ({domain})")

    domain_scores = info.get("domain_scores", {})
    if any(domain_scores.values()):
        print(f"  - 四大领域得分：")
        for domain, score in domain_scores.items():
            if score:
                domain_cn = {
                    "executing": "执行",
                    "influencing": "影响",
                    "relationship_building": "关系建立",
                    "strategic_thinking": "战略思维"
                }.get(domain, domain)
                print(f"    {domain_cn}: {score}分")


def main():
    if len(sys.argv) < 2:
        print("使用方法：")
        print("  python gallup_parser.py <gallup_report.pdf>")
        print("\n示例：")
        print("  python gallup_parser.py gallup_report.pdf")
        print("  python gallup_parser.py gallup_report.pdf --output gallup_data.json")
        print("\n环境变量（可选，用于增强提取）：")
        print("  ANTHROPIC_API_KEY - Claude API key")
        sys.exit(1)

    gallup_file = sys.argv[1]

    # 解析输出路径
    output_path = None
    if len(sys.argv) >= 4 and sys.argv[2] == "--output":
        output_path = sys.argv[3]

    try:
        # 1. 解析PDF
        print(f"📄 正在解析：{gallup_file}")
        text = parse_pdf(gallup_file)

        if not text:
            print("❌ PDF解析失败或文件为空")
            use_manual = input("\n是否使用手动输入模式？(y/n): ").strip().lower()
            if use_manual == 'y':
                info = manual_input_mode()
                info["extraction_method"] = "手动输入"
            else:
                sys.exit(1)
        else:
            print(f"✅ 解析成功，共 {len(text)} 个字符")

            # 2. 尝试使用 LLM API 提取信息
            print("\n🔍 正在提取盖洛普优势信息...")

            # 尝试 Claude API
            info = extract_with_claude(text)
            extraction_method = "Claude API"

            # 如果 Claude 失败，使用规则提取
            if info is None:
                print("⚠️  Claude API 不可用，使用规则提取")
                info = extract_with_rules(text)
                extraction_method = "规则提取"

                # 检查提取质量
                if not info.get("top_themes"):
                    print("⚠️  规则提取未能识别主题")
                    use_manual = input("\n是否使用手动输入模式？(y/n): ").strip().lower()
                    if use_manual == 'y':
                        info = manual_input_mode()
                        extraction_method = "手动输入"
            else:
                print(f"✅ 使用 Claude API 提取成功")

            info["extraction_method"] = extraction_method

        # 添加元数据
        info["extracted_at"] = datetime.now().isoformat()
        info["source_file"] = gallup_file

        # 3. 保存结果
        if not output_path:
            output_path = Path(gallup_file).stem + "_gallup.json"
        save_json(info, output_path)

        # 4. 显示摘要
        print_summary(info)

        print(f"\n💡 提示：使用 {extraction_method} 进行提取")
        if extraction_method == "规则提取":
            print("   建议：设置 ANTHROPIC_API_KEY 环境变量以获得更好的提取效果")
        elif extraction_method == "手动输入":
            print("   建议：下次可以尝试设置 ANTHROPIC_API_KEY 进行自动提取")

    except Exception as e:
        print(f"❌ 错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
