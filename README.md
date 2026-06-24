# WorkBuddy Skills Repository

个人 WorkBuddy / Claude Code 技能库，包含自定义 skill 定义。

## 已发布技能

### loop - 迭代优化执行技能

**路径**: `loop/SKILL.md`

复刻 Claude Code `/loop` 命令的迭代优化能力。支持自主执行 → 验证 → 修复 → 重试循环，直到满足退出条件。

**功能特性**:
- ✅ 条件循环模式（直到达标）
- ✅ 限次循环模式（最大迭代轮数）
- ✅ 自动缺陷归因与修复
- ✅ 量化指标追踪
- ✅ 完整迭代日志记录

**触发方式**:
```
/loop 【迭代任务】|【终止条件】|【最大迭代轮数】
```

**示例**:
```
/loop 优化期货LLM分析Prompt | 幻觉率≤5%、逻辑准确率≥65% | 最大8轮
```

## 安装方式

### 方式一：从 GitHub 安装

1. 下载 skill 目录
2. 放置到 `~/.workbuddy/skills/` (用户级) 或 `.workbuddy/skills/` (项目级)
3. 重启 WorkBuddy

### 方式二：使用 WorkBuddy 命令

在 WorkBuddy 中执行：
```
/skill-creator install https://github.com/wq180705550-cmd/skills
```

## Skill 开发规范

本仓库中的 skill 遵循 WorkBuddy Skill 规范：

- **SKILL.md**: 必需，包含 YAML frontmatter 和 Markdown 指令
- **scripts/**: 可选，可执行脚本
- **references/**: 可选，参考文档
- **assets/**: 可选，输出资源模板

## 版本管理

- 每个 skill 独立版本管理
- Release 打标签发布
- 变更记录在各 skill 目录下的 CHANGELOG.md（如有）

## 许可证

MIT License - 可自由使用、修改和分发

## 维护者

[@wq180705550-cmd](https://github.com/wq180705550-cmd)

**创建时间**: 2026-06-24
