# 决策生命周期流程

## 决策状态定义

### 1. pending（待处理）
**含义**：决策刚被记录，尚未开始处理

**何时使用**：
- 刚记录一个决策时
- 还没开始冷静期或信息收集

**下一步操作**：
- 如果是生命级决策 → 进入冷静期（in_progress）
- 如果是重要决策 → 开始信息收集
- 如果是日常决策 → 可以直接决定（accepted/rejected）

---

### 2. in_progress（进行中）
**含义**：正在执行必要行动（冷静期、信息收集、咨询等）

**何时使用**：
- 开始执行冷静期（7天倒计时）
- 正在收集信息（咨询他人、市场调研）
- 正在完成必要行动清单

**需要完成的动作**（根据决策类型）：

**生命级决策必要行动**：
1. 列出3个不做的理由
2. 最坏情况推演
3. 咨询3个不同立场的人
4. 7天冷静期
5. 检查"责任"主题（是否对他人的期待负责）

**重要决策建议行动**：
1. 列出1-2个不做的理由
2. 咨询1-2个人
3. 简单冷静期（1-2天）

**日常决策**：
- 相信直觉，直接决定

**如何转换到下一状态**：
- 完成所有必要行动后 → 可以转为 accepted（采纳）或 rejected（拒绝）
- 使用命令：`python decision_tracker.py update-status <decision_id> --status accepted`

---

### 3. accepted（已采纳）
**含义**：决定执行这个决策

**何时使用**：
- 冷静期结束后，决定执行
- 完成所有必要行动后，认为应该做

**下一步**：
- 开始执行决策
- 定期回顾执行结果
- 完成后转为 completed

**如何记录**：
```bash
python decision_tracker.py update-status 2026-02-05-da5ba2fb --status accepted --note "冷静期7天后，决定买房"
```

---

### 4. rejected（已拒绝）
**含义**：决定放弃这个决策

**何时使用**：
- 冷静期结束后，决定不执行
- 列出了足够多的"不做理由"
- 发现这不是真正想做的

**如何记录**：
```bash
python decision_tracker.py update-status 2026-02-05-da5ba2fb --status rejected --note "列出3个不做理由后，决定不买"
```

---

### 5. completed（已完成）
**含义**：决策已经执行完成，可以看到结果

**何时使用**：
- 决策已经执行完毕
- 可以看到最终结果（成功/失败/部分成功）

**需要记录**：
- 最终结果（success/failure/partial）
- 学到的教训
- 如果可以重来，会怎么做

**如何记录**：
```bash
python decision_tracker.py complete 2026-02-05-da5ba2fb \
  --result success \
  --outcome "成功买房，价格合理" \
  --lessons "下次应该更早开始看房，不要急于决定"
```

---

## 状态转换规则

```
pending → in_progress → accepted → completed
            ↓
         rejected
```

**特殊转换**：
- pending → accepted（日常决策可以直接决定）
- pending → rejected（某些决策很快就能决定不做）
- in_progress → pending（暂停执行）

---

## 使用示例

### 场景1：生命级决策（买房）
```bash
# 1. 记录决策
python decision_tracker.py record \
  --type life_level \
  --description "考虑在北京买房" \
  --emotions "结婚需求" "父母期待" \
  --rational "需要稳定住所"

# 状态：pending

# 2. 开始冷静期
python decision_tracker.py update-status 2026-02-05-da5ba2fb \
  --status in_progress \
  --note "开始7天冷静期，同时咨询3个人"

# 状态：in_progress

# 3. 7天后，决定执行
python decision_tracker.py update-status 2026-02-05-da5ba2fb \
  --status accepted \
  --note "冷静期结束，咨询了3个人，决定买房"

# 状态：accepted

# 4. 买房完成
python decision_tracker.py complete 2026-02-05-da5ba2fb \
  --result success \
  --outcome "成功买房，价格合理，位置满意"

# 状态：completed
```

### 场景2：重要决策（换工作）
```bash
# 1. 记录决策
python decision_tracker.py record \
  --type important \
  --description "考虑换到A公司" \
  --rational "薪资更高，平台更好"

# 状态：pending

# 2. 信息收集后，决定不去
python decision_tracker.py update-status 2026-02-06-xxx \
  --status rejected \
  --note "了解了详情后，发现加班太严重，决定不去"

# 状态：rejected（结束）
```

---

## 待实现功能

### 命令：update-status
更新决策状态
```bash
python decision_tracker.py update-status <decision_id> --status <status> [--note <备注>]
```

### 命令：complete
标记决策完成
```bash
python decision_tracker.py complete <decision_id> --result <success|failure|partial> --outcome <结果> [--lessons <教训>]
```

### 命令：list
查看某个状态的所有决策
```bash
python decision_tracker.py list --status pending
python decision_tracker.py list --status in_progress
```

---

## 流程图

```
┌─────────────┐
│   pending   │  决策刚被记录
└──────┬──────┘
       │
       ├──→ 生命级/重要 → ┌──────────────┐
       │                │  in_progress  │  冷静期/信息收集
       │                └──────┬─────────┘
       │                       │
       │                       ├──→ accepted → ┌────────────┐
       │                       │              │  completed   │  执行完毕
       │                       │              └─────────────┘
       │                       │
       │                       └──→ rejected  （放弃）
       │
       └──→ 日常决策 → 直接 accepted/rejected
```
