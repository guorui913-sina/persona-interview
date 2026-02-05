#!/usr/bin/env python3
"""
决策追踪系统 - 记录和分析用户的决策，帮助识别模式和改进

使用方法：
    python decision_tracker.py record --type life_level --description "考虑买房"
    python decision_tracker.py history --days 30
    python decision_tracker.py analyze --pattern emotion_hijack
    python decision_tracker.py check-risk --description "我要结婚"

功能：
- 记录决策（类型、时间、理由、情感因素）
- 查看决策历史
- 分析决策模式
- 检查决策风险
"""

import sys
import json
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional


# 决策分类
DECISION_TYPES = {
    "life_level": {
        "name": "生命级决策",
        "description": "一旦失误，损失>1年收入或需要>1年才能恢复",
        "examples": ["婚姻", "买房", "生子", "职业选择", "创业"],
        "required_actions": [
            "列出3个不做的理由",
            "最坏情况推演",
            "咨询3个不同立场的人",
            "7天冷静期",
            "检查'责任'主题"
        ]
    },
    "important": {
        "name": "重要决策",
        "description": "一旦失误，损失<1年收入但需要<1年恢复",
        "examples": ["换项目", "学习新技能", "小额投资<5万"],
        "recommended_actions": [
            "列出1-2个不做的理由",
            "咨询1-2个人",
            "简单冷静期（1-2天）"
        ]
    },
    "daily": {
        "name": "日常决策",
        "description": "损失可控，可快速调整",
        "examples": ["今天学什么", "吃什么", "看什么内容"],
        "recommended_actions": ["相信直觉"]
    }
}

# 风险关键词
HIGH_RISK_KEYWORDS = ["买房", "结婚", "生子", "投资", "换工作", "创业"]
EMOTION_KEYWORDS = ["为了父母", "为了家人", "结婚需求", "应该", "必须"]
OPPORTUNITY_KEYWORDS = ["发现了", "新机会", "有个想法", "我想做"]


def get_decision_dir() -> Path:
    """获取决策记录目录"""
    script_dir = Path(__file__).parent.parent
    decision_dir = script_dir / "data" / "decisions"
    decision_dir.mkdir(parents=True, exist_ok=True)
    return decision_dir


def generate_decision_id() -> str:
    """生成决策ID"""
    now = datetime.now()
    return f"{now.strftime('%Y-%m-%d')}-{uuid.uuid4().hex[:8]}"


def record_decision(
    description: str,
    decision_type: str = "important",
    rational_analysis: str = "",
    emotional_factors: List[str] = None,
    ai_warning: str = ""
) -> Dict[str, Any]:
    """记录一个决策"""
    decision_id = generate_decision_id()
    now = datetime.now()

    # 检测情感因素
    emotion_ratio = 0.0
    if emotional_factors:
        emotion_ratio = min(len(emotional_factors) * 0.2, 1.0)  # 每个因素20%

    # 确定风险等级
    risk_level = "low"
    if decision_type == "life_level":
        risk_level = "high"
    elif emotion_ratio > 0.5:
        risk_level = "high"
    elif decision_type == "important":
        risk_level = "medium"

    decision = {
        "decision_id": decision_id,
        "timestamp": now.isoformat(),
        "type": decision_type,
        "description": description,
        "rational_analysis": rational_analysis,
        "emotional_factors": emotional_factors or [],
        "emotion_ratio": emotion_ratio,
        "risk_level": risk_level,
        "ai_warning": ai_warning,
        "required_actions": DECISION_TYPES[decision_type].get("required_actions", []) if decision_type == "life_level" else [],
        "outcome": "pending",
        "created_at": now.isoformat(),
        "updated_at": now.isoformat()
    }

    # 保存到文件
    decision_dir = get_decision_dir()
    file_path = decision_dir / f"{decision_id}.json"

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(decision, f, ensure_ascii=False, indent=2)

    return decision


