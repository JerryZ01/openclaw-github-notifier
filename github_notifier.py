#!/usr/bin/env python3
"""
GitHub Notifier - OpenClaw Skill
监控 GitHub 仓库动态，自动通知 PR/Issue 状态变化
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional


class GitHubNotifier:
    """GitHub 通知器"""
    
    def __init__(self, token: str = None):
        """初始化
        
        Args:
            token: GitHub Personal Access Token
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            # 从 MEMORY.md 读取 token
            memory_path = Path.home() / '.openclaw' / 'workspace' / 'MEMORY.md'
            if memory_path.exists():
                content = memory_path.read_text()
                for line in content.split('\n'):
                    if 'Personal Access Token:' in line:
                        self.token = line.split(':')[1].strip()
                        break
        
        if not self.token:
            raise ValueError("GitHub token not found. Set GITHUB_TOKEN env var or configure in MEMORY.md")
        
        self.api_base = "https://api.github.com"
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # 配置文件路径
        self.config_path = Path.home() / '.openclaw' / 'github-notifier.yaml'
        self.watched_repos = []
        self.load_config()
    
    def load_config(self):
        """加载配置"""
        if self.config_path.exists():
            # 简单 YAML 解析（实际应该用 pyyaml）
            content = self.config_path.read_text()
            for line in content.split('\n'):
                if line.strip().startswith('- '):
                    repo = line.strip()[2:]
                    if '/' in repo:
                        self.watched_repos.append(repo)
    
    def save_config(self):
        """保存配置"""
        config_dir = self.config_path.parent
        config_dir.mkdir(parents=True, exist_ok=True)
        
        content = "# GitHub Notifier Configuration\n\nrepositories:\n"
        for repo in self.watched_repos:
            content += f"  - {repo}\n"
        
        self.config_path.write_text(content)
    
    def watch(self, repo: str) -> Dict:
        """添加监控的仓库
        
        Args:
            repo: 仓库全名 (owner/repo)
            
        Returns:
            操作结果
        """
        if '/' not in repo:
            return {'error': 'Invalid repo format. Use owner/repo'}
        
        if repo in self.watched_repos:
            return {'message': f'Already watching {repo}'}
        
        # 验证仓库是否存在
        owner, name = repo.split('/')
        url = f"{self.api_base}/repos/{owner}/{name}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 404:
            return {'error': f'Repository {repo} not found'}
        elif response.status_code != 200:
            return {'error': f'Failed to verify repo: {response.status_code}'}
        
        self.watched_repos.append(repo)
        self.save_config()
        
        return {
            'success': True,
            'message': f'Now watching {repo}',
            'repo': repo
        }
    
    def unwatch(self, repo: str) -> Dict:
        """移除监控的仓库
        
        Args:
            repo: 仓库全名
            
        Returns:
            操作结果
        """
        if repo not in self.watched_repos:
            return {'error': f'Not watching {repo}'}
        
        self.watched_repos.remove(repo)
        self.save_config()
        
        return {
            'success': True,
            'message': f'Stopped watching {repo}'
        }
    
    def list_watched(self) -> List[str]:
        """列出监控的仓库
        
        Returns:
            仓库列表
        """
        return self.watched_repos
    
    def check_notifications(self, repo: str = None) -> List[Dict]:
        """检查通知
        
        Args:
            repo: 可选，指定仓库
            
        Returns:
            通知列表
        """
        notifications = []
        
        repos_to_check = [repo] if repo else self.watched_repos
        
        for repo in repos_to_check:
            owner, name = repo.split('/')
            
            # 获取 PR
            pr_url = f"{self.api_base}/repos/{owner}/{name}/pulls"
            pr_response = requests.get(pr_url, headers=self.headers)
            if pr_response.status_code == 200:
                prs = pr_response.json()[:5]  # 最近 5 个 PR
                for pr in prs:
                    notifications.append({
                        'type': 'pr',
                        'repo': repo,
                        'number': pr['number'],
                        'title': pr['title'],
                        'state': pr['state'],
                        'user': pr['user']['login'],
                        'created_at': pr['created_at'],
                        'url': pr['html_url']
                    })
            
            # 获取 Issue
            issue_url = f"{self.api_base}/repos/{owner}/{name}/issues"
            issue_response = requests.get(issue_url, headers=self.headers)
            if issue_response.status_code == 200:
                issues = issue_response.json()[:5]  # 最近 5 个 Issue
                for issue in issues:
                    # 排除 PR（GitHub API 中 PR 也是 issue）
                    if 'pull_request' not in issue:
                        notifications.append({
                            'type': 'issue',
                            'repo': repo,
                            'number': issue['number'],
                            'title': issue['title'],
                            'state': issue['state'],
                            'user': issue['user']['login'],
                            'created_at': issue['created_at'],
                            'url': issue['html_url']
                        })
        
        # 按时间排序
        notifications.sort(key=lambda x: x['created_at'], reverse=True)
        
        return notifications
    
    def get_pr_checks(self, repo: str, pr_number: int) -> Dict:
        """获取 PR 的 CI 检查状态
        
        Args:
            repo: 仓库全名
            pr_number: PR 号
            
        Returns:
            CI 检查状态
        """
        owner, name = repo.split('/')
        url = f"{self.api_base}/repos/{owner}/{name}/commits/{pr_number}/status"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            return {'error': f'Failed to get checks: {response.status_code}'}
        
        data = response.json()
        return {
            'state': data.get('state', 'unknown'),
            'total_count': data.get('total_count', 0),
            'statuses': [
                {
                    'context': s['context'],
                    'state': s['state'],
                    'description': s.get('description', '')
                }
                for s in data.get('statuses', [])
            ]
        }
    
    def generate_reply(self, repo: str, item_type: str, number: int) -> Dict:
        """自动生成回复草稿
        
        Args:
            repo: 仓库全名
            item_type: 'pr' 或 'issue'
            number: PR/Issue 号
            
        Returns:
            回复草稿
        """
        owner, name = repo.split('/')
        # PR 在 GitHub API 中也是 issue，需要用 pulls 端点
        api_type = 'pulls' if item_type == 'pr' else 'issues'
        url = f"{self.api_base}/repos/{owner}/{name}/{api_type}/{number}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            return {'error': f'Failed to get {item_type}: {response.status_code}'}
        
        item = response.json()
        
        # 简单的 AI 回复生成（实际应该调用 LLM）
        if item_type == 'pr':
            if item['state'] == 'open':
                reply = f"Thanks for the PR! Let me review it and get back to you soon. 👍"
            else:
                reply = f"Thanks for your contribution! 🎉"
        else:  # issue
            if 'bug' in item['title'].lower() or 'error' in item['body'].lower():
                reply = f"Thanks for reporting this! Can you provide more details about your environment?\n- OS: ?\n- Python version: ?\n- Steps to reproduce: ?"
            else:
                reply = f"Thanks for the feedback! We'll look into this."
        
        return {
            'success': True,
            'draft': reply,
            'item': {
                'type': item_type,
                'number': number,
                'title': item['title'],
                'user': item['user']['login']
            }
        }
    
    def daily_report(self) -> str:
        """生成每日汇总报告
        
        Returns:
            报告文本
        """
        report = f"📊 GitHub 日报 ({datetime.now().strftime('%Y-%m-%d')})\n\n"
        
        for repo in self.watched_repos:
            owner, name = repo.split('/')
            report += f"🏗️ {repo}\n"
            
            # 获取今天合并的 PR
            pr_url = f"{self.api_base}/repos/{owner}/{name}/pulls"
            pr_params = {'state': 'closed', 'per_page': 10}
            pr_response = requests.get(pr_url, headers=self.headers, params=pr_params)
            
            if pr_response.status_code == 200:
                merged_prs = [pr for pr in pr_response.json() if pr.get('merged_at')]
                if merged_prs:
                    for pr in merged_prs[:3]:
                        report += f"  ✅ PR #{pr['number']} merged ({pr['title']})\n"
            
            # 获取仓库统计
            repo_url = f"{self.api_base}/repos/{owner}/{name}"
            repo_response = requests.get(repo_url, headers=self.headers)
            
            if repo_response.status_code == 200:
                repo_data = repo_response.json()
                report += f"🌟 {repo_data.get('stargazers_count', 0)} stars\n"
                report += f"🍴 {repo_data.get('forks_count', 0)} forks\n"
            
            report += "\n"
        
        return report


