"""数据库初始化 & 会话管理。

用法：
    from backend.database import init_db, get_db

    # 启动时调用一次
    init_db(app_config.database_url)

    # 每次请求获取一个会话
    db = get_db()
    db.add(...)
    db.commit()
    db.close()
"""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

_engine = None
_SessionLocal = None


def init_db(database_url: str) -> None:
    """创建引擎并建表。应用启动时调用一次即可。"""
    global _engine, _SessionLocal

    if not database_url:
        raise RuntimeError("DATABASE_URL 未配置，无法初始化数据库。")

    _engine = create_engine(
        database_url,
        # 开发阶段开启 echo 可以看到每条 SQL，生产请关掉
        echo=False,
        # 连接池：连接用完后自动回收
        pool_pre_ping=True,
    )
    _SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)

    # 自动建表（已有表则跳过，不会重复创建）
    from backend.models import Base  # noqa: F811  # 延迟导入，避免循环依赖

    Base.metadata.create_all(bind=_engine)


def get_db() -> Session:
    """获取一个新的数据库会话。用完记得 close()。"""
    if _SessionLocal is None:
        raise RuntimeError("数据库未初始化，请先调用 init_db()。")
    return _SessionLocal()
