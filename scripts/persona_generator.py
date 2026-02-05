#!/usr/bin/env python3
"""
画像生成器 - 整合简历、MBTI 和其他信息，生成初步人格画像

使用方法：
    python persona_generator.py --resume resume_parsed.json --mbti mbti_INTJ.json
    python persona_generator.py --resume resume_parsed.json --mbti mbti_INTJ.json --output persona.json
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class PersonaGenerator:
    def __init__(self):
        self.data = {}

    def load_resume(self, resume_path: str) -> Dict[str, Any]:
        """加载简历数据"""
        with open(resume_path, 'r', encoding='utf-8') as f:
            resume = json.load(f)

        self.data['resume'] = resume
        return resume

    def load_mbti(self, mbti_path: str) -> Dict[str, Any]:
        """加载 MBTI 数据"""
        with open(mbti_path, 'r', encoding='utf-8') as f:
            mbti = json.load(f)

        self.data['mbti'] = mbti
        return mbti

    def generate_persona(self) -> Dict[str, Any]:
        """生成人格画像"""
        if 'resume' not in self.data or 'mbti' not in self.data:
            raise ValueError("需要同时提供简历和 MBTI 数据")

        resume = self.data['resume']
        mbti = self.data['mbti']

        # 生成画像
        persona = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "version": "1.0",
                "data_sources": ["resume", "mbti"]
            },
            "basics": self._extract_basics(resume, mbti),
            "mbti_profile": self._extract_mbti_profile(mbti),
            "career_background": self._extract_career_background(resume),
            "skills": self._extract_skills(resume),
            "strengths_weaknesses": self._analyze_strengths_weaknesses(resume, mbti),
            "work_style": self._analyze_work_style(resume, mbti),
            "preliminary_insights": self._generate_insights(resume, mbti)
        }

        return persona

    def _extract_basics(self, resume: Dict, mbti: Dict) -> Dict[str, Any]:
        """提取基本信息"""
        basics = resume.get('basics', {})

        # 添加 MBTI 类型
        basics['mbti_type'] = mbti.get('type', '')
        basics['mbti_name'] = mbti.get('name', '')

        return basics

    def _extract_mbti_profile(self, mbti: Dict) -> Dict[str, Any]:
        """提取 MBTI 档案"""
        return {
            "type": mbti.get('type'),
            "name": mbti.get('name'),
            "description": mbti.get('description'),
            "strengths": mbti.get('strengths', []),
            "weaknesses": mbti.get('weaknesses', []),
            "career_matches": mbti.get('career_matches', []),
            "work_style": mbti.get('work_style', ''),
            "scores": mbti.get('scores', {})
        }

    def _extract_career_background(self, resume: Dict) -> Dict[str, Any]:
        """提取职业背景"""
        work_history = resume.get('work_history', [])
        education = resume.get('education', [])

        # 分析职业轨迹
        total_jobs = len(work_history)
        industries = set()
        positions = set()

        for job in work_history:
            if 'company' in job:
                industries.add(job['company'])
            if 'position' in job:
                positions.add(job['position'])

        return {
            "total_jobs": total_jobs,
            "industries": list(industries),
            "positions": list(positions),
            "work_history": work_history,
            "education": education
        }

    def _extract_skills(self, resume: Dict) -> Dict[str, Any]:
        """提取技能"""
        skills = resume.get('skills', [])

        return {
            "all_skills": skills,
            "total_count": len(skills)
        }

    def _analyze_strengths_weaknesses(self, resume: Dict, mbti: Dict) -> Dict[str, Any]:
        """分析优势和劣势"""
        # 从 MBTI 获取
        mbti_strengths = mbti.get('strengths', [])
        mbti_weaknesses = mbti.get('weaknesses', [])

        # 从简历推断（简化版）
        resume_strengths = []
        resume_weaknesses = []

        # 如果工作经历多，说明经验丰富
        if len(resume.get('work_history', [])) >= 5:
            resume_strengths.append("丰富的职业经验")

        # 如果技能多，说明学习能力强
        if len(resume.get('skills', [])) >= 10:
            resume_strengths.append("快速学习能力")

        return {
            "from_mbti": mbti_strengths,
            "from_resume": resume_strengths,
            "weaknesses_from_mbti": mbti_weaknesses,
            "all_strengths": mbti_strengths + resume_strengths,
            "all_weaknesses": mbti_weaknesses + resume_weaknesses
        }

    def _analyze_work_style(self, resume: Dict, mbti: Dict) -> Dict[str, Any]:
        """分析工作风格"""
        mbti_work_style = mbti.get('work_style', '')

        # 基于简历推断工作风格
        resume_insights = []

        work_history = resume.get('work_history', [])
        if work_history:
            # 如果工作变动频繁，可能喜欢变化
            if len(work_history) >= 5:
                resume_insights.append("工作经历显示可能喜欢接受新挑战")

        return {
            "from_mbti": mbti_work_style,
            "from_resume_analysis": resume_insights,
            "combined_style": f"{mbti_work_style}。{' '.join(resume_insights)}"
        }

    def _generate_insights(self, resume: Dict, mbti: Dict) -> List[str]:
        """生成初步洞察"""
        insights = []

        mbti_type = mbti.get('type', '')

        # 基于 MBTI 类型的洞察
        if 'I' in mbti_type:
            insights.append("内向型性格，可能更适合独立工作或深度思考的任务")
        if 'E' in mbti_type:
            insights.append("外向型性格，擅长与人互动和协作")

        if 'S' in mbti_type:
            insights.append("感觉型，注重实际和细节")
        if 'N' in mbti_type:
            insights.append("直觉型，善于看到全局和可能性")

        if 'T' in mbti_type:
            insights.append("思考型，决策时更依赖逻辑分析")
        if 'F' in mbti_type:
            insights.append("情感型，决策时更重视价值观和他人感受")

        if 'J' in mbti_type:
            insights.append("判断型，喜欢计划和组织")
        if 'P' in mbti_type:
            insights.append("感知型，喜欢灵活和开放选项")

        # 基于简历的洞察
        work_history = resume.get('work_history', [])
        if work_history:
            most_recent = work_history[0] if work_history else {}
            if 'position' in most_recent:
                insights.append(f"最近的职位是 {most_recent['position']}")

        return insights

    def save_persona(self, persona: Dict[str, Any], output_path: str):
        """保存画像"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(persona, f, ensure_ascii=False, indent=2)
        print(f"✅ 画像已保存到：{output_path}")

    def print_summary(self, persona: Dict[str, Any]):
        """打印画像摘要"""
        print("\n" + "=" * 60)
        print("初步人格画像")
        print("=" * 60)

        basics = persona['basics']
        mbti = persona['mbti_profile']

        print(f"\n👤 基本信息")
        if 'email' in basics:
            print(f"  邮箱：{basics['email']}")
        print(f"  MBTI：{basics['mbti_type']} - {basics['mbti_name']}")

        print(f"\n🧠 MBTI 描述")
        print(f"  {mbti['description']}")

        print(f"\n💪 优势")
        for strength in persona['strengths_weaknesses']['all_strengths'][:5]:
            print(f"  - {strength}")

        print(f"\n⚠️  需要注意")
        for weakness in persona['strengths_weaknesses']['all_weaknesses'][:3]:
            print(f"  - {weakness}")

        print(f"\n💼 工作风格")
        print(f"  {persona['work_style']['combined_style']}")

        print(f"\n💡 初步洞察")
        for insight in persona['preliminary_insights'][:3]:
            print(f"  - {insight}")


