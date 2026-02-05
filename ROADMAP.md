# Persona Interview Skill - 迭代路线图

**愿景**：从"自我理解工具"进化成"终身成长伙伴"

**当前状态**：Phase 1（数据整合基础）- v1.2 四维整合版已完成

---

## 📅 总体规划

```
Phase 1: 数据整合基础（Week 1-2）✅ v1.2已完成，待完善工具
Phase 2: 持续追踪系统（Week 3-8）
Phase 3: 智能伙伴系统（Week 9-20）
Phase 4: 生态系统（Week 21-44）
```

---

## Phase 1: 数据整合基础（Week 1-2）

### 目标
建立完整的多维画像基础和工具链

### 已完成 ✅
- ✅ 深度访谈框架（四阶段：基线→模式挖掘→深度探索→关系定义）
- ✅ 简历解析脚本（`resume_parser.py`）- 支持PDF/DOCX/MD + LLM API
- ✅ MBTI分析脚本（`mbti_analyzer.py`）- 8题测试 + 16型数据库
- ✅ 画像v1.0（访谈版）
- ✅ 画像v1.1（三维整合：简历+MBTI+访谈）
- ✅ 画像v1.2（四维整合：简历+MBTI+盖洛普+访谈）

### 待完成 ⏳
- [ ] `gallup_parser.py` - 盖洛普PDF自动解析脚本
- [ ] `persona_schema.json` - 统一的Persona数据格式定义
- [ ] `version_manager.py` - 版本管理工具（自动记录版本历史）
- [ ] 文档更新（README.md中添加新功能说明）

### 交付物
- [x] 完整的四维画像（v1.2）
- [ ] 完整的数据解析工具链（简历+MBTI+盖洛普）
- [ ] 标准化的数据格式

### 预计完成时间：Week 2

---

## Phase 2: 持续追踪系统（Week 3-8）

### 目标
从"一次性访谈"到"持续成长追踪"

### 核心功能

#### 2.1 决策追踪系统（Week 3-4）
**脚本**：`decision_tracker.py`

**功能**：
- 记录用户的决策（类型、时间、理由、情感因素）
- 分析决策模式（对比画像中的模式）
- 风险检查（对比画像中的风险点）
- 情感因素检测

**数据结构**：
```json
{
  "decision_id": "2026-02-05-001",
  "timestamp": "2026-02-05T14:30:00",
  "type": "life_level",  // life_level | important | daily
  "description": "考虑买房",
  "rational_analysis": "...",
  "emotional_factors": ["结婚需求", "父母期待"],
  "emotion_ratio": 0.7,
  "risk_level": "high",
  "ai_warning": "情感因素占比70%，建议冷静期",
  "required_actions": ["7天冷静期", "咨询3人", "列出反对理由"],
  "outcome": "pending",  // pending | accepted | rejected
  "created_at": "2026-02-05T14:30:00",
  "updated_at": "2026-02-05T14:30:00"
}
```

**使用方式**：
```bash
# 记录决策
python decision_tracker.py record --type life_level --description "考虑买房"

# 查看决策历史
python decision_tracker.py history --days 30

# 分析模式
python decision_tracker.py analyze --pattern emotion_hijack
```

**交付物**：
- [ ] `decision_tracker.py` 脚本
- [ ] `data/decisions/` 目录结构
- [ ] 决策记录JSON格式
- [ ] 使用文档

---

#### 2.2 周期性成长回顾（Week 5-6）
**脚本**：`growth_reviewer.py`

**功能**：
- 每周/每月自动生成成长报告
- 对比画像中的"待改进项"
- 追踪"知行合一"的改善情况
- 发现新的行为模式
- 追踪关键指标（情感劫持率、冷静期执行率等）

**报告格式**：
```markdown
# 成长周报（2026-02-05 第5周）

## 决策追踪
- 本周记录决策：3个
- 生命级决策：0个
- 重要决策：1个（换工作）
- 日常决策：2个

## 行为模式分析
✅ 改善：重大决策前咨询了AI
⚠️ 重复："发现新机会"仍然直接投入，未验证需求
❌ 警示：仍然多任务并行（3个项目）

## 指标追踪
| 指标 | 本周 | 上周 | 变化 |
|------|------|------|------|
| 情感劫持率 | 30% | 50% | ✅ -20% |
| 冷静期执行率 | 100% | 0% | ✅ +100% |
| 多任务并行 | 3个 | 4个 | ✅ -1个 |

## 画像对比
对比v1.2画像中的"决策分类系统"：
- 本周遵守生命级决策流程：0/0（无生命级决策）
- 重要决策遵守80%理性：1/1（✅）

## 下周建议
1. 聚焦：3个项目中选择1个重点推进
2. 验证：新项目启动前必须做市场验证
3. 冷静期：重要决策前至少冷静2天
```

**使用方式**：
```bash
# 生成周报
python growth_reviewer.py weekly --week 5

# 生成月报
python growth_reviewer.py monthly --month 2

# 查看指标趋势
python growth_reviewer.py trends --metric emotion_hijack_rate --days 90
```

