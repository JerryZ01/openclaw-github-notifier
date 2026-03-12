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
                        # Handle markdown formatting (e.g., "**Token:** value")
                        token_part = line.split(':')[-1].strip()
                        # Remove markdown bold/italic markers
                        import re
                        self.token = re.sub(r'\*+', '', token_part).strip()
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
    
    def get_repo_stats(self, repo: str) -> Dict:
        """获取仓库统计信息
        
        Args:
            repo: 仓库全名
            
        Returns:
            统计数据
        """
        owner, name = repo.split('/')
        url = f"{self.api_base}/repos/{owner}/{name}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            return {'error': f'Failed to get stats: {response.status_code}'}
        
        data = response.json()
        return {
            'stars': data.get('stargazers_count', 0),
            'forks': data.get('forks_count', 0),
            'watchers': data.get('watchers_count', 0),
            'open_issues': data.get('open_issues_count', 0),
            'subscribers': data.get('subscribers_count', 0),
            'language': data.get('language', ''),
            'updated_at': data.get('updated_at', '')
        }
    
    def get_recent_activity(self, repo: str, days: int = 7) -> Dict:
        """获取最近 N 天的仓库活动
        
        Args:
            repo: 仓库全名
            days: 天数
            
        Returns:
            活动统计
        """
        owner, name = repo.split('/')
        since = (datetime.now() - timedelta(days=days)).isoformat()
        
        activity = {
            'prs': 0,
            'issues': 0,
            'commits': 0,
            'releases': 0
        }
        
        # 获取 PR
        pr_url = f"{self.api_base}/repos/{owner}/{name}/pulls"
        pr_response = requests.get(pr_url, headers=self.headers, params={'state': 'all', 'per_page': 100})
        if pr_response.status_code == 200:
            for pr in pr_response.json():
                if pr['created_at'] > since:
                    activity['prs'] += 1
        
        # 获取 Issue
        issue_url = f"{self.api_base}/repos/{owner}/{name}/issues"
        issue_response = requests.get(issue_url, headers=self.headers, params={'state': 'all', 'per_page': 100})
        if issue_response.status_code == 200:
            for issue in issue_response.json():
                if 'pull_request' not in issue and issue['created_at'] > since:
                    activity['issues'] += 1
        
        # 获取 Commits
        commits_url = f"{self.api_base}/repos/{owner}/{name}/commits"
        commits_response = requests.get(commits_url, headers=self.headers, params={'per_page': 100, 'since': since})
        if commits_response.status_code == 200:
            activity['commits'] = len(commits_response.json())
        
        # 获取 Releases
        releases_url = f"{self.api_base}/repos/{owner}/{name}/releases"
        releases_response = requests.get(releases_url, headers=self.headers)
        if releases_response.status_code == 200:
            for release in releases_response.json():
                if release['created_at'] > since:
                    activity['releases'] += 1
        
        return activity
    
    def check_mentions(self) -> List[Dict]:
        """检查@提及
        
        Returns:
            提及列表
        """
        mentions = []
        
        # 获取当前用户
        user_url = f"{self.api_base}/user"
        user_response = requests.get(user_url, headers=self.headers)
        if user_response.status_code != 200:
            return mentions
        
        username = user_response.json()['login']
        
        # 搜索提及
        search_url = f"{self.api_base}/search/issues"
        search_params = {
            'q': f'"{username}" in:comment author:not:{username}',
            'sort': 'updated',
            'per_page': 10
        }
        search_response = requests.get(search_url, headers=self.headers, params=search_params)
        
        if search_response.status_code == 200:
            for item in search_response.json().get('items', []):
                mentions.append({
                    'type': 'mention',
                    'repo': item['repository_url'].split('/')[-2] + '/' + item['repository_url'].split('/')[-1],
                    'number': item['number'],
                    'title': item['title'],
                    'url': item['html_url'],
                    'updated_at': item['updated_at']
                })
        
        return mentions
    
    def daily_report(self, include_stats: bool = True) -> str:
        """生成每日汇总报告
        
        Args:
            include_stats: 是否包含仓库统计
            
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
                
                # 检查今天新开的 PR
                new_prs = [pr for pr in pr_response.json() if pr['state'] == 'open']
                if new_prs:
                    report += f"  🔀 {len(new_prs)} open PRs\n"
            
            # 获取仓库统计
            if include_stats:
                stats = self.get_repo_stats(repo)
                if 'error' not in stats:
                    report += f"  🌟 {stats['stars']} stars"
                    if stats['forks'] > 0:
                        report += f"  🍴 {stats['forks']} forks"
                    report += "\n"
            
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
    
    elif cmd == 'stats':
        if len(parts) < 2:
            # 显示所有监控仓库的统计
            if not notifier.watched_repos:
                return "No watched repositories"
            result = "📊 Repository Stats:\n\n"
            for repo in notifier.watched_repos:
                stats = notifier.get_repo_stats(repo)
                if 'error' not in stats:
                    result += f"🏗️ {repo}\n"
                    result += f"   🌟 {stats['stars']} stars  🍴 {stats['forks']} forks\n"
                    result += f"   📝 {stats['open_issues']} open issues\n"
                    if stats['language']:
                        result += f"   💻 {stats['language']}\n"
                    result += "\n"
            return result
        else:
            stats = notifier.get_repo_stats(parts[1])
            return json.dumps(stats, indent=2, ensure_ascii=False)
    
    elif cmd == 'activity':
        days = int(parts[2]) if len(parts) > 2 else 7
        if len(parts) < 2:
            return "Usage: /github-notifier activity owner/repo [days]"
        activity = notifier.get_recent_activity(parts[1], days)
        return f"📈 {parts[1]} - Last {days} days:\n" + \
               f"  🔀 {activity['prs']} PRs\n" + \
               f"  📝 {activity['issues']} Issues\n" + \
               f"  💻 {activity['commits']} Commits\n" + \
               f"  📦 {activity['releases']} Releases"
    
    elif cmd == 'mentions':
        mentions = notifier.check_mentions()
        if not mentions:
            return "No recent mentions"
        result = f"📬 {len(mentions)} mentions:\n\n"
        for m in mentions[:10]:
            result += f"🔔 [{m['repo']}] #{m['number']}: {m['title']}\n"
            result += f"   {m['url']}\n"
        return result
    
    else:
        return f"Unknown command: {cmd}\nCommands: watch, unwatch, list, check, reply, report, stats, activity, mentions"


if __name__ == '__main__':
    import sys
    command = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else None
    print(main(command))
