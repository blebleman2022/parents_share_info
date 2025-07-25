#!/usr/bin/env python3
"""
年级管理命令行工具
"""
import asyncio
import sys
import argparse
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.database import AsyncSessionLocal
from app.services.grade_service import grade_service
from app.models.user import User
from sqlalchemy import select


async def list_users_grades(db):
    """列出所有用户的年级信息"""
    result = await db.execute(
        select(User.id, User.nickname, User.child_grade, User.last_grade_upgrade_year)
        .where(User.is_active == True)
        .order_by(User.id)
    )
    
    users = result.all()
    
    print(f"\n📚 用户年级信息（共 {len(users)} 个用户）")
    print("=" * 60)
    print(f"{'ID':<5} {'昵称':<15} {'当前年级':<12} {'最后升级年份':<10}")
    print("-" * 60)
    
    for user_id, nickname, grade, last_upgrade_year in users:
        upgrade_year_str = str(last_upgrade_year) if last_upgrade_year else "未升级"
        print(f"{user_id:<5} {nickname:<15} {grade:<12} {upgrade_year_str:<10}")


async def upgrade_all_grades(db, force=False):
    """升级所有用户的年级"""
    current_year = datetime.now().year
    
    if not force and not grade_service.should_upgrade_grade():
        print("❌ 当前不是升级时间（9月1日后），使用 --force 参数强制升级")
        return
    
    print("🚀 开始批量升级用户年级...")
    
    # 获取升级前的统计
    result = await db.execute(
        select(User.child_grade, User.last_grade_upgrade_year)
        .where(User.is_active == True)
    )
    users_before = result.all()
    
    # 执行升级
    upgraded_count = await grade_service.upgrade_all_users_grade(db, force=force)
    
    if upgraded_count > 0:
        print(f"✅ 升级完成！共升级了 {upgraded_count} 个用户的年级")
        
        # 显示升级后的统计
        await list_users_grades(db)
    else:
        print("ℹ️ 没有需要升级的用户")


async def upgrade_user_grade(db, user_id, force=False):
    """升级指定用户的年级"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        print(f"❌ 用户 ID {user_id} 不存在")
        return
    
    print(f"👤 用户信息：{user.nickname} - 当前年级：{user.child_grade}")
    
    if not force and not grade_service.should_upgrade_grade():
        print("❌ 当前不是升级时间（9月1日后），使用 --force 参数强制升级")
        return
    
    old_grade = user.child_grade
    success = await grade_service.upgrade_user_grade(db, user, force=force)
    
    if success:
        await db.refresh(user)
        print(f"✅ 升级成功：{old_grade} → {user.child_grade}")
    else:
        print("ℹ️ 用户年级无需升级或已经升级过")


async def reset_upgrade_year(db, year=None):
    """重置升级年份（用于测试）"""
    if year is None:
        year = datetime.now().year - 1
    
    result = await db.execute(select(User).where(User.is_active == True))
    users = result.scalars().all()
    
    for user in users:
        user.last_grade_upgrade_year = year
    
    await db.commit()
    print(f"✅ 已将所有用户的最后升级年份重置为 {year}")


async def main():
    parser = argparse.ArgumentParser(description="年级管理工具")
    parser.add_argument("command", choices=["list", "upgrade-all", "upgrade-user", "reset-year"], 
                       help="执行的命令")
    parser.add_argument("--user-id", type=int, help="用户ID（用于upgrade-user命令）")
    parser.add_argument("--force", action="store_true", help="强制执行（忽略时间限制）")
    parser.add_argument("--year", type=int, help="年份（用于reset-year命令）")
    
    args = parser.parse_args()
    
    async with AsyncSessionLocal() as db:
        if args.command == "list":
            await list_users_grades(db)
            
        elif args.command == "upgrade-all":
            await upgrade_all_grades(db, args.force)
            
        elif args.command == "upgrade-user":
            if not args.user_id:
                print("❌ 请指定用户ID：--user-id <ID>")
                return
            await upgrade_user_grade(db, args.user_id, args.force)
            
        elif args.command == "reset-year":
            await reset_upgrade_year(db, args.year)


if __name__ == "__main__":
    print("🎓 K12年级管理工具")
    print("=" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 操作已取消")
    except Exception as e:
        print(f"❌ 执行失败: {e}")
    
    print("\n💡 使用说明：")
    print("  python manage_grades.py list                    # 查看所有用户年级")
    print("  python manage_grades.py upgrade-all             # 批量升级年级")
    print("  python manage_grades.py upgrade-all --force     # 强制批量升级")
    print("  python manage_grades.py upgrade-user --user-id 1 # 升级指定用户")
    print("  python manage_grades.py reset-year --year 2023  # 重置升级年份（测试用）")