def main():
    parser = argparse.ArgumentParser(description='生成初步人格画像')
    parser.add_argument('--resume', required=True, help='简历 JSON 文件路径')
    parser.add_argument('--mbti', required=True, help='MBTI JSON 文件路径')
    parser.add_argument('--output', default='persona.json', help='输出文件路径（默认：persona.json）')

    args = parser.parse_args()

    # 检查文件是否存在
    if not Path(args.resume).exists():
        print(f"❌ 简历文件不存在：{args.resume}")
        sys.exit(1)

    if not Path(args.mbti).exists():
        print(f"❌ MBTI 文件不存在：{args.mbti}")
        sys.exit(1)

    try:
        generator = PersonaGenerator()

        # 加载数据
        print(f"📄 加载简历：{args.resume}")
        generator.load_resume(args.resume)

        print(f"🧠 加载 MBTI：{args.mbti}")
        generator.load_mbti(args.mbti)

        # 生成画像
        print("\n🎨 正在生成画像...")
        persona = generator.generate_persona()

        # 显示摘要
        generator.print_summary(persona)

        # 保存结果
        generator.save_persona(persona, args.output)

        print("\n💡 提示：这是基于简历和 MBTI 的初步画像")
        print("   建议通过 persona-interview skill 进行深度访谈以获得更准确的画像")

    except Exception as e:
        print(f"❌ 错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
