#!/usr/bin/env python3
"""
GitHub Notifier Skill - 测试脚本
"""

import sys
sys.path.insert(0, '/home/zhanganjie/.openclaw/workspace/skills/github-notifier')

from github_notifier import GitHubNotifier


def test_all():
    """运行所有测试"""
    print("=" * 60)
    print("GitHub Notifier Skill - 测试套件")
    print("=" * 60)
    print()
    
    # 测试 1: 初始化
    print("[测试 1] 初始化 GitHub Notifier...")
    try:
        notifier = GitHubNotifier()
        print("✅ 初始化成功")
        print(f"   Token: {'已配置' if notifier.token else '❌ 未配置'}")
    except Exception as e:
        print(f"❌ 初始化失败：{e}")
        return
    print()
    
    # 测试 2: 查看监控列表
    print("[测试 2] 查看监控列表...")
    repos = notifier.list_watched()
    if repos:
        print(f"✅ 当前监控 {len(repos)} 个仓库:")
        for repo in repos:
            print(f"   - {repo}")
    else:
        print("⚠️  暂无监控的仓库")
    print()
    
    # 测试 3: 添加监控（可选）
    print("[测试 3] 添加监控仓库...")
    print("   提示：运行以下命令添加监控")
    print("   /github-notifier watch JerryZ01/CLI-Anything")
    print()
    
    # 测试 4: 检查通知
    print("[测试 4] 检查通知...")
    if repos:
        try:
            notifications = notifier.check_notifications(repos[0])
            print(f"✅ 获取到 {len(notifications)} 条通知")
            for n in notifications[:3]:
                icon = "🔀" if n['type'] == 'pr' else "📝"
                print(f"   {icon} #{n['number']}: {n['title']}")
        except Exception as e:
            print(f"❌ 检查失败：{e}")
    else:
        print("⚠️  先添加监控的仓库")
    print()
    
    # 测试 5: 生成回复
    print("[测试 5] 生成回复草稿...")
    if repos:
        try:
            result = notifier.generate_reply(repos[0], 'pr', 33)
            if 'success' in result:
                print(f"✅ 生成回复草稿:")
                print(f"   \"{result['draft']}\"")
            else:
                print(f"⚠️  {result.get('error', '未知错误')}")
        except Exception as e:
            print(f"❌ 生成失败：{e}")
    else:
        print("⚠️  先添加监控的仓库")
    print()
    
    # 测试 6: 每日报告
    print("[测试 6] 生成每日报告...")
    if repos:
        try:
            report = notifier.daily_report()
            print("✅ 每日报告:")
            print(report[:500] + "..." if len(report) > 500 else report)
        except Exception as e:
            print(f"❌ 生成失败：{e}")
    else:
        print("⚠️  先添加监控的仓库")
    print()
    
    # 总结
    print("=" * 60)
    print("测试完成！")
    print("=" * 60)
    print()
    print("📝 使用技能:")
    print("   /github-notifier watch JerryZ01/CLI-Anything")
    print("   /github-notifier check")
    print("   /github-notifier report")
    print()


if __name__ == '__main__':
    test_all()
