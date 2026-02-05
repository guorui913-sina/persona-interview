#!/usr/bin/env python3
"""
成长回顾系统 - 周期性生成成长报告，追踪行为模式和关键指标

特点：
- 从画像中动态提取个性化指标（不是硬编码）
- 计算通用指标（适用于所有人）
- 生成周报/月报
- 趋势分析

使用方法：
    # 生成周报
    python growth_reviewer.py weekly --week 5 --persona ../interviews/my-persona.md

    # 生成月报
    python growth_reviewer.py monthly --month 2 --persona ../interviews/my-persona.md

    # 查看指标趋势
    python growth_reviewer.py trends --days 90

    # 提取画像中的元数据
    python growth_reviewer.py extract-metadata --persona ../interviews/my-persona.md
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict, Counter


def get_decision_dir() -> Path:
    """获取决策记录目录"""
    script_dir = Path(__file__).parent.parent
    decision_dir = script_dir / "data" / "decisions"
    return decision_dir


def get_review_dir() -> Path:
    """获取成长回顾目录"""
    script_dir = Path(__file__).parent.parent
    review_dir = script_dir / "data" / "reviews"
    review_dir.mkdir(parents=True, exist_ok=True)
    return review_dir


def load_all_decisions(days: Optional[int] = None) -> List[Dict[str, Any]]:
    """加载所有决策记录"""
    decision_dir = get_decision_dir()
    decisions = []

    cutoff_date = None
    if days:
        cutoff_date = datetime.now() - timedelta(days=days)

    for file_path in decision_dir.glob("*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                decision = json.load(f)
                decision_timestamp = datetime.fromisoformat(decision["timestamp"])

                if cutoff_date is None or decision_timestamp >= cutoff_date:
                    decisions.append(decision)
        except Exception as e:
            print(f"⚠️  警告：无法加载 {file_path.name}: {e}")

    # 按时间排序
    decisions.sort(key=lambda x: x["timestamp"], reverse=True)
    return decisions


def extract_persona_metadata(persona_path: str) -> Dict[str, Any]:
    """
    从画像文件中提取元数据

    提取内容：
    1. 行为模式（behavioral_patterns）
    2. 盲区（blind_spots）
    3. 核心劣势（weaknesses）
    4. 决策关键词（decision_keywords）
    5. 触发词（triggers）
    """
    metadata = {
        "behavioral_patterns": [],
        "blind_spots": [],
        "weaknesses": [],
        "decision_keywords": [],
        "triggers": [],
        "improvement_areas": []
    }

    try:
        with open(persona_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取行为模式
        pattern_section = re.search(r'### 行为模式\n+(.*?)(?=\n###|\n##|$)', content, re.DOTALL)
        if pattern_section:
            patterns = re.findall(r'\*\*([\d\.\s]+.*?)\*\*\s*\n', pattern_section.group(1))
            metadata["behavioral_patterns"] = [p.strip() for p in patterns]

        # 提取盲区
        blind_section = re.search(r'### 盲区\n+(.*?)(?=\n---|\n##|$)', content, re.DOTALL)
        if blind_section:
            blinds = re.findall(r'\\d+\\.\\s+\\*\\*(.+?)\\*\\*', blind_section.group(1))
            metadata["blind_spots"] = [b.strip() for b in blinds]

        # 提取核心劣势
        weakness_section = re.search(r'## 我的核心劣势\n+(.*?)(?=\n---|\n##|$)', content, re.DOTALL)
        if weakness_section:
            weaknesses = re.findall(r'\*\*([\d\.\s]+.+?)\*\*\s+�?', weakness_section.group(1))
            metadata["weaknesses"] = [w.strip() for w in weaknesses]

        # 提取决策关键词（从"当我说"或"当我说X时"中提取）
        triggers = re.findall(r'当(?:我)?说"?([^\"]+)"?', content)
        metadata["triggers"] = list(set(triggers))  # 去重

        # 提取高风险关键词
        high_risk_keywords = re.findall(r'提到.*?关键词.*?[:：]\s*([^\n]+)', content)
        if high_risk_keywords:
            keywords = re.findall(r'["\uff1c]([\u4e00-\u9fa5A-Za-z]+)["\uff1c]', high_risk_keywords[0])
            metadata["decision_keywords"] = keywords

        # 提取改进领域（从"待改进"、"需要改进"等部分）
        improvement_patterns = [
            r'\*\*待改进\*\*[:：]\s*([^\n]+)',
            r'需要改进[:：]\s*([^\n]+)',
            r'改进建议[:：]\s*([^\n]+)'
        ]
        for pattern in improvement_patterns:
            matches = re.findall(pattern, content)
            metadata["improvement_areas"].extend([m.strip() for m in matches])

        print(f"✅ 成功从画像中提取元数据：")
        print(f"  - 行为模式: {len(metadata['behavioral_patterns'])} 个")
        print(f"  - 盲区: {len(metadata['blind_spots'])} 个")
        print(f"  - 核心劣势: {len(metadata['weaknesses'])} 个")
        print(f"  - 触发词: {len(metadata['triggers'])} 个")
        print(f"  - 决策关键词: {len(metadata['decision_keywords'])} 个")

    except Exception as e:
        print(f"⚠️  警告：无法从画像中提取元数据: {e}")

    return metadata


def calculate_generic_metrics(decisions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    计算通用指标（适用于所有人）

    通用指标：
    1. 决策类型分布
    2. 情感因素统计
    3. 风险等级分布
    4. 决策结果状态
    """
    if not decisions:
        return {}

    metrics = {
        "total_decisions": len(decisions),
        "by_type": defaultdict(int),
        "by_risk": defaultdict(int),
        "emotion_stats": {
            "high_emotion_count": 0,  # 情感占比>50%
            "avg_emotion_ratio": 0.0,
            "emotion_distribution": []
        },
        "outcome_stats": defaultdict(int)
    }

    emotion_ratios = []

    for decision in decisions:
        # 决策类型统计
        dtype = decision.get("type", "unknown")
        metrics["by_type"][dtype] += 1

        # 风险等级统计
        risk = decision.get("risk_level", "unknown")
        metrics["by_risk"][risk] += 1

        # 情感因素统计
        emotion_ratio = decision.get("emotion_ratio", 0.0)
        emotion_ratios.append(emotion_ratio)
        metrics["emotion_stats"]["emotion_distribution"].append(emotion_ratio)
        if emotion_ratio > 0.5:
            metrics["emotion_stats"]["high_emotion_count"] += 1

        # 决策结果统计
        outcome = decision.get("outcome", "pending")
        metrics["outcome_stats"][outcome] += 1

    # 计算平均情感占比
    if emotion_ratios:
        metrics["emotion_stats"]["avg_emotion_ratio"] = sum(emotion_ratios) / len(emotion_ratios)

    # 转换defaultdict为普通dict
    metrics["by_type"] = dict(metrics["by_type"])
    metrics["by_risk"] = dict(metrics["by_risk"])
    metrics["outcome_stats"] = dict(metrics["outcome_stats"])

    return metrics


