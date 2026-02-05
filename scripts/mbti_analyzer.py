#!/usr/bin/env python3
"""
MBTI 分析器 - 分析用户的 MBTI 类型

支持功能：
1. 交互式 MBTI 测试
2. 直接输入已知的 MBTI 类型
3. 生成 MBTI 分析报告

使用方法：
    python mbti_analyzer.py test        # 交互式测试
    python mbti_analyzer.py input INTJ  # 直接输入类型
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


class MBTIAnalyzer:
    def __init__(self, template_path: str = None):
        """初始化 MBTI 分析器"""
        if template_path is None:
            template_path = Path(__file__).parent.parent / "templates" / "mbti_questions.json"

        with open(template_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        self.questions = self.data['questions']
        self.types = self.data['types']
        self.scores = {'E': 0, 'I': 0, 'S': 0, 'N': 0, 'T': 0, 'F': 0, 'J': 0, 'P': 0}

    def reset_scores(self):
        """重置分数"""
        self.scores = {'E': 0, 'I': 0, 'S': 0, 'N': 0, 'T': 0, 'F': 0, 'J': 0, 'P': 0}

    def interactive_test(self) -> str:
        """交互式 MBTI 测试"""
        print("=" * 60)
        print("MBTI 性格测试")
        print("=" * 60)
        print("请根据你的真实情况选择最符合你的选项\n")

        self.reset_scores()

        for i, question in enumerate(self.questions, 1):
            print(f"\n问题 {i}/{len(self.questions)}")
            print(f"{question['question']}")

            for j, option in enumerate(question['options'], 1):
                print(f"  {j}. {option['text']}")

            while True:
                try:
                    choice = input("\n请选择（输入数字）: ").strip()
                    choice_idx = int(choice) - 1

                    if 0 <= choice_idx < len(question['options']):
                        selected = question['options'][choice_idx]
                        score = selected['score']
                        self.scores[score] += 1
                        break
                    else:
                        print("❌ 无效的选项，请重新输入")
                except ValueError:
                    print("❌ 请输入数字")
                except KeyboardInterrupt:
                    print("\n\n测试已取消")
                    sys.exit(0)

        # 计算结果
        return self.calculate_type()

    def calculate_type(self) -> str:
        """根据分数计算 MBTI 类型"""
        type_str = ""

        type_str += 'E' if self.scores['E'] >= self.scores['I'] else 'I'
        type_str += 'S' if self.scores['S'] >= self.scores['N'] else 'N'
        type_str += 'T' if self.scores['T'] >= self.scores['F'] else 'F'
        type_str += 'J' if self.scores['J'] >= self.scores['P'] else 'P'

        return type_str

    def analyze_type(self, mbti_type: str) -> Dict[str, Any]:
        """分析 MBTI 类型"""
        mbti_type = mbti_type.upper()

        if mbti_type not in self.types:
            print(f"❌ 无效的 MBTI 类型：{mbti_type}")
            print(f"   有效类型：{', '.join(self.types.keys())}")
            sys.exit(1)

        type_info = self.types[mbti_type]

        return {
            "type": mbti_type,
            "name": type_info['name'],
            "description": type_info['description'],
            "strengths": type_info['strengths'],
            "weaknesses": type_info['weaknesses'],
            "career_matches": type_info['career_matches'],
            "work_style": type_info['work_style'],
            "analyzed_at": datetime.now().isoformat(),
            "scores": self.scores
        }

    def save_result(self, result: Dict[str, Any], output_path: str):
        """保存分析结果"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 分析结果已保存到：{output_path}")

    def print_result(self, result: Dict[str, Any]):
        """打印分析结果"""
        print("\n" + "=" * 60)
        print("MBTI 分析结果")
        print("=" * 60)

        print(f"\n🎯 你的类型：{result['type']} - {result['name']}")
        print(f"\n📝 描述：{result['description']}")

        print(f"\n💪 优势：")
        for strength in result['strengths']:
            print(f"  - {strength}")

        print(f"\n⚠️  弱点：")
        for weakness in result['weaknesses']:
            print(f"  - {weakness}")

        print(f"\n💼 适合的职业：")
        for career in result['career_matches']:
            print(f"  - {career}")

        print(f"\n🏢 工作风格：")
        print(f"  {result['work_style']}")

        # 如果有测试分数，显示维度得分
        if 'scores' in result:
            print(f"\n📊 维度得分：")
            scores = result['scores']
            print(f"  外向(E) vs 内向(I)：{scores['E']} : {scores['I']}")
            print(f"  感觉(S) vs 直觉(N)：{scores['S']} : {scores['N']}")
            print(f"  思考(T) vs 情感(F)：{scores['T']} : {scores['F']}")
            print(f"  判断(J) vs 感知(P)：{scores['J']} : {scores['P']}")


def main():
    if len(sys.argv) < 2:
        print("使用方法：")
        print("  python mbti_analyzer.py test              # 交互式测试")
        print("  python mbti_analyzer.py input <MBTI类型>  # 直接输入类型")
        print("\n示例：")
        print("  python mbti_analyzer.py test")
        print("  python mbti_analyzer.py input INTJ")
        sys.exit(1)

    analyzer = MBTIAnalyzer()
    command = sys.argv[1].lower()

    if command == "test":
        # 交互式测试
        mbti_type = analyzer.interactive_test()
        result = analyzer.analyze_type(mbti_type)
        analyzer.print_result(result)

        output_file = f"mbti_{mbti_type}.json"
        analyzer.save_result(result, output_file)

    elif command == "input":
        # 直接输入类型
        if len(sys.argv) < 3:
            print("❌ 请提供 MBTI 类型")
            print("示例：python mbti_analyzer.py input INTJ")
            sys.exit(1)

        mbti_type = sys.argv[2].upper()
        result = analyzer.analyze_type(mbti_type)
        analyzer.print_result(result)

        output_file = f"mbti_{mbti_type}.json"
        analyzer.save_result(result, output_file)

    else:
        print(f"❌ 未知命令：{command}")
        print("可用命令：test, input")
        sys.exit(1)


if __name__ == "__main__":
    main()
