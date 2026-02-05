#!/usr/bin/env python3
"""
版本对比工具 - 对比两个版本的画像，发现变化和趋势

使用方法：
    python version_comparer.py list
    python version_comparer.py compare --old v1.1 --new v1.2
    python version_comparer.py show --version v1.2

功能：
- 列出所有版本
- 对比两个版本
- 查看版本详情
- 生成对比报告
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional


def find_persona_versions(interview_dir: str) -> List[Dict[str, Any]]:
    """查找所有画像版本"""
    interviews_path = Path(interview_dir)
    versions = []

    # 查找所有 my-persona-*.md 文件
    for file in interviews_path.glob("my-persona-*.md"):
        # 提取版本号
        match = re.search(r'v(\d+)\.(\d+)', file.name)
        if match:
            major, minor = int(match.group(1)), int(match.group(2))
            version = f"v{major}.{minor}"

            # 读取文件获取版本名称
            version_name = ""
            with open(file, 'r', encoding='utf-8') as f:
                for line in f:
                    if '版本名称' in line or '整合版' in line or '访谈版' in line:
                        # 提取版本名称
                        name_match = re.search(r'[\"*](.+?)[\"*]', line)
                        if name_match:
                            version_name = name_match.group(1)
                            break

            versions.append({
                "version": version,
                "major": major,
                "minor": minor,
                "file": file.name,
                "version_name": version_name
            })

    # 按版本号排序
    versions.sort(key=lambda x: (x["major"], x["minor"]))
    return versions


def load_version_data(interview_dir: str, version: str) -> Optional[Dict[str, Any]]:
    """加载指定版本的数据"""
    versions = find_persona_versions(interview_dir)

    # 查找匹配的版本
    target_version = None
    for v in versions:
        if v["version"] == version:
            target_version = v
            break

    if not target_version:
        return None

    file_path = Path(interview_dir) / target_version["file"]

    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取基本信息
    data = {
        "version": target_version["version"],
        "version_name": target_version["version_name"],
        "file": file_path.name,
        "created_at": None,
        "data_sources": [],
        "summary": "",
        "key_findings": [],
        "strengths": [],
        "weaknesses": [],
        "suitable_directions": [],
        "unsuitable_directions": []
    }

    # 提取创建时间
    date_match = re.search(r'\*\*生成时间\*\*[：:]\s*(\d{4}-\d{2}-\d{2})', content)
    if date_match:
        data["created_at"] = date_match.group(1)

    # 提取数据源
    sources_match = re.search(r'\*\*数据来源\*\*[：:]\s*(.+)', content)
    if sources_match:
        sources_text = sources_match.group(1)
        data["data_sources"] = [s.strip() for s in sources_text.split('+')]

    # 提取摘要
    summary_match = re.search(r'>\s*(.+)', content)
    if summary_match:
        data["summary"] = summary_match.group(1).strip()

    # 提取核心发现
    findings_section = re.search(r'##\s+核心发现.*?(?=##|\Z)', content, re.DOTALL)
    if findings_section:
        findings_lines = findings_section.group(0).split('\n')
        for line in findings_lines:
            line = line.strip()
            if line.startswith('-') or line.startswith('•'):
                data["key_findings"].append(line.lstrip('-*• ').strip())

    # 提取优势
    strengths_match = re.search(r'##\s+我的核心优势.*?(?=##|\Z)', content, re.DOTALL)
    if strengths_match:
        # 提取 ⭐⭐⭐⭐⭐ 的项目
        strength_items = re.findall(r'[⭐*]{5}\s+(.+?)(?:\n|$)', strengths_match.group(0))
        data["strengths"] = [s.strip() for s in strength_items]

    # 提取劣势
    weaknesses_match = re.search(r'##\s+我的核心劣势.*?(?=##|\Z)', content, re.DOTALL)
    if weaknesses_match:
        weakness_items = re.findall(r'[-*]\s+(.+?)(?:\n|$)', weaknesses_match.group(0))
        data["weaknesses"] = [w.strip() for w in weakness_items if w.strip()]

    # 提取适合方向
    suitable_match = re.search(r'##\s+适合的职业方向.*?(?=##|\Z)', content, re.DOTALL)
    if suitable_match:
        # 提取 ⭐⭐⭐⭐⭐ 的项目
        suitable_items = re.findall(r'[⭐*]{5}\s+(.+?)(?:\n|$)', suitable_match.group(0))
        data["suitable_directions"] = [s.strip() for s in suitable_items]

    # 提取不适合方向
    unsuitable_items = re.findall(r'[-*]\s+❌\s+(.+?)(?:\n|$)', content)
    data["unsuitable_directions"] = [u.strip() for u in unsuitable_items if u.strip()]

    return data


def compare_versions(old_data: Dict, new_data: Dict) -> Dict[str, Any]:
    """对比两个版本"""
    comparison = {
        "old_version": old_data["version"],
        "new_version": new_data["version"],
        "comparison_date": datetime.now().strftime("%Y-%m-%d"),
        "new_data_sources": [],
        "removed_data_sources": [],
        "changes": [],
        "improvements": [],
        "new_issues": [],
        "metric_changes": []
    }

    # 对比数据源
    new_sources = set(new_data.get("data_sources", []))
    old_sources = set(old_data.get("data_sources", []))

    comparison["new_data_sources"] = list(new_sources - old_sources)
    comparison["removed_data_sources"] = list(old_sources - new_sources)

    # 检查版本历史中的changes
    # 这个需要从画像文件中读取版本历史部分

    # 对比摘要
    if old_data.get("summary") != new_data.get("summary"):
        comparison["changes"].append({
            "type": "summary",
            "description": "画像摘要已更新"
        })

    # 对比核心发现
    old_findings = set(old_data.get("key_findings", []))
    new_findings = set(new_data.get("key_findings", []))

    for finding in new_findings - old_findings:
        comparison["improvements"].append({
            "type": "new_finding",
            "description": finding
        })

    # 对比优势
    old_strengths = set(old_data.get("strengths", []))
    new_strengths = set(new_data.get("strengths", []))

    for strength in new_strengths - old_strengths:
        comparison["improvements"].append({
            "type": "new_strength",
            "description": f"新发现优势：{strength}"
        })

    # 对比劣势
    old_weaknesses = set(old_data.get("weaknesses", []))
    new_weaknesses = set(new_data.get("weaknesses", []))

    for weakness in new_weaknesses - old_weaknesses:
        comparison["new_issues"].append({
            "type": "new_weakness",
            "description": f"新发现劣势：{weakness}"
        })

    # 对比适合方向
    old_suitable = set(old_data.get("suitable_directions", []))
    new_suitable = set(new_data.get("suitable_directions", []))

    if old_suitable != new_suitable:
        comparison["changes"].append({
            "type": "career_directions",
            "description": "职业方向建议有变化"
        })

    return comparison


def generate_comparison_report(comparison: Dict, old_data: Dict, new_data: Dict) -> str:
    """生成对比报告（Markdown格式）"""
    report = []

    report.append(f"# 版本对比：{comparison['old_version']} → {comparison['new_version']}\n")
    report.append(f"**对比日期**：{comparison['comparison_date']}\n")

    # 新增数据源
    if comparison["new_data_sources"]:
        report.append("### 新增数据源")
        for source in comparison["new_data_sources"]:
            report.append(f"- ✅ 整合{source}")
        report.append("")

    # 关键发现
    report.append("### 关键发现")
    if new_data.get("summary"):
        report.append(f"**{new_data['summary']}**")
    report.append("")

    # 进步点
    if comparison["improvements"]:
        report.append("### 进步点")
        for item in comparison["improvements"]:
            if item["type"] == "new_finding":
                report.append(f"- ✅ {item['description']}")
            elif item["type"] == "new_strength":
                report.append(f"- ✅ {item['description']}")
        report.append("")

    # 新问题
    if comparison["new_issues"]:
        report.append("### 待改进")
        for item in comparison["new_issues"]:
            report.append(f"- ⏳ {item['description']}")
        report.append("")

    # 变化
    if comparison["changes"]:
        report.append("### 变化")
        for item in comparison["changes"]:
            report.append(f"- {item['description']}")
        report.append("")

    # 数据源对比
    report.append("### 数据源对比")
    report.append(f"| 数据源 | {comparison['old_version']} | {comparison['new_version']} |")
    report.append("|--------|----------|----------|")

    all_sources = set(old_data.get("data_sources", [])) | set(new_data.get("data_sources", []))
    for source in sorted(all_sources):
        old_has = "✅" if source in old_data.get("data_sources", []) else "❌"
        new_has = "✅" if source in new_data.get("data_sources", []) else "❌"
        report.append(f"| {source} | {old_has} | {new_has} |")

    return "\n".join(report)


def list_versions(interview_dir: str):
    """列出所有版本"""
    versions = find_persona_versions(interview_dir)

    print("\n📋 可用版本列表：\n")
    print(f"{'版本':<12} {'版本名称':<20} {'文件名'}")
    print("-" * 60)

    for v in versions:
        print(f"{v['version']:<12} {v['version_name']:<20} {v['file']}")

    print()


def show_version_details(interview_dir: str, version: str):
    """显示版本详情"""
    data = load_version_data(interview_dir, version)

    if not data:
        print(f"❌ 未找到版本：{version}")
        return

    print(f"\n📊 版本详情：{version}\n")
    print(f"版本名称：{data['version_name']}")
    print(f"创建时间：{data['created_at']}")
    print(f"文件：{data['file']}")

    print(f"\n数据源：")
    for source in data.get("data_sources", []):
        print(f"  - {source}")

    if data.get("summary"):
        print(f"\n摘要：\n{data['summary']}")

    if data.get("key_findings"):
        print(f"\n核心发现：")
        for finding in data["key_findings"][:5]:
            print(f"  • {finding}")

    if data.get("strengths"):
        print(f"\n核心优势：")
        for strength in data["strengths"][:5]:
            print(f"  ⭐ {strength}")

    if data.get("weaknesses"):
        print(f"\n核心劣势：")
        for weakness in data["weaknesses"][:5]:
            print(f"  • {weakness}")

    print()


def compare_versions_command(interview_dir: str, old_version: str, new_version: str, output_path: Optional[str] = None):
    """对比两个版本"""
    old_data = load_version_data(interview_dir, old_version)
    new_data = load_version_data(interview_dir, new_version)

    if not old_data:
        print(f"❌ 未找到版本：{old_version}")
        return

    if not new_data:
        print(f"❌ 未找到版本：{new_version}")
        return

    comparison = compare_versions(old_data, new_data)
    report = generate_comparison_report(comparison, old_data, new_data)

    # 输出报告
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✅ 对比报告已保存到：{output_path}\n")
    else:
        print("\n" + report)

    # 打印简要摘要
    print("\n📊 对比摘要：")
    print(f"  新增数据源：{', '.join(comparison['new_data_sources']) if comparison['new_data_sources'] else '无'}")
    print(f"  进步点：{len(comparison['improvements'])} 项")
    print(f"  新问题：{len(comparison['new_issues'])} 项")
    print(f"  变化：{len(comparison['changes'])} 项")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Persona版本对比工具")
    parser.add_argument("command", choices=["list", "compare", "show"], help="命令")

    # list命令不需要额外参数
    # compare命令需要 --old 和 --new
    # show命令需要 --version

    parser.add_argument("--old", help="旧版本（如：v1.1）")
    parser.add_argument("--new", help="新版本（如：v1.2）")
    parser.add_argument("--version", help="版本号（如：v1.2）")
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument("--interview-dir", default="interviews", help="访谈目录路径")

    args = parser.parse_args()

    interview_dir = Path(__file__).parent.parent / args.interview_dir

    if not interview_dir.exists():
        print(f"❌ 访谈目录不存在：{interview_dir}")
        sys.exit(1)

    try:
        if args.command == "list":
            list_versions(str(interview_dir))

        elif args.command == "compare":
            if not args.old or not args.new:
                print("❌ compare命令需要 --old 和 --new 参数")
                print("示例：python version_comparer.py compare --old v1.1 --new v1.2")
                sys.exit(1)

            compare_versions_command(str(interview_dir), args.old, args.new, args.output)

        elif args.command == "show":
            if not args.version:
                print("❌ show命令需要 --version 参数")
                print("示例：python version_comparer.py show --version v1.2")
                sys.exit(1)

            show_version_details(str(interview_dir), args.version)

    except Exception as e:
        print(f"❌ 错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