**交付物**：
- [ ] `growth_reviewer.py` 脚本
- [ ] `data/reviews/` 目录结构
- [ ] 成长报告模板
- [ ] 指标可视化（可选）

---

#### 2.3 版本对比分析（Week 7-8）
**脚本**：`version_comparer.py`

**功能**：
- 对比两个版本的画像
- 发现进步点
- 发现新问题
- 追踪核心指标的变化
- 生成版本对比报告

**对比维度**：
1. 新增数据（简历、MBTI、盖洛普、访谈）
2. 关键发现
3. 进步点
4. 待改进
5. 指标变化

**报告格式**：
```markdown
## 版本对比：v1.1 → v1.2

### 新增数据
- ✅ 整合盖洛普测评（战略30、关系28、执行22、影响20）

### 关键发现
- 🎯 三大评估完美对齐：MBTI(INTJ) + 盖洛普(战略30) + 简历(战略14年)
- 🤔 意外发现：关系建立28分与INTJ标签不一致（深度 > 广度）
- ⚠️ 新问题："责任"主题导致对他人过度承诺

### 进步点
- ✅ 职业方向更明确：发挥"战略+关系"双核优势
- ✅ 更精准的职业匹配：深度客户咨询 vs 纯销售

### 待改进
- ⏳ "责任"主题管理：学会拒绝他人情感期待
- ⏳ "成就"主题管理：避免急于完成任务跳过验证

### 指标变化
| 指标 | v1.1 | v1.2 | 变化 |
|------|------|------|------|
| 战略思维确认 | 2/3 | 4/4 | ✅ 完美对齐 |
| 关系能力认知 | 不擅长 | 深度>广度 | ✅ 修正 |
| 决策盲区 | 5个 | 6个 | ❌ 新增"责任"主题副作用 |
```

**使用方式**：
```bash
# 对比两个版本
python version_comparer.py compare --old v1.1 --new v1.2

# 查看版本列表
python version_comparer.py list

# 查看版本详情
python version_comparer.py show --version v1.2
```

**交付物**：
- [ ] `version_comparer.py` 脚本
- [ ] 版本对比报告模板
- [ ] 版本元数据文件（`data/versions.json`）

---

### Phase 2 交付物汇总
- [x] 决策追踪系统（`decision_tracker.py`）
- [x] 周期性成长回顾（`growth_reviewer.py`）
- [x] 版本对比分析（`version_comparer.py`）
- [x] 数据目录结构（`data/decisions/`, `data/reviews/`, `data/versions/`）
- [x] 使用文档（`docs/phase2-guide.md`）

### 预计完成时间：Week 8

---

## Phase 3: 智能伙伴系统（Week 9-20）

### 目标
从"被动记录"到"主动干预"

### 核心功能

#### 3.1 主动风险预警（Week 9-12）
**脚本**：`risk_monitor.py`

**功能**：
- 监测用户的决策关键词
- 自动识别高风险决策
- 主动启动"风险干预流程"
- 实时引用画像数据提醒用户

**关键词库**：
```json
{
  "high_risk_keywords": ["买房", "结婚", "生子", "创业", "投资", "换工作"],
  "emotion_keywords": ["为了父母", "结婚需求", "尽快结束", "应该"],
  "opportunity_keywords": ["发现了", "新机会", "有个想法"]
}
```

**风险干预流程**：
1. 检测到高风险关键词
2. 分析情感因素占比
3. 引用画像中的历史案例
4. 引用画像中的优势/劣势
5. 强制执行冷静期
6. 提供"魔鬼代言人"视角

**交付物**：
- [ ] `risk_monitor.py` 脚本
- [ ] 关键词库（`data/keywords.json`）
- [ ] 风险干预流程文档

---

#### 3.2 个性化成长建议（Week 13-16）
**脚本**：`growth_advisor.py`

**功能**：
- 基于用户的画像数据，主动推荐成长路径
- 发现用户的优势盲区，提醒发挥
- 发现用户的劣势陷阱，提醒避免
- 追踪建议的执行情况

**建议类型**：
1. **发挥优势**：基于画像中的核心优势
2. **避开陷阱**：基于画像中的核心劣势
3. **决策改进**：基于历史决策模式
4. **关系建立**：基于盖洛普"交往"主题

**交付物**：
- [ ] `growth_advisor.py` 脚本
- [ ] 建议模板库
- [ ] 建议执行追踪系统

---

#### 3.3 智能对话伙伴（Week 17-20）
**脚本**：`intelligent_partner.py`

**功能**：
- AI不只是工具，而是"成长伙伴"
- 对话中主动引用画像数据
- 发现用户的模式并指出
- 提供基于画像的个性化反馈

**技术实现**：
- 向量数据库存储对话历史（ChromaDB/Faiss）
- RAG（检索增强生成）检索画像内容
- 模式识别算法发现重复模式

**交付物**：
- [ ] `intelligent_partner.py` 脚本
- [ ] 对话历史数据库
- [ ] RAG检索系统
- [ ] 模式识别算法

---