def load_decision(decision_id: str) -> Optional[Dict[str, Any]]:
    """加载决策记录"""
    decision_dir = get_decision_dir()
    file_path = decision_dir / f"{decision_id}.json"

    if not file_path.exists():
        return None

    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_all_decisions(days: Optional[int] = None) -> List[Dict[str, Any]]:
    """加载所有决策记录"""
    decision_dir = get_decision_dir()
    decisions = []

    cutoff_date = None
    if days:
        cutoff_date = datetime.now() - timedelta(days=days)

    for file_path in decision_dir.glob("*.json"):
        with open(file_path, 'r', encoding='utf-8') as f:
            decision = json.load(f)
            decision_timestamp = datetime.fromisoformat(decision["timestamp"])

            # 过滤日期
            if cutoff_date is None or decision_timestamp >= cutoff_date:
                decisions.append(decision)

    # 按时间排序
    decisions.sort(key=lambda x: x["timestamp"], reverse=True)
    return decisions


def check_risk(description: str, persona_path: Optional[str] = None) -> Dict[str, Any]:
    """检查决策风险"""
    risk_assessment = {
        "description": description,
        "detected_keywords": [],
        "decision_type_suggestion": "daily",
        "emotion_factors": [],
        "emotion_ratio": 0.0,
        "risk_level": "low",
        "warnings": [],
        "required_actions": [],
        "persona_references": []
    }

    # 检测高风险关键词
    for keyword in HIGH_RISK_KEYWORDS:
        if keyword in description:
            risk_assessment["detected_keywords"].append(keyword)
            risk_assessment["decision_type_suggestion"] = "life_level"

    # 检测情感关键词
    for keyword in EMOTION_KEYWORDS:
        if keyword in description:
            risk_assessment["emotion_factors"].append(keyword)

    # 计算情感占比
    if risk_assessment["emotion_factors"]:
        risk_assessment["emotion_ratio"] = min(len(risk_assessment["emotion_factors"]) * 0.25, 1.0)

    # 确定风险等级
    if risk_assessment["decision_type_suggestion"] == "life_level":
        risk_assessment["risk_level"] = "high"
    elif risk_assessment["emotion_ratio"] > 0.5:
        risk_assessment["risk_level"] = "high"
        risk_assessment["decision_type_suggestion"] = "important"
    elif len(risk_assessment["detected_keywords"]) > 0:
        risk_assessment["risk_level"] = "medium"
        risk_assessment["decision_type_suggestion"] = "important"

    # 生成警告
    if risk_assessment["risk_level"] == "high":
        risk_assessment["warnings"].append("⚠️ 检测到高风险决策")

        if risk_assessment["emotion_ratio"] > 0.5:
            risk_assessment["warnings"].append(
                f"⚠️ 情感因素占比{risk_assessment['emotion_ratio']*100:.0f}%，可能劫持理性"
            )

        risk_assessment["warnings"].append("⚠️ 建议执行7天冷静期")

    # 必要行动
    if risk_assessment["decision_type_suggestion"] == "life_level":
        risk_assessment["required_actions"] = DECISION_TYPES["life_level"]["required_actions"]

    # 引用画像（如果提供）
    if persona_path:
        try:
            with open(persona_path, 'r', encoding='utf-8') as f:
                persona_content = f.read()

            # 提取关键引用
            if "战略规划14年" in persona_content:
                risk_assessment["persona_references"].append(
                    "你简历上写着战略规划14年，这次有做战略分析吗？"
                )

            if "盖洛普" in persona_content and "责任" in persona_content:
                risk_assessment["persona_references"].append(
                    "你盖洛普'责任'主题排名第3，是不是又在对他人的期待负责？"
                )

            if "情感劫持" in persona_content:
                risk_assessment["persona_references"].append(
                    "根据你的画像，纯理性判断准确率>2/3，情感介入往往失败。这次是什么情况？"
                )

        except Exception as e:
            print(f"⚠️  无法读取画像文件：{e}")

    return risk_assessment


