#!/usr/bin/env python3
"""
简历解析器 - 从简历中提取结构化信息

支持格式：PDF, DOCX, Markdown
输出格式：JSON

使用方法：
    python resume_parser.py resume.pdf
    python resume_parser.py resume.docx
    python resume_parser.py resume.md
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


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


def extract_resume_info(text: str) -> Dict[str, Any]:
    """
    使用规则和正则表达式从简历文本中提取关键信息

    这是一个基础实现。对于更准确的提取，建议使用 LLM API。
    """

    info = {
        "raw_text": text,
        "extracted_at": datetime.now().isoformat(),
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
        if any(keyword in line for keyword in ['工作经历', '工作体验', '经历', 'Work Experience', 'Experience']):
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

        # 提取信息（简化版，实际应用中建议用 LLM）
        if current_section == 'work':
            # 简单的提取：假设格式为 "公司 职位 时间"
            parts = line.split()
            if len(parts) >= 2:
                info["work_history"].append({
                    "company": parts[0],
                    "position": parts[1] if len(parts) > 1 else "",
                    "description": line
                })
        elif current_section == 'skills':
            # 分割技能列表
            skills = re.split(r'[,、|]', line)
            info["skills"].extend([s.strip() for s in skills if s.strip()])

    # 尝试提取基本信息（名字、邮箱、电话）
    # 邮箱
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if emails:
        info["basics"]["email"] = emails[0]

    # 电话（简单匹配）
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


def main():
    if len(sys.argv) < 2:
        print("使用方法：")
        print("  python resume_parser.py <resume_file>")
        print("\n示例：")
        print("  python resume_parser.py resume.pdf")
        print("  python resume_parser.py resume.docx")
        print("  python resume_parser.py resume.md")
        sys.exit(1)

    resume_file = sys.argv[1]

    try:
        # 1. 解析简历
        print(f"📄 正在解析：{resume_file}")
        text = parse_resume(resume_file)
        print(f"✅ 解析成功，共 {len(text)} 个字符")

        # 2. 提取信息
        print("🔍 正在提取关键信息...")
        info = extract_resume_info(text)

        # 3. 保存结果
        output_file = Path(resume_file).stem + "_parsed.json"
        save_json(info, output_file)

        # 4. 显示摘要
        print("\n📊 提取摘要：")
        print(f"  - 邮箱：{info['basics'].get('email', '未找到')}")
        print(f"  - 电话：{info['basics'].get('phone', '未找到')}")
        print(f"  - 工作经历：{len(info['work_history'])} 条")
        print(f"  - 技能：{len(info['skills'])} 项")

        # 提示：建议使用 LLM 进行更准确的提取
        print("\n💡 提示：当前使用规则提取，建议结合 LLM API 进行更准确的解析")
        print("   可以使用 Claude API、OpenAI API 等增强提取效果")

    except Exception as e:
        print(f"❌ 错误：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
