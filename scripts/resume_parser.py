#!/usr/bin/env python3
"""
简历解析器 - 从简历中提取结构化信息（增强版）

支持格式：PDF, DOCX, Markdown
输出格式：JSON

特性：
- 自动检测可用的 LLM API（Claude、OpenAI）
- 使用 LLM 进行智能信息提取
- 回退到规则提取（当 API 不可用时）

使用方法：
    python resume_parser.py resume.pdf
    python resume_parser.py resume.docx
    python resume_parser.py resume.md

环境变量：
    ANTHROPIC_API_KEY - Claude API key
    OPENAI_API_KEY - OpenAI API key
"""

import sys
import json
import re
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional


def parse_markdown(file_path: str) -> str:
    """解析 Markdown 文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def parse_docx(file_path: str) -> str:
    """解析 DOCX 文件"""
    try:
        from docx import Document
        doc = Document(file_path)
        return '\n'.join([para.text for para in doc.paragraphs])
    except ImportError:
        print("错误：需要安装 python-docx")
        print("请运行：pip install python-docx")
        sys.exit(1)


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


def parse_resume(file_path: str) -> str:
    """根据文件扩展名选择解析方法"""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"文件不存在：{file_path}")

    suffix = path.suffix.lower()

    if suffix == '.md' or suffix == '.markdown':
        return parse_markdown(file_path)
    elif suffix == '.docx':
        return parse_docx(file_path)
    elif suffix == '.pdf':
        return parse_pdf(file_path)
    else:
        raise ValueError(f"不支持的文件格式：{suffix}")


def extract_with_claude(text: str) -> Optional[Dict[str, Any]]:
    """使用 Claude API 提取简历信息"""
    try:
        import anthropic

        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            return None

        client = anthropic.Anthropic(api_key=api_key)

        prompt = f"""请从以下简历文本中提取结构化信息，以 JSON 格式返回。

简历文本：
{text}

请提取以下信息（如果找不到就留空或返回空数组）：
{{
  "basics": {{
    "name": "姓名",
    "gender": "性别",
    "age": "年龄",
    "email": "邮箱",
    "phone": "电话",
    "location": "所在地"
  }},
  "summary": "个人简介（一句话）",
  "work_history": [
    {{
      "company": "公司名称",
      "position": "职位",
      "department": "部门",
      "start_date": "开始时间",
      "end_date": "结束时间",
      "location": "地点",
      "description": "工作描述（数组，每条一个要点）"
    }}
  ],
  "education": [
    {{
      "school": "学校名称",
      "major": "专业",
      "degree": "学位",
      "start_date": "开始时间",
      "end_date": "结束时间"
    }}
  ],
  "skills": ["技能1", "技能2", ...],
  "projects": [
    {{
      "name": "项目名称",
      "description": "项目描述",
      "role": "角色",
      "technologies": ["技术1", "技术2"]
    }}
  ],
  "awards": ["奖项1", "奖项2", ...],
  "languages": ["语言1", "语言2", ...]
}}

只返回 JSON，不要有其他文字。"""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text

        # 尝试解析 JSON
        # 移除可能的 markdown 代码块标记
        response_text = response_text.strip()
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]

        return json.loads(response_text)

    except Exception as e:
        print(f"⚠️  Claude API 调用失败：{e}")
        return None


def extract_with_openai(text: str) -> Optional[Dict[str, Any]]:
    """使用 OpenAI API 提取简历信息"""
    try:
        import openai

        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            return None

        client = openai.OpenAI(api_key=api_key)

        prompt = f"""请从以下简历文本中提取结构化信息，以 JSON 格式返回。

简历文本：
{text}}

请提取以下信息（如果找不到就留空或返回空数组）：
{{
  "basics": {{
    "name": "姓名",
    "gender": "性别",
    "age": "年龄",
    "email": "邮箱",
    "phone": "电话",
    "location": "所在地"
  }},
  "summary": "个人简介（一句话）",
  "work_history": [
    {{
      "company": "公司名称",
      "position": "职位",
      "department": "部门",
      "start_date": "开始时间",
      "end_date": "结束时间",
      "location": "地点",
      "description": "工作描述（数组，每条一个要点）"
    }}
  ],
  "education": [
    {{
      "school": "学校名称",
      "major": "专业",
      "degree": "学位",
      "start_date": "开始时间",
      "end_date": "结束时间"
    }}
  ],
  "skills": ["技能1", "技能2", ...],
  "projects": [
    {{
      "name": "项目名称",
      "description": "项目描述",
      "role": "角色",
      "technologies": ["技术1", "技术2"]
    }}
  ],
  "awards": ["奖项1", "奖项2", ...],
  "languages": ["语言1", "语言2", ...]
}}

只返回 JSON，不要有其他文字。"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=4096
        )

        response_text = response.choices[0].message.content

        # 尝试解析 JSON
        response_text = response_text.strip()
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]

        return json.loads(response_text)

    except Exception as e:
        print(f"⚠️  OpenAI API 调用失败：{e}")
        return None