def calculate_personalized_metrics(
    decisions: List[Dict[str, Any]],
    persona_metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """
    计算个性化指标（基于画像元数据）

    个性化指标：
    1. 触发词出现次数
    2. 行为模式重复检测
    3. 盲区相关的决策
    """
    metrics = {
        "trigger_matches": defaultdict(int),
        "pattern_repetitions": [],
        "blind_spot_violations": defaultdict(int)
    }

    # 提取触发词
    triggers = persona_metadata.get("triggers", [])
    decision_keywords = persona_metadata.get("decision_keywords", [])

    for decision in decisions:
        description = decision.get("description", "").lower()

        # 检测触发词
        for trigger in triggers:
            if trigger.lower() in description:
                metrics["trigger_matches"][trigger] += 1

        # 检测决策关键词
        for keyword in decision_keywords:
            if keyword.lower() in description:
                metrics["trigger_matches"][keyword] += 1

        # 检测盲区相关（高风险且情感占比高的决策）
        if decision.get("risk_level") == "high" and decision.get("emotion_ratio", 0) > 0.5:
            blind_spot = "情感劫持"
            metrics["blind_spot_violations"][blind_spot] += 1

    # 转换defaultdict为普通dict
    metrics["trigger_matches"] = dict(metrics["trigger_matches"])
    metrics["blind_spot_violations"] = dict(metrics["blind_spot_violations"])

    return metrics


def generate_weekly_report(
    week_num: int,
    persona_path: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> str:
    """生成周报"""
    print(f"\n📊 正在生成第 {week_num} 周成长报告...")

    # 计算本周日期范围
    if not start_date:
        # 假设每周从周一开始
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        start_date = start_of_week - timedelta(weeks=week_num - 1)
        end_date = start_date + timedelta(days=6)

    # 加载本周决策
    days_diff = (end_date - start_date).days + 1
    decisions = load_all_decisions(days=days_diff)
    week_decisions = [
        d for d in decisions
        if start_date <= datetime.fromisoformat(d["timestamp"]) <= end_date
    ]

    # 提取画像元数据
    persona_metadata = extract_persona_metadata(persona_path)

    # 计算指标
    generic_metrics = calculate_generic_metrics(week_decisions)
    personalized_metrics = calculate_personalized_metrics(week_decisions, persona_metadata)

    # 生成报告
    report_lines = [
        f"# 成长周报（第{week_num}周：{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}）\n",
        "## 📊 决策追踪\n",
        f"- **本周记录决策**：{len(week_decisions)} 个"
    ]

    if generic_metrics:
        report_lines.extend([
            f"- **生命级决策**：{generic_metrics['by_type'].get('life_level', 0)} 个",
            f"- **重要决策**：{generic_metrics['by_type'].get('important', 0)} 个",
            f"- **日常决策**：{generic_metrics['by_type'].get('daily', 0)} 个",
            ""
        ])

    # 具体决策列表
    if week_decisions:
        report_lines.extend([
            "### 本周决策详情\n"
        ])

        for i, decision in enumerate(week_decisions, 1):
            timestamp = datetime.fromisoformat(decision["timestamp"]).strftime("%Y-%m-%d %H:%M")
            dtype = decision.get("type", "unknown")
            risk_level = decision.get("risk_level", "unknown")
            emotion_ratio = decision.get("emotion_ratio", 0.0)
            description = decision.get("description", "")
            emotional_factors = decision.get("emotional_factors", [])
            outcome = decision.get("outcome", "pending")
            decision_id = decision.get("decision_id", "unknown")

            # 风险等级标签
            risk_emoji = {
                "high": "🔴",
                "medium": "🟡",
                "low": "🟢"
            }.get(risk_level, "⚪")

            # 决策类型标签
            type_label = {
                "life_level": "生命级",
                "important": "重要",
                "daily": "日常"
            }.get(dtype, dtype)

            report_lines.extend([
                f"#### {i}. {description}",
                f"- **ID**：`{decision_id}`",
                f"- **时间**：{timestamp}",
                f"- **类型**：{type_label} | **风险**：{risk_emoji} {risk_level.upper()}",
                f"- **情感因素**：{emotion_ratio*100:.0f}%{' (' + ', '.join(emotional_factors) + ')' if emotional_factors else '无'}",
                f"- **状态**：{outcome}",
                ""
            ])

    # 行为模式分析
    report_lines.extend([
        "## 🔍 行为模式分析\n"
    ])

    if personalized_metrics.get("trigger_matches"):
        report_lines.append("**触发的关键词/模式**：")
        for trigger, count in sorted(
            personalized_metrics["trigger_matches"].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            report_lines.append(f"- \"{trigger}\": {count} 次")
        report_lines.append("")

    if personalized_metrics.get("blind_spot_violations"):
        report_lines.append("**⚠️ 盲区触发**：")
        for blind_spot, count in personalized_metrics["blind_spot_violations"].items():
            report_lines.append(f"- {blind_spot}: {count} 次")
        report_lines.append("")

    if not personalized_metrics.get("trigger_matches") and not personalized_metrics.get("blind_spot_violations"):
        report_lines.append("✅ 本周无明显行为模式重复\n")

    # 指标追踪
    report_lines.extend([
        "## 📈 指标追踪\n",
        "| 指标 | 本周 | 说明 |",
        "|------|------|------|"
    ])

    if generic_metrics:
        total = generic_metrics.get("total_decisions", 0)
        high_emotion = generic_metrics.get("emotion_stats", {}).get("high_emotion_count", 0)
        avg_emotion = generic_metrics.get("emotion_stats", {}).get("avg_emotion_ratio", 0.0)

        emotion_hijack_rate = (high_emotion / total * 100) if total > 0 else 0

        report_lines.extend([
            f"| 决策总数 | {total} | 本周记录的决策数量 |",
            f"| 高情感决策 | {high_emotion} ({emotion_hijack_rate:.0f}%) | 情感占比>50%的决策 |",
            f"| 平均情感占比 | {avg_emotion*100:.0f}% | 所有决策的平均情感因素 |"
        ])

    # 画像对比
    report_lines.extend([
        "",
        "## 🎯 画像对比\n"
    ])

    if persona_metadata.get("behavioral_patterns"):
        report_lines.append("**对比画像中的行为模式**：")
        for i, pattern in enumerate(persona_metadata["behavioral_patterns"][:3], 1):
            report_lines.append(f"{i}. {pattern}")
        report_lines.append("")

    if persona_metadata.get("blind_spots"):
        report_lines.append("**对比画像中的盲区**：")
        for i, blind in enumerate(persona_metadata["blind_spots"][:3], 1):
            report_lines.append(f"{i}. {blind}")
        report_lines.append("")

    # 下周建议
    report_lines.extend([
        "## 💡 下周建议\n"
    ])

    suggestions = []

    if generic_metrics and generic_metrics.get("emotion_stats", {}).get("high_emotion_count", 0) > 0:
        suggestions.append("1. 加强冷静期执行：重大决策前至少冷静2-3天")

    if personalized_metrics.get("trigger_matches"):
        top_trigger = max(
            personalized_metrics["trigger_matches"].items(),
            key=lambda x: x[1]
        )
        suggestions.append(f"2. 注意触发词：\"{top_trigger[0]}\" 出现 {top_trigger[1]} 次，决策前先做风险评估")

    if generic_metrics and generic_metrics.get("by_risk", {}).get("high", 0) > 0:
        suggestions.append("3. 高风险决策管理：确保完成所有必要行动（列出反对理由、咨询他人、最坏情况推演）")

    if not suggestions:
        suggestions.append("继续保持理性决策的习惯！")

    report_lines.extend(suggestions)
    report_lines.append("")
    report_lines.append("---")
    report_lines.append(f"\n**生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}")

    return "\n".join(report_lines)


def save_report(report: str, report_type: str, identifier: int) -> Path:
    """保存报告到文件"""
    review_dir = get_review_dir()

    timestamp = datetime.now().strftime("%Y%m%d")
    filename = f"{report_type}_{identifier}_{timestamp}.md"
    file_path = review_dir / filename

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(report)

    return file_path


def main():
    import argparse

    parser = argparse.ArgumentParser(description="成长回顾系统")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # weekly命令
    weekly_parser = subparsers.add_parser("weekly", help="生成周报")
    weekly_parser.add_argument("--week", type=int, required=True, help="周数")
    weekly_parser.add_argument("--persona", required=True, help="画像文件路径")

    # monthly命令
    monthly_parser = subparsers.add_parser("monthly", help="生成月报")
    monthly_parser.add_argument("--month", type=int, required=True, help="月数")
    monthly_parser.add_argument("--persona", required=True, help="画像文件路径")

    # trends命令
    trends_parser = subparsers.add_parser("trends", help="查看指标趋势")
    trends_parser.add_argument("--days", type=int, default=90, help="查看最近多少天")

    # extract-metadata命令
    metadata_parser = subparsers.add_parser("extract-metadata", help="提取画像元数据")
    metadata_parser.add_argument("--persona", required=True, help="画像文件路径")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "weekly":
            report = generate_weekly_report(
                week_num=args.week,
                persona_path=args.persona
            )
            file_path = save_report(report, "weekly", args.week)
            print(f"\n✅ 周报已保存到：{file_path}")

        elif args.command == "monthly":
            print(f"📊 正在生成第 {args.month} 月成长报告...")
            # TODO: 实现月报生成
            print("⚠️  月报功能开发中...")

        elif args.command == "trends":
            print(f"📈 查看最近 {args.days} 天的指标趋势...")
            decisions = load_all_decisions(days=args.days)
            metrics = calculate_generic_metrics(decisions)

            print(f"\n总决策数：{metrics.get('total_decisions', 0)}")
            print(f"决策类型分布：{metrics.get('by_type', {})}")
            print(f"风险等级分布：{metrics.get('by_risk', {})}")

        elif args.command == "extract-metadata":
            print(f"\n📋 正在提取画像元数据...")
            metadata = extract_persona_metadata(args.persona)

            print(f"\n元数据：")
            print(json.dumps(metadata, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"❌ 错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
