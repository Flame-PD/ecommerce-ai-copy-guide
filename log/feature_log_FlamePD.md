# Feature Branch 开发日志

> 分支：feature
> 作者：FlamePD
> 日期：2026-07-13
> 基准：Milestone 1 骨架 → 推进至 AI 接入 + 数据库持久化

---

## 概述

本次开发完成了两项核心工作：

1. **AI 服务层改造**：将 Mock 假数据替换为 DeepSeek 大模型真调用，同时保留 Mock 作为 fallback
2. **数据库持久化**：设计并实现 PostgreSQL 表结构，每次 AI 调用自动写入历史记录

---

## 一、AI 服务层改造

### 1.1 抽象接口

新建 `backend/services/base.py`，定义 `BaseAIService` 抽象基类，统一四个业务方法的签名：

- `generate_copy(payload)` → 商品文案生成
- `recommend(payload)` → 智能导购推荐
- `analyze_reviews(payload)` → 评论情感分析
- `generate_live_script(payload)` → 直播脚本生成
- `capabilities()` → 能力清单（具体方法，子类可覆盖）

### 1.2 DeepSeek 大模型接入

新建 `backend/services/ai_deepseek.py`，类 `DeepSeekAIService`：

- 使用 Python 标准库 `urllib.request` 发 HTTP 请求（零额外依赖）
- 兼容 OpenAI API 格式（`/v1/chat/completions`）
- 调用流程：构造 system + user prompt → POST 到 DeepSeek → 安全解析 JSON 返回
- 提供 `_parse_json()` 兜底解析：去除 markdown 包裹 → 直接解析 → 首尾花括号匹配
- 每个业务方法内置 fallback：API 失败时自动降级到模板结果，保证前端不崩

### 1.3 工厂模式切换

修改 `backend/services/__init__.py`，新增 `create_ai_service(config)` 工厂函数：

- 当 `.env` 中 `AI_PROVIDER=deepseek` 且 `AI_API_KEY` 不为空 → `DeepSeekAIService`
- 否则 → `MockAIService`（和之前行为完全一致）

修改 `backend/api/routes.py`，所有端点改用 `_get_service()` 动态获取实例，不再写死 Mock。

### 1.4 配置扩展

修改 `backend/config.py`，`AppConfig` 新增字段：

- `ai_api_key` — 模型 API 密钥（从 `.env` 读取，不提交 Git）
- `ai_base_url` — API 接口地址（默认 `https://api.deepseek.com`）

`.env.example` 同步更新占位字段。

---

## 二、数据库持久化

### 2.1 设计文档

新建 `docs/design/database-schema.md`，包含：

- 5 张表的完整字段说明与 ER 图
- 各表的写入时机和使用场景
- JSONB 字段查询示例
- MySQL/PostgreSQL 切换指南

### 2.2 ORM 模型

新建 `backend/models.py`，使用 SQLAlchemy 2.0 声明式 API，定义 5 张表：

| 表名 | 说明 |
|---|---|
| `products` | 商品基础信息（name, category, description, source_url） |
| `reviews` | 用户评论（FK → products，含 sentiment 情绪标注字段） |
| `generation_tasks` | **核心表**：每次 AI 调用的完整 request + result（JSONB），含 task_type、ai_provider、status 等查询字段 |
| `sessions` | 多轮导购对话上下文 |
| `recommendation_records` | 导购推荐结构化记录，关联 task 和 session |

### 2.3 数据库初始化

新建 `backend/database.py`：

- `init_db(database_url)` — 创建 SQLAlchemy 引擎和会话工厂，自动建表
- `get_db()` — 每次请求获取独立数据库会话

修改 `backend/app.py`，`create_app()` 启动时自动调 `init_db()`（仅当 `DATABASE_URL` 已配置）。

### 2.4 历史记录自动写入

修改 `backend/api/routes.py`，新增私有函数 `_save_task()`：

- 每次 AI 调用成功后自动写入 `generation_tasks` 表
- 数据库不可用时静默跳过，不影响 API 正常返回

新增 `GET /api/history` 端点：

- 按 `task_type` 筛选（可选）
- 按创建时间倒序
- 支持 `limit` 参数（默认 20，上限 100）

---

## 三、测试适配

修改 `tests/test_api.py`：

- `test_capabilities`：`mode` 断言从 `== "mock"` 改为 `in ("mock", "deepseek")`
- `test_generate_copy`：不再检查 `product_name` 原样出现在 title 中（AI 会改写），改为检查四个输出字段都存在且有值

---

## 四、文件变更清单

### 新增（6 个文件）

```
backend/services/base.py
backend/services/ai_deepseek.py
backend/models.py
backend/database.py
docs/design/database-schema.md
log/feature_FlamePD.log          ← 本文件
```

### 修改（8 个文件）

```
backend/config.py
backend/services/ai_mock.py
backend/services/__init__.py
backend/api/routes.py
backend/app.py
requirements.txt
tests/test_api.py
.env.example
```

---

## 五、后续待办

- [ ] 前端路由拆分 + 四个功能页面（`vue-router`）
- [ ] AI 流式输出（SSE + 打字机效果）
- [ ] Scrapy 爬虫抓取商品/评论演示数据
- [ ] Redis 缓存热点商品和会话上下文
- [ ] Alembic 数据库迁移管理（替代 `create_all` 自动建表）
- [ ] 管理后台 / 数据看板
