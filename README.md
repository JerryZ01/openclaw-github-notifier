# GitHub Notifier Skill for OpenClaw

监控 GitHub 仓库动态，自动通知 PR/Issue 状态变化。

## 🚀 快速开始

### 1. 安装

技能已经在 `~/.openclaw/workspace/skills/github-notifier/` 目录

### 2. 配置 Token

Token 已从 MEMORY.md 自动读取，无需额外配置。

### 3. 使用

```bash
# 添加监控的仓库
/github-notifier watch JerryZ01/CLI-Anything

# 查看监控列表
/github-notifier list

# 检查通知
/github-notifier check

# 检查特定仓库
/github-notifier check JerryZ01/CLI-Anything

# 生成回复草稿
/github-notifier reply pr 33

# 每日汇总报告
/github-notifier report
```

## 📋 命令参考

| 命令 | 说明 | 示例 |
|------|------|------|
| `watch <repo>` | 添加监控仓库 | `/github-notifier watch JerryZ01/CLI-Anything` |
| `unwatch <repo>` | 移除监控仓库 | `/github-notifier unwatch JerryZ01/CLI-Anything` |
| `list` | 列出监控列表 | `/github-notifier list` |
| `check [repo]` | 检查通知 | `/github-notifier check` |
| `reply <pr\|issue> <number>` | 生成回复草稿 | `/github-notifier reply pr 33` |
| `report` | 每日汇总报告 | `/github-notifier report` |

## 🔔 通知类型

### PR 相关
- 新 PR 创建
- PR 状态变化（open/closed/merged）
- PR 评论
- CI 检查状态

### Issue 相关
- 新 Issue 创建
- Issue 状态变化
- Issue 评论
- 被@提及

### 仓库统计
- 新增 Stars
- 新增 Forks
- 新 Release

## 📊 示例输出

### 检查通知

```
📬 5 notifications:

🔀 [JerryZ01/CLI-Anything] PR #33: fix: auto-save project after layer and text operations
   by @JerryZ01 • https://github.com/HKUDS/CLI-Anything/pull/33

📝 [JerryZ01/CLI-Anything] ISSUE #18: Bug in Windows backend
   by @Laplace5079 • https://github.com/HKUDS/CLI-Anything/issues/18
```

### 每日报告

```
📊 GitHub 日报 (2026-03-12)

🏗️ JerryZ01/CLI-Anything
  ✅ PR #33 merged (fix: auto-save project)
  ⚠️  PR #34 checks failed
  🌟 28 stars
  🍴 5 forks

🏗️ JerryZ01/openclaw-skills
  ✅ PR #5 merged (Add weather skill)
  🌟 12 stars
  🍴 2 forks
```

### 生成回复

```json
{
  "success": true,
  "draft": "Thanks for the PR! Let me review it and get back to you soon. 👍",
  "item": {
    "type": "pr",
    "number": 33,
    "title": "fix: auto-save project after layer and text operations",
    "user": "JerryZ01"
  }
}
```

## 🛠️ 开发说明

### 文件结构

```
github-notifier/
├── SKILL.md              # Skill 文档（OpenClaw 读取）
├── github_notifier.py    # 主程序
├── README.md             # 使用说明
└── test.py               # 测试脚本
```

### 依赖

- Python 3.10+
- `requests` 库

### 添加新功能

1. 在 `github_notifier.py` 添加新方法
2. 在 `main()` 函数添加命令处理
3. 更新 `SKILL.md` 文档
4. 运行测试

### 测试

```bash
cd /home/zhanganjie/.openclaw/workspace/skills/github-notifier
python3 test.py
```

## 🎯 待办事项

- [ ] 添加 Webhook 支持（实时通知）
- [ ] 实现优先级分类
- [ ] 添加通知历史记录
- [ ] 支持多个 GitHub 账号
- [ ] 添加通知渠道（Telegram/Discord/微信）
- [ ] 实现智能回复（调用 LLM）
- [ ] 添加通知过滤规则
- [ ] 实现定时检查（cron）

## 📚 参考资料

- [GitHub API 文档](https://docs.github.com/en/rest)
- [OpenClaw Skill 开发指南](https://docs.openclaw.ai/skills)
- [GitHub Webhook](https://docs.github.com/en/developers/webhooks-and-events)

## 🤝 贡献

欢迎提交 Issue 和 PR！

## 📄 License

MIT License