# OpenClaw Skill 入口
def main(command: str = None):
    """OpenClaw Skill 主函数
    
    Args:
        command: 命令行参数
    """
    notifier = GitHubNotifier()
    
    if not command:
        return "Usage: /github-notifier <command> [args]\nCommands: watch, unwatch, list, check, reply, report"
    
    parts = command.split()
    cmd = parts[0]
    
    if cmd == 'watch':
        if len(parts) < 2:
            return "Usage: /github-notifier watch owner/repo"
        result = notifier.watch(parts[1])
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    elif cmd == 'unwatch':
        if len(parts) < 2:
            return "Usage: /github-notifier unwatch owner/repo"
        result = notifier.unwatch(parts[1])
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    elif cmd == 'list':
        repos = notifier.list_watched()
        if not repos:
            return "Not watching any repositories"
        return "Watching:\n" + "\n".join(f"  - {repo}" for repo in repos)
    
    elif cmd == 'check':
        repo = parts[1] if len(parts) > 1 else None
        notifications = notifier.check_notifications(repo)
        if not notifications:
            return "No new notifications"
        
        result = f"📬 {len(notifications)} notifications:\n\n"
        for n in notifications[:10]:
            icon = "🔀" if n['type'] == 'pr' else "📝"
            result += f"{icon} [{n['repo']}] {n['type'].upper()} #{n['number']}: {n['title']}\n"
            result += f"   by @{n['user']} • {n['url']}\n"
        
        return result
    
    elif cmd == 'reply':
        if len(parts) < 3:
            return "Usage: /github-notifier reply <pr|issue> <number>"
        item_type = parts[1]
        number = int(parts[2])
        # 需要知道是哪个 repo，简化处理用第一个
        if not notifier.watched_repos:
            return "No watched repositories"
        result = notifier.generate_reply(notifier.watched_repos[0], item_type, number)
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    elif cmd == 'report':
        return notifier.daily_report()
    
    else:
        return f"Unknown command: {cmd}"


if __name__ == '__main__':
    import sys
    command = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else None
    print(main(command))
