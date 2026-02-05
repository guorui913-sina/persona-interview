#!/bin/bash
# Phase 1 完整流程测试脚本

echo "========================================="
echo "Persona Interview Skill - Phase 1 测试"
echo "========================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 测试计数器
PASSED=0
FAILED=0

# 测试函数
test_command() {
    local name="$1"
    local command="$2"

    echo "📝 测试：$name"
    echo "   命令：$command"

    if eval "$command" > /dev/null 2>&1; then
        echo "   ✅ 通过"
        ((PASSED++))
    else
        echo "   ❌ 失败"
        ((FAILED++))
    fi
    echo ""
}

echo "1. 测试盖洛普解析脚本"
echo "-------------------------------------------"
test_command "盖洛普帮助信息" "python gallup_parser.py --help"
test_command "盖洛普PDF解析（手动输入模式）" "python gallup_parser.py /dev/null 2>&1 | grep -q '使用方法'"

echo "2. 测试版本对比工具"
echo "-------------------------------------------"
test_command "版本列表" "python version_comparer.py list"
test_command "版本详情" "python version_comparer.py show --version v1.2"
test_command "版本对比" "python version_comparer.py compare --old v1.1 --new v1.2"

echo "3. 测试决策追踪系统"
echo "-------------------------------------------"
test_command "风险检查" "python decision_tracker.py check-risk --description '测试决策'"
test_command "决策历史" "python decision_tracker.py history"
test_command "模式分析" "python decision_tracker.py analyze --pattern emotion_hijack"

echo "4. 验证数据文件"
echo "-------------------------------------------"
echo "📝 检查必要的数据文件..."

# 检查Schema文件
if [ -f "../schemas/persona_schema.json" ]; then
    echo "   ✅ persona_schema.json 存在"
    ((PASSED++))
else
    echo "   ❌ persona_schema.json 不存在"
    ((FAILED++))
fi

# 检查示例文件
if [ -f "../schemas/persona_example.json" ]; then
    echo "   ✅ persona_example.json 存在"
    ((PASSED++))
else
    echo "   ❌ persona_example.json 不存在"
    ((FAILED++))
fi

# 检查数据目录
if [ -d "../data/decisions" ]; then
    echo "   ✅ data/decisions 目录存在"
    ((PASSED++))
else
    echo "   ❌ data/decisions 目录不存在"
    ((FAILED++))
fi

if [ -d "../data/reviews" ]; then
    echo "   ✅ data/reviews 目录存在"
    ((PASSED++))
else
    echo "   ❌ data/reviews 目录不存在"
    ((FAILED++))
fi

if [ -d "../data/versions" ]; then
    echo "   ✅ data/versions 目录存在"
    ((PASSED++))
else
    echo "   ❌ data/versions 目录不存在"
    ((FAILED++))
fi

echo ""
echo "5. 验证画像文件"
echo "-------------------------------------------"

# 检查画像文件
for version in "v1.0" "v1.1" "v1.2"; do
    version_file=$(ls ../interviews/my-persona-${version}*.md 2>/dev/null)
    if [ -n "$version_file" ]; then
        echo "   ✅ ${version} 画像文件存在"
        ((PASSED++))
    else
        echo "   ❌ ${version} 画像文件不存在"
        ((FAILED++))
    fi
done

echo ""
echo "========================================="
echo "测试总结"
echo "========================================="
echo "通过：$PASSED"
echo "失败：$FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 所有测试通过！Phase 1 开发完成。"
    exit 0
else
    echo "⚠️  有 $FAILED 个测试失败，请检查。"
    exit 1
fi