def analyze_pattern(pattern: str) -> Dict[str, Any]:
    """分析决策模式"""
    decisions = load_all_decisions()

    analysis = {
        "pattern": pattern,
        "total_decisions": len(decisions),
        "findings": [],
        "recommendations": []
    }

    if pattern == "emotion_hijack":
        # 分析情感劫持模式
        emotion_decisions = [d for d in decisions if d.get("emotion_ratio", 0) > 0.5]

        analysis["findings"].append(
            f"发现{len(emotion_decisions)}个可能被情感劫持的决策（占比>50%）"
        )

        if len(emotion_decisions) > 0:
            avg_emotion = sum(d.get("emotion_ratio", 0) for d in emotion_decisions) / len(emotion_decisions)
            analysis["findings"].append(
                f"平均情感占比：{avg_emotion*100:.0f}%"
            )

        # 检查趋势
        recent_decisions = decisions[:5] if len(decisions) >= 5 else decisions
        recent_emotion_ratio = sum(d.get("emotion_ratio", 0) for d in recent_decisions) / len(recent_decisions)

        if recent_emotion_ratio > 0.3:
            analysis["recommendations"].append(
                "⚠️ 最近决策中情感因素较多，建议加强冷静期执行"
            )
        else:
            analysis["recommendations"].append(
                "✅ 最近决策较为理性，继续保持"
            )

    elif pattern == "validation":
        # 分析验证模式
        no_validation = [d for d in decisions if "验证" not in d.get("rational_analysis", "")]

        analysis["findings"].append(
            f"发现{len(no_validation)}个可能未做充分验证的决策"
        )

        if len(no_validation) > 3:
            analysis["recommendations"].append(
                "⚠️ 你经常跳过验证环节，建议每次决策前先做市场验证"
            )

    elif pattern == "multi_task":
        # 分析多任务模式
        active_decisions = [d for d in decisions if d.get("outcome") == "pending"]

        analysis["findings"].append(
            f"当前有{len(active_decisions)}个待完成决策"
        )

        if len(active_decisions) > 3:
            analysis["recommendations"].append(
                "⚠️ 同时进行的决策过多，建议聚焦完成其中一个"
            )

    return analysis


def print_decision_summary(decision: Dict[str, Any]):
    """打印决策摘要"""
    print(f"\n📝 决策ID：{decision['decision_id']}")
    print(f"  时间：{decision['timestamp'][:19]}")
    print(f"  类型：{DECISION_TYPES[decision['type']]['name']}")
    print(f"  描述：{decision['description']}")

    if decision.get("emotional_factors"):
        print(f"  情感因素：{', '.join(decision['emotional_factors'])}")
        print(f"  情感占比：{decision['emotion_ratio']*100:.0f}%")

    print(f"  风险等级：{decision['risk_level'].upper()}")

    if decision.get("ai_warning"):
        print(f"  AI警告：{decision['ai_warning']}")

    if decision.get("required_actions"):
        print(f"  必要行动：")
        for action in decision["required_actions"]:
            print(f"    • {action}")

    print(f"  结果：{decision['outcome']}")


def print_decision_history(decisions: List[Dict[str, Any]]):
    """打印决策历史"""
    if not decisions:
        print("\n📋 暂无决策记录")
        return

    print(f"\n📋 决策历史（共{len(decisions)}条）\n")

    # 按类型分组
    by_type = {}
    for d in decisions:
        dtype = d["type"]
        if dtype not in by_type:
            by_type[dtype] = []
        by_type[dtype].append(d)

    for dtype, dtype_decisions in by_type.items():
        print(f"{DECISION_TYPES[dtype]['name']}（{len(dtype_decisions)}条）：")
        for d in dtype_decisions[:3]:  # 只显示前3个
            print(f"  • {d['description']}")
            if d.get("emotional_factors"):
                print(f"    情感因素：{', '.join(d['emotional_factors'])}")
        if len(dtype_decisions) > 3:
            print(f"  • ... 还有{len(dtype_decisions)-3}条")
        print()