def extract_with_rules(text: str) -> Dict[str, Any]:
    """
    使用规则和正则表达式从简历文本中提取关键信息

    这是基础实现，当 LLM API 不可用时使用
    """
    info = {
        "raw_text": text,
        "extracted_at": datetime.now().isoformat(),
        "extraction_method": "rules",
        "basics": {},
        "work_history": [],
        "education": [],
        "skills": [],
        "projects": []
    }

    lines = text.split('\n')
    current_section = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 识别章节标题（简单规则：常见标题）
        if any(keyword in line for keyword in ['工作经历', '工作体验', '经历', 'Work Experience', 'Experience', '职业经历']):
            current_section = 'work'
            continue
        elif any(keyword in line for keyword in ['教育', '学历', 'Education']):
            current_section = 'education'
            continue
        elif any(keyword in line for keyword in ['技能', '专长', 'Skills', '技术栈']):
            current_section = 'skills'
            continue
        elif any(keyword in line for keyword in ['项目', 'Project', 'Projects']):
            current_section = 'projects'
            continue

        # 提取信息（简化版）
        if current_section == 'work':
            parts = line.split()
            if len(parts) >= 2:
                info["work_history"].append({
                    "company": parts[0],
                    "position": parts[1] if len(parts) > 1 else "",
                    "description": line
                })
        elif current_section == 'skills':
            skills = re.split(r'[,、|]', line)
            info["skills"].extend([s.strip() for s in skills if s.strip()])

    # 尝试提取基本信息（名字、邮箱、电话）
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if emails:
        info["basics"]["email"] = emails[0]

    phone_pattern = r'1[3-9]\d{9}'
    phones = re.findall(phone_pattern, text)
    if phones:
        info["basics"]["phone"] = phones[0]

    return info


def save_json(data: Dict[str, Any], output_path: str):
    """保存为 JSON 文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 已保存到：{output_path}")


def print_summary(info: Dict[str, Any]):
    """打印提取摘要"""
    print("\n📊 提取摘要：")

    basics = info.get('basics', {})
    if basics.get('name'):
        print(f"  - 姓名：{basics['name']}")
    if basics.get('email'):
        print(f"  - 邮箱：{basics['email']}")
    if basics.get('phone'):
        print(f"  - 电话：{basics['phone']}")

    work_history = info.get('work_history', [])
    if work_history:
        print(f"  - 工作经历：{len(work_history)} 条")
        for job in work_history[:3]:  # 只显示前3个
            print(f"    • {job.get('company', 'N/A')} - {job.get('position', 'N/A')}")

    skills = info.get('skills', [])
    if skills:
        print(f"  - 技能：{len(skills)} 项")
        if len(skills) <= 5:
            for skill in skills:
                print(f"    • {skill}")
        else:
            for skill in skills[:5]:
                print(f"    • {skill}")
            print(f"    • ... 还有 {len(skills) - 5} 项")

    education = info.get('education', [])
    if education:
        print(f"  - 教育背景：{len(education)} 条")
        for edu in education:
            print(f"    • {edu.get('school', 'N/A')} - {edu.get('major', 'N/A')}")


def main():
    if len(sys.argv) < 2:
        print("使用方法：")
        print("  python resume_parser.py <resume_file>")
        print("\n示例：")
        print("  python resume_parser.py resume.pdf")
        print("  python resume_parser.py resume.docx")
        print("  python resume_parser.py resume.md")
        print("\n环境变量（可选，用于增强提取）：")
        print("  ANTHROPIC_API_KEY - Claude API key")
        print("  OPENAI_API_KEY - OpenAI API key")
        sys.exit(1)

    resume_file = sys.argv[1]

    try:
        # 1. 解析简历
        print(f"📄 正在解析：{resume_file}")
        text = parse_resume(resume_file)
        print(f"✅ 解析成功，共 {len(text)} 个字符")

        # 2. 尝试使用 LLM API 提取信息
        print("\n🔍 正在提取关键信息...")

        # 尝试 Claude API
        info = extract_with_claude(text)
        extraction_method = "Claude API"

        # 如果 Claude 失败，尝试 OpenAI
        if info is None:
            info = extract_with_openai(text)
            extraction_method = "OpenAI API"

        # 如果 LLM 都失败，使用规则提取
        if info is None:
            print("⚠️  LLM API 不可用，使用规则提取（效果较差）")
            info = extract_with_rules(text)
            extraction_method = "规则提取"
        else:
            print(f"✅ 使用 {extraction_method} 提取成功")

        # 添加元数据
        info['raw_text'] = text
        info['extracted_at'] = datetime.now().isoformat()
        info['extraction_method'] = extraction_method

        # 3. 保存结果
        output_file = Path(resume_file).stem + "_parsed.json"
        save_json(info, output_file)

        # 4. 显示摘要
        print_summary(info)

        print(f"\n💡 提示：使用 {extraction_method} 进行提取")
        if extraction_method == "规则提取":
            print("   建议：设置 ANTHROPIC_API_KEY 或 OPENAI_API_KEY 环境变量以获得更好的提取效果")

    except Exception as e:
        print(f"❌ 错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
