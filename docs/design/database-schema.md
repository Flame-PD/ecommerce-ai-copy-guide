# 数据库设计文档

> 最后更新：2026-07-13  
> 数据库：PostgreSQL 16  
> ORM：SQLAlchemy 2.0+

---

## 一、表结构总览

```
┌──────────┐     ┌─────────────────┐     ┌──────────────────────────┐
│ products │────<│ generation_tasks │────<│ recommendation_records   │
└──────────┘     └─────────────────┘     └──────────────────────────┘
     │                                              │
     │              ┌──────────┐                    │
     └─────────────<│ reviews  │     ┌──────────┐   │
                    └──────────┘     │ sessions │───┘
                                     └──────────┘
```

共 5 张表：

| 表名 | 用途 | 写入时机 |
|---|---|---|
| `products` | 商品基础信息 | 手动录入 / 爬虫写入 |
| `reviews` | 用户评论 | 手动录入 / 爬虫写入 |
| `generation_tasks` | 每次 AI 调用的请求 & 结果 | 每次 API 调用自动写入 |
| `recommendation_records` | 导购推荐结构化记录 | 导购 API 调用时写入 |
| `sessions` | 多轮对话上下文 | 导购会话创建时写入 |

---

## 二、各表详细字段

### 2.1 products（商品表）

| 列名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `id` | `SERIAL` | ✅ | 主键，自增 |
| `name` | `VARCHAR(200)` | ✅ | 商品名称 |
| `category` | `VARCHAR(100)` | | 商品分类（如「办公家具」） |
| `description` | `TEXT` | | 商品详情描述 |
| `source_url` | `VARCHAR(500)` | | 数据来源 URL（爬虫用） |
| `created_at` | `TIMESTAMPTZ` | ✅ | 创建时间，默认 `now()` |

### 2.2 reviews（评论表）

| 列名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `id` | `SERIAL` | ✅ | 主键，自增 |
| `product_id` | `INTEGER` | ✅ | 外键 → `products.id` |
| `content` | `TEXT` | ✅ | 评论原文 |
| `sentiment` | `VARCHAR(10)` | | 情绪标注：`positive` / `neutral` / `negative`，分析后回填 |
| `source` | `VARCHAR(100)` | | 评论来源（如「京东」「淘宝」） |
| `created_at` | `TIMESTAMPTZ` | ✅ | 创建时间 |

### 2.3 generation_tasks（生成记录表）⭐核心

| 列名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `id` | `SERIAL` | ✅ | 主键，自增 |
| `task_type` | `VARCHAR(20)` | ✅ | 任务类型：`copy` / `guide` / `review_analysis` / `live_script` |
| `request_input` | `JSONB` | ✅ | 原始请求参数（完整 dict） |
| `result_output` | `JSONB` | ✅ | AI 返回结果（完整 dict） |
| `ai_provider` | `VARCHAR(30)` | | 模型供应商：`deepseek` / `mock` / `openai` |
| `ai_model` | `VARCHAR(30)` | | 模型名称：`deepseek-chat` |
| `status` | `VARCHAR(10)` | ✅ | `success` / `error` / `fallback` |
| `product_id` | `INTEGER` | | 外键 → `products.id`（可空，后续关联） |
| `created_at` | `TIMESTAMPTZ` | ✅ | 创建时间 |

**`status` 取值说明**：
- `success` — AI 正常返回
- `fallback` — AI 调用失败，降级到 Mock 模板
- `error` — 请求校验失败

### 2.4 sessions（会话表）

| 列名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `id` | `SERIAL` | ✅ | 主键，自增 |
| `session_key` | `VARCHAR(64)` | ✅ | 唯一会话标识（UUID） |
| `context` | `JSONB` | | 对话上下文（多轮历史） |
| `created_at` | `TIMESTAMPTZ` | ✅ | 创建时间 |
| `expires_at` | `TIMESTAMPTZ` | | 过期时间，默认 24 小时后 |

### 2.5 recommendation_records（推荐记录表）

| 列名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `id` | `SERIAL` | ✅ | 主键，自增 |
| `task_id` | `INTEGER` | | 外键 → `generation_tasks.id` |
| `session_id` | `INTEGER` | | 外键 → `sessions.id`（可空） |
| `user_need` | `TEXT` | ✅ | 用户原始需求 |
| `budget` | `VARCHAR(50)` | | 预算范围 |
| `recommended_product` | `VARCHAR(200)` | | AI 推荐的首选商品 |
| `created_at` | `TIMESTAMPTZ` | ✅ | 创建时间 |

---

## 三、如何在代码里使用

### 3.1 写入记录

```python
from backend.database import get_db
from backend.models import GenerationTask

def save_task(task_type: str, request: dict, result: dict, provider: str, model: str, status: str):
    db = get_db()
    task = GenerationTask(
        task_type=task_type,
        request_input=request,
        result_output=result,
        ai_provider=provider,
        ai_model=model,
        status=status,
    )
    db.add(task)
    db.commit()
    return task.id
```

### 3.2 查询历史

```python
from backend.database import get_db
from backend.models import GenerationTask

db = get_db()
# 最近 20 条文案生成记录
tasks = db.query(GenerationTask) \
    .filter(GenerationTask.task_type == "copy") \
    .order_by(GenerationTask.created_at.desc()) \
    .limit(20).all()
```

### 3.3 JSONB 字段内查询

PostgreSQL 支持在 JSONB 字段内做索引查询：

```sql
-- 查所有商品名包含「键盘」的请求
SELECT * FROM generation_tasks
WHERE request_input->>'product_name' LIKE '%键盘%';

-- 查返回标题包含「舒适」的结果
SELECT * FROM generation_tasks
WHERE result_output->>'title' LIKE '%舒适%';
```

---

## 四、ER 图（关系说明）

```
products (1) ──────< (N) reviews
    │
    │  product_id (可空)
    └────────> (N) generation_tasks
                       │
                       │ task_id
                       └────────> (N) recommendation_records
                                        │
                           session_id   │
sessions (1) ──────────────────────────<┘
```

- 一个商品可以有多条评论
- 一个商品可以有多条生成记录
- 一条生成记录可以关联一个推荐记录
- 一个会话可以关联多条推荐记录