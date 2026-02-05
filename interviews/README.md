# 人格访谈记录目录

本目录用于保存人格访谈的记录和画像文档。

## 🔒 隐私说明

**重要**：本目录中的个人访谈记录存储在**本地**，不会被上传到 GitHub。

- 你的真实访谈记录（`interview-*.md`、`my-persona*.md`、`CHANGELOG.md`）已被 `.gitignore` 忽略
- 只有 `example/` 目录和本文件会被上传到 GitHub
- 你的隐私数据完全由你自己掌控

## 📁 本地文件结构

当你开始使用 persona-interview skill 后，本目录会包含以下文件：

```
interviews/
├── README.md                  # 本文件
├── example/                   # 示例访谈（会上传到 GitHub）
│   ├── sample-interview.md    # 示例访谈记录
│   └── sample-persona-v1.0.md # 示例人格画像
├── interview-YYYY-MM-DD.md    # 你的访谈记录（本地）
├── my-persona.md              # 当前画像索引（本地）
├── my-persona-vX.X.md         # 历史版本画像（本地）
└── CHANGELOG.md               # 版本变更记录（本地）
```

## 📋 文件说明

### 本地文件（不上传）

- `interview-YYYY-MM-DD.md` - 完整访谈记录
- `my-persona.md` - 当前最新的人格画像索引
- `my-persona-vX.X.md` - 历史版本的完整人格画像
- `CHANGELOG.md` - 人格版本变更记录

这些文件包含你的个人数据，已被 `.gitignore` 忽略，不会上传到 GitHub。

### 示例文件（会上传）

- `example/sample-interview.md` - 匿名化示例访谈
- `example/sample-persona-v1.0.md` - 匿名化示例人格画像

这些文件用于展示访谈格式，所有信息均为虚构。

## 🚀 如何开始

### 第一次使用

当你使用 persona-interview skill 进行首次访谈后，AI 会自动在本目录创建：

1. `interview-YYYY-MM-DD.md` - 完整访谈记录
2. `my-persona-v1.0.md` - v1.0 版人格画像
3. `my-persona.md` - 当前画像索引
4. `CHANGELOG.md` - 版本变更记录

### 后续访谈

每次新访谈后，AI 会：

1. 创建新的访谈记录（如 `interview-2026-05-05.md`）
2. 更新人格画像版本（如 `my-persona-v1.1.md`）
3. 更新 `my-persona.md` 指向最新版本
4. 更新 `CHANGELOG.md` 记录变更

### 访谈流程

1. **先阅读历史**：
   - 阅读 `my-persona.md` 了解当前画像
   - 阅读 `interview-YYYY-MM-DD.md` 了解之前的发现

2. **对比变化**：
   - 哪些模式仍然存在？
   - 哪些模式已经改善？
   - 出现了哪些新模式？

3. **更新画像**：
   - 根据新发现更新 `my-persona-vX.X.md`
   - 保留旧版本记录

## 📅 更新频率建议

- **常规更新**：每3个月一次
- **重大事件后**：遇到重大决策或变故后立即更新
- **感觉迷失时**：当感觉需要重新审视自己时

## 📖 参考示例

想了解访谈记录和人格画像的格式，可以查看：

- [示例访谈记录](example/sample-interview.md)
- [示例人格画像 v1.0](example/sample-persona-v1.0.md)

## 🔐 隐私保护

- 所有个人访谈数据都存储在本地
- GitHub 仓库只包含示例和模板
- 你可以选择是否分享你的访谈记录
- 建议定期备份 `interviews/` 目录

---

**开始你的第一次访谈**：在 Claude Code 中运行 `/skill persona-interview`
