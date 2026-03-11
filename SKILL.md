---
name: github-notifier
description: "Monitor GitHub repositories for new PRs, issues, and notifications. Get real-time alerts and auto-generated response drafts."
---

# GitHub Notifier Skill

监控 GitHub 仓库动态，自动通知 PR/Issue 状态变化。

## 功能

### 1. 监控仓库

```bash
# 添加监控的仓库
/github-notifier watch JerryZ01/CLI-Anything

# 查看监控列表
/github-notifier list

# 移除监控
/github-notifier unwatch JerryZ01/CLI-Anything
```

### 2. 检查通知

```bash
# 检查所有监控仓库的通知
/github-notifier check

# 检查特定仓库
/github-notifier check JerryZ01/CLI-Anything

# 查看未读通知
/github-notifier unread
```

### 3. 通知设置

```bash
# 设置通知频率
/github-notifier config interval 30  # 每 30 分钟检查一次

# 设置通知类型
/github-notifier config types pr,issue,mention  # 只通知 PR、Issue 和@提及

# 设置优先级过滤
/github-notifier config min-priority medium  # 只显示中等及以上优先级
```

### 4. 自动生成回复

```bash
# 为 PR 生成回复草稿
/github-notifier reply pr 33

# 为 Issue 生成回复草稿
/github-notifier reply issue 18
```

## 实现细节

### 使用的 API

- GitHub REST API v3
- GitHub GraphQL API v4（用于复杂查询）

### 通知类型

1. **PR 相关**
   - 新 PR 创建
   - PR 状态变化（open/closed/merged）
   - PR 评论
   - CI 检查失败
   - Code Review 请求

2. **Issue 相关**
   - 新 Issue 创建
   - Issue 状态变化
   - Issue 评论
   - 被@提及

3. **仓库相关**
   - 新的 Star
   - 新的 Fork
   - 新的 Release

### 优先级分类

**高优先级**（立即通知）：
- PR 被 Merge
- CI 检查失败
- 被@提及
- 紧急 Issue

**中优先级**（每小时汇总）：
- 新 PR
- 新 Issue
- PR 评论

**低优先级**（每天汇总）：
- 新的 Star
- 新的 Fork

## 配置示例

```yaml
# ~/.openclaw/github-notifier.yaml
repositories:
  - JerryZ01/CLI-Anything
  - JerryZ01/openclaw-skills

notifications:
  interval: 30  # 分钟
  types:
    - pr
    - issue
    - mention
  priority_filter: medium

channel:
  type: webchat  # 或 telegram/discord/qqbot
```

## 依赖

- GitHub Personal Access Token（已在 MEMORY.md 配置）
- `gh` CLI 工具（可选，用于本地命令）
- Python `requests` 库

## 使用示例

### 示例 1：监控开源项目

```bash
# 添加监控
/github-notifier watch HKUDS/CLI-Anything

# 设置每 15 分钟检查
/github-notifier config interval 15

# 等待通知...
# 15 分钟后：
# "🔔 [CLI-Anything] PR #33 状态变化：Open → Merged 🎉"
```

### 示例 2：自动生成回复

```bash
# 收到新 Issue 时
/github-notifier reply issue 42

# AI 生成回复草稿：
# "感谢反馈！这个问题我们已经复现，会在下个版本修复。
# 请问你的环境是？（操作系统/Python 版本）"
```

### 示例 3：每日汇总报告

```bash
# 每天早上 9 点自动发送
📊 GitHub 日报 (2026-03-12)

🏗️ JerryZ01/CLI-Anything
  ✅ PR #33 merged (fix: auto-save project)
  ⚠️  PR #34 checks failed
  💬 3 new comments

🌟 新增 5 stars
🍴 新增 2 forks
```

## 待办事项

- [ ] 实现基础监控功能
- [ ] 添加通知渠道（webchat/telegram/discord）
- [ ] 实现优先级分类
- [ ] 添加自动回复生成
- [ ] 实现每日汇总报告
- [ ] 添加 Webhook 支持（实时通知）
- [ ] 支持多个 GitHub 账号
- [ ] 添加通知历史记录

## 参考资料

- GitHub API 文档：https://docs.github.com/en/rest
- GitHub Webhook：https://docs.github.com/en/developers/webhooks-and-events
- OpenClaw Skill 开发指南：https://docs.openclaw.ai/skills