def update_decision_status(decision_id: str, new_status: str, note: str = "") -> Dict[str, Any]:
    """更新决策状态"""
    decision = load_decision(decision_id)
    if not decision:
        raise ValueError(f"决策 {decision_id} 不存在")

    valid_statuses = ["pending", "in_progress", "accepted", "rejected", "completed"]
    if new_status not in valid_statuses:
        raise ValueError(f"无效的状态：{new_status}。有效状态：{', '.join(valid_statuses)}")

    old_status = decision["outcome"]
    decision["outcome"] = new_status
    decision["updated_at"] = datetime.now().isoformat()

    if note:
        decision.setdefault("status_history", []).append({
            "timestamp": datetime.now().isoformat(),
            "from_status": old_status,
            "to_status": new_status,
            "note": note
        })

    # 保存更新后的决策
    decision_dir = get_decision_dir()
    file_path = decision_dir / f"{decision_id}.json"

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(decision, f, ensure_ascii=False, indent=2)

    return decision


def complete_decision(decision_id: str, result: str, outcome: str, lessons: str = "") -> Dict[str, Any]:
    """完成决策"""
    decision = load_decision(decision_id)
    if not decision:
        raise ValueError(f"决策 {decision_id} 不存在")

    valid_results = ["success", "failure", "partial"]
    if result not in valid_results:
        raise ValueError(f"无效的结果：{result}。有效结果：{', '.join(valid_results)}")

    decision["outcome"] = "completed"
    decision["result"] = result
    decision["final_outcome"] = outcome
    decision["lessons_learned"] = lessons
    decision["completed_at"] = datetime.now().isoformat()
    decision["updated_at"] = datetime.now().isoformat()

    # 保存
    decision_dir = get_decision_dir()
    file_path = decision_dir / f"{decision_id}.json"

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(decision, f, ensure_ascii=False, indent=2)

    return decision


def list_decisions_by_status(status: str, days: Optional[int] = None) -> List[Dict[str, Any]]:
    """按状态列出决策"""
    decisions = load_all_decisions(days=days)

    filtered = [d for d in decisions if d.get("outcome") == status]

    # 按时间排序
    filtered.sort(key=lambda x: x["timestamp"], reverse=True)

    return filtered