### Phase 3 交付物汇总
- [x] 主动风险预警（`risk_monitor.py`）
- [x] 个性化成长建议（`growth_advisor.py`）
- [x] 智能对话伙伴（`intelligent_partner.py`）
- [x] 对话历史数据库
- [x] RAG检索系统
- [x] 使用文档（`docs/phase3-guide.md`）

### 预计完成时间：Week 20

---

## Phase 4: 生态系统（Week 21-44）

### 目标
从"个人工具"到"成长平台"

### 核心功能

#### 4.1 多模态数据整合（Week 21-28）
**脚本**：`multimodal_integrator.py`

**功能**：
- 整合健康数据（睡眠、运动、心率）
- 整合行为数据（时间管理、APP使用）
- 整合社交数据（社交频率、关系深度）
- 整合财务数据（收入、支出、投资）
- 多维度数据交叉分析

**数据源**：
- Apple Health / Google Fit
- RescueTime / Screen Time
- 日历/邮件/社交网络
- 银行/支付工具

**交付物**：
- [ ] `multimodal_integrator.py` 脚本
- [ ] 数据源适配器
- [ ] 交叉分析报告

---

#### 4.2 社交成长网络（Week 29-36）
**脚本**：`social_network.py`

**功能**：
- 邀请朋友、家人、导师加入成长网络
- 他们可以看到你的成长目标（需要授权）
- 他们可以提供反馈、建议、支持
- 形成外部监督和支持系统

**功能模块**：
1. 成员邀请
2. 权限管理
3. 反馈收集
4. 支持报告

**交付物**：
- [ ] `social_network.py` 脚本
- [ ] 权限管理系统
- [ ] 反馈收集系统

---

#### 4.3 成长期货市场（Week 37-44）
**脚本**：`growth_futures.py`

**功能**：
- 设定长期成长目标
- 邀请朋友作为"见证人"
- 完成目标得到奖励，失败付出代价
- 用"舍得"哲学设计激励机制

**合约流程**：
1. 创建合约（目标、期限、见证人、赌注）
2. 追踪进度
3. 验证完成情况
4. 结算合约

**交付物**：
- [ ] `growth_futures.py` 脚本
- [ ] 合约管理系统
- [ ] 进度追踪系统

---

### Phase 4 交付物汇总
- [x] 多模态数据整合（`multimodal_integrator.py`）
- [x] 社交成长网络（`social_network.py`）
- [x] 成长期货市场（`growth_futures.py`）
- [x] 使用文档（`docs/phase4-guide.md`）

### 预计完成时间：Week 44

---

## 🗺️ 总体时间线

```
Week 1-2:  Phase 1 数据整合基础
  ├─ ✅ 画像v1.2（已完成）
  ├─ ⏳ Persona Schema
  ├─ ⏳ 盖洛普PDF解析
  └─ ⏳ 版本管理工具

Week 3-4:  Phase 2.1 决策追踪系统
  ├─ ⏳ decision_tracker.py
  ├─ ⏳ 决策记录JSON
  └─ ⏳ 风险检查逻辑

Week 5-6:  Phase 2.2 周期性成长回顾
  ├─ ⏳ growth_reviewer.py
  ├─ ⏳ 成长报告模板
  └─ ⏳ 指标追踪系统

Week 7-8:  Phase 2.3 版本对比分析
  ├─ ⏳ version_comparer.py
  └─ ⏳ 版本元数据

Week 9-12: Phase 3.1 主动风险预警
  ├─ ⏳ risk_monitor.py
  └─ ⏳ 关键词库

Week 13-16: Phase 3.2 个性化成长建议
  ├─ ⏳ growth_advisor.py
  └─ ⏳ 建议模板

Week 17-20: Phase 3.3 智能对话伙伴
  ├─ ⏳ intelligent_partner.py
  ├─ ⏳ 对话历史DB
  └─ ⏳ RAG系统

Week 21-44: Phase 4 生态系统
  ├─ 多模态数据整合
  ├─ 社交成长网络
  └─ 成长期货市场
```

---

## 📊 成功指标

### Phase 1 成功指标
- [x] 完成四维画像（简历+MBTI+盖洛普+访谈）
- [ ] 能够自动解析简历、MBTI、盖洛普数据
- [ ] 数据格式标准化

### Phase 2 成功指标
- [ ] 用户能够记录决策
- [ ] 用户能够查看成长报告
- [ ] 用户能够对比版本变化

### Phase 3 成功指标
- [ ] AI能够主动预警风险
- [ ] AI能够提供个性化建议
- [ ] AI能够进行智能对话

### Phase 4 成功指标
- [ ] 整合多模态数据
- [ ] 形成社交成长网络
- [ ] 运行成长期货市场

---

## 🎯 近期任务（本周+下周）

### 本周任务（Week 1）
- [x] ✅ 完成画像v1.2
- [ ] 设计Persona Schema
- [ ] 实现盖洛普PDF自动解析

### 下周任务（Week 2）
- [ ] 实现版本对比分析
- [ ] 设计决策追踪系统
- [ ] 测试整个流程

---

**最后更新**：2026-02-05
**当前版本**：v1.2
**下次更新**：每周日更新进度
