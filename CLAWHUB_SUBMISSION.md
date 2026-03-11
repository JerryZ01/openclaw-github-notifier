# ClawdHub Skill Submission - GitHub Notifier

## Skill Information

**Name**: github-notifier  
**Version**: 1.0.0  
**Author**: JerryZ01  
**License**: MIT  
**Category**: Developer Tools / Productivity  

## Description

Monitor GitHub repositories for new PRs, issues, and notifications. Get real-time alerts and auto-generated response drafts.

Perfect for open source contributors and maintainers who want to stay on top of their repository activity.

## Features

- 🔍 **Monitor Multiple Repositories** - Watch any number of GitHub repos
- 📬 **Real-time Notifications** - Get alerts for new PRs, issues, and comments
- 🤖 **Auto-reply Generation** - AI-powered reply drafts for PRs/issues
- 📊 **Daily Summary Reports** - Get consolidated activity reports
- 🎯 **Priority Filtering** - Focus on what matters most

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `watch` | Add repository to watch list | `/github-notifier watch HKUDS/CLI-Anything` |
| `unwatch` | Remove repository from watch list | `/github-notifier unwatch owner/repo` |
| `list` | List all watched repositories | `/github-notifier list` |
| `check` | Check for new notifications | `/github-notifier check` |
| `reply` | Generate reply draft | `/github-notifier reply pr 33` |
| `report` | Generate daily summary | `/github-notifier report` |

## Installation

### Method 1: OpenClaw CLI
```bash
openclaw plugins install github-notifier
```

### Method 2: Git Clone
```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/JerryZ01/openclaw-github-notifier.git
```

### Method 3: ClawdHub UI
Visit https://clawhub.ai/skills/github-notifier and click Install

## Usage Examples

### Watch a Repository
```bash
/github-notifier watch HKUDS/CLI-Anything
```

### Check Notifications
```bash
/github-notifier check
```

Output:
```
📬 5 notifications:

🔀 [HKUDS/CLI-Anything] PR #33: fix: auto-save project
   by @JerryZ01 • https://github.com/HKUDS/CLI-Anything/pull/33
```

### Generate Reply
```bash
/github-notifier reply pr 33
```

Output:
```json
{
  "draft": "Thanks for the PR! Let me review it and get back to you soon. 👍"
}
```

### Daily Report
```bash
/github-notifier report
```

Output:
```
📊 GitHub 日报 (2026-03-12)

🏗️ HKUDS/CLI-Anything
  ✅ PR #33 merged
  🌟 28 stars
  🍴 5 forks
```

## Requirements

- Python 3.10+
- requests library
- GitHub Personal Access Token (auto-detected from environment)

## Configuration

The skill automatically reads GitHub token from:
1. `GITHUB_TOKEN` environment variable
2. OpenClaw MEMORY.md configuration

## Permissions

- GitHub API access (read-only for notifications)
- Local file system (for configuration storage)

## Links

- **GitHub Repository**: https://github.com/JerryZ01/openclaw-github-notifier
- **Issue Tracker**: https://github.com/JerryZ01/openclaw-github-notifier/issues
- **Documentation**: https://github.com/JerryZ01/openclaw-github-notifier/blob/main/README.md

## Changelog

### v1.0.0 (2026-03-12)

- Initial release
- Repository monitoring
- PR/Issue notifications
- Auto-reply generation
- Daily summary reports

## Author

**JerryZ01**
- GitHub: https://github.com/JerryZ01
- Notable Contributions: CLI-Anything PR #33 (bug fix)

## License

MIT License - See LICENSE file for details

---

## Submission Checklist

- [x] Skill developed and tested
- [x] GitHub repository created
- [x] Code pushed to GitHub
- [x] README.md complete
- [x] SKILL.md complete
- [x] manifest.json configured
- [x] Version 1.0.0 tagged
- [x] License included
- [x] Documentation complete

## Notes for ClawdHub Reviewers

This skill was developed and tested on 2026-03-12. It successfully:
- Monitors GitHub repositories
- Detects new PRs and issues
- Generates notification summaries
- Creates AI-powered reply drafts

The skill is production-ready and has been tested with real GitHub repositories (HKUDS/CLI-Anything).