def main():
    import argparse

    parser = argparse.ArgumentParser(description="决策追踪系统")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # record命令
    record_parser = subparsers.add_parser("record", help="记录决策")
    record_parser.add_argument("--type", choices=["life_level", "important", "daily"],
                             default="important", help="决策类型")
    record_parser.add_argument("--description", required=True, help="决策描述")
    record_parser.add_argument("--rational", help="理性分析")
    record_parser.add_argument("--emotions", nargs="*", help="情感因素")
    record_parser.add_argument("--warning", help="AI警告")

    # history命令
    history_parser = subparsers.add_parser("history", help="查看决策历史")
    history_parser.add_argument("--days", type=int, help="最近多少天")

    # check-risk命令
    risk_parser = subparsers.add_parser("check-risk", help="检查决策风险")
    risk_parser.add_argument("--description", required=True, help="决策描述")
    risk_parser.add_argument("--persona", help="画像文件路径")

    # analyze命令
    analyze_parser = subparsers.add_parser("analyze", help="分析决策模式")
    analyze_parser.add_argument("--pattern", required=True,
                               choices=["emotion_hijack", "validation", "multi_task"],
                               help="分析模式")

    # update-status命令
    status_parser = subparsers.add_parser("update-status", help="更新决策状态")
    status_parser.add_argument("decision_id", help="决策ID")
    status_parser.add_argument("--status", required=True,
                               choices=["pending", "in_progress", "accepted", "rejected", "completed"],
                               help="新状态")
    status_parser.add_argument("--note", help="备注")

    # complete命令
    complete_parser = subparsers.add_parser("complete", help="完成决策")
    complete_parser.add_argument("decision_id", help="决策ID")
    complete_parser.add_argument("--result", required=True,
                                choices=["success", "failure", "partial"],
                                help="结果")
    complete_parser.add_argument("--outcome", required=True, help="最终结果")
    complete_parser.add_argument("--lessons", help="学到的教训")

    # list命令
    list_parser = subparsers.add_parser("list", help="列出决策")
    list_parser.add_argument("--status", choices=["pending", "in_progress", "accepted", "rejected", "completed"],
                            help="按状态过滤")
    list_parser.add_argument("--days", type=int, help="最近多少天")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "record":
            decision = record_decision(
                description=args.description,
                decision_type=args.type,
                rational_analysis=args.rational or "",
                emotional_factors=args.emotions,
                ai_warning=args.warning or ""
            )
            print("✅ 决策已记录")
            print_decision_summary(decision)

        elif args.command == "history":
            decisions = load_all_decisions(days=args.days)
            print_decision_history(decisions)

        elif args.command == "check-risk":
            risk_assessment = check_risk(args.description, args.persona)

            print(f"\n🔍 决策风险评估")
            print(f"  决策：{risk_assessment['description']}")
            print(f"  建议类型：{DECISION_TYPES[risk_assessment['decision_type_suggestion']]['name']}")

            if risk_assessment["detected_keywords"]:
                print(f"  检测到关键词：{', '.join(risk_assessment['detected_keywords'])}")

            if risk_assessment["emotion_factors"]:
                print(f"  情感因素：{', '.join(risk_assessment['emotion_factors'])}")
                print(f"  情感占比：{risk_assessment['emotion_ratio']*100:.0f}%")

            print(f"  风险等级：{risk_assessment['risk_level'].upper()}")

            if risk_assessment["warnings"]:
                print("\n⚠️  警告：")
                for warning in risk_assessment["warnings"]:
                    print(f"  {warning}")

            if risk_assessment["required_actions"]:
                print("\n📋 必要行动：")
                for action in risk_assessment["required_actions"]:
                    print(f"  • {action}")

            if risk_assessment["persona_references"]:
                print("\n💡 AI建议：")
                for ref in risk_assessment["persona_references"]:
                    print(f"  • {ref}")

        elif args.command == "analyze":
            analysis = analyze_pattern(args.pattern)

            print(f"\n📊 决策模式分析：{args.pattern}")
            print(f"  总决策数：{analysis['total_decisions']}")

            if analysis["findings"]:
                print("\n发现：")
                for finding in analysis["findings"]:
                    print(f"  • {finding}")

            if analysis["recommendations"]:
                print("\n建议：")
                for rec in analysis["recommendations"]:
                    print(f"  {rec}")

        elif args.command == "update-status":
            decision = update_decision_status(
                decision_id=args.decision_id,
                new_status=args.status,
                note=args.note or ""
            )
            print(f"✅ 决策状态已更新：{args.decision_id}")
            print(f"  状态：{args.status}")
            if args.note:
                print(f"  备注：{args.note}")

        elif args.command == "complete":
            decision = complete_decision(
                decision_id=args.decision_id,
                result=args.result,
                outcome=args.outcome,
                lessons=args.lessons or ""
            )
            print(f"✅ 决策已完成：{args.decision_id}")
            print(f"  结果：{args.result}")
            print(f"  最终结果：{args.outcome}")
            if args.lessons:
                print(f"  学到的教训：{args.lessons}")

        elif args.command == "list":
            if args.status:
                decisions = list_decisions_by_status(args.status, args.days)
                status_names = {
                    "pending": "待处理",
                    "in_progress": "进行中",
                    "accepted": "已采纳",
                    "rejected": "已拒绝",
                    "completed": "已完成"
                }
                print(f"\n📋 {status_names[args.status]}的决策（共{len(decisions)}条）\n")
            else:
                decisions = load_all_decisions(days=args.days)
                print(f"\n📋 所有决策（最近{args.days or '全部'}天，共{len(decisions)}条）\n")

            if not decisions:
                print("无相关决策")
            else:
                for d in decisions:
                    status_emoji = {
                        "pending": "⏳",
                        "in_progress": "🔄",
                        "accepted": "✅",
                        "rejected": "❌",
                        "completed": "🏁"
                    }.get(d.get("outcome", "pending"), "⚪")
                    print(f"{status_emoji} {d['description']}")
                    print(f"   ID: {d['decision_id']}")
                    print(f"   状态: {d.get('outcome', 'pending')}")
                    print()

    except Exception as e:
        print(f"❌ 错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
