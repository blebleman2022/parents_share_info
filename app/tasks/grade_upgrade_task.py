"""
年级升级定时任务
"""
import asyncio
import logging
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.services.grade_service import grade_service

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_grade_upgrade_task():
    """
    运行年级升级任务
    每年9月1日自动执行
    """
    logger.info("开始执行年级升级任务...")
    
    try:
        async with AsyncSessionLocal() as db:
            # 批量升级所有用户的年级
            upgraded_count = await grade_service.upgrade_all_users_grade(db)
            
            if upgraded_count > 0:
                logger.info(f"年级升级任务完成，共升级了 {upgraded_count} 个用户的年级")
            else:
                logger.info("年级升级任务完成，没有需要升级的用户")
                
    except Exception as e:
        logger.error(f"年级升级任务执行失败: {e}")


async def check_and_run_grade_upgrade():
    """
    检查是否需要运行年级升级任务
    """
    now = datetime.now()
    current_year = now.year
    
    # 检查是否是9月1日
    upgrade_date = date(current_year, 9, 1)
    today = date.today()
    
    if today == upgrade_date:
        logger.info("今天是9月1日，开始执行年级升级任务")
        await run_grade_upgrade_task()
    else:
        logger.info(f"今天不是升级日期（9月1日），当前日期：{today}")


if __name__ == "__main__":
    # 可以直接运行此脚本来手动执行年级升级
    asyncio.run(run_grade_upgrade_task())
