# Ecommerce AI Copy Guide

电商 AI 商品文案生成与智能导购助手。当前仓库是课程项目的初始化版本，目标是先把文档、前后端骨架、Mock API 和本地验证流程搭起来，后续再接入真实模型、数据库、缓存和爬虫。

## 功能范围

- 商品文案智能生成：根据商品名称、目标人群、语气和卖点生成标题、卖点、详情页文案和广告语。
- 智能导购推荐：根据用户需求、预算和候选商品生成推荐理由与购买建议。
- 用户评论情感分析：统计评论情绪、提取关键词、沉淀差评痛点和优化建议。
- 直播 / 短视频脚本生成：按时长、语气和商品亮点生成讲解流程和互动问题。

## 当前状态

- 后端：Flask + Pydantic，已提供 deterministic Mock API，方便前端和汇报材料先行联调。
- 前端：Vue 3 + Vite，已替换默认模板，提供项目首页、功能卡片、后端状态和文案生成演示。
- 数据层：Docker Compose 已规划 PostgreSQL 与 Redis，但当前 API 暂不读写数据库和缓存。
- AI 层：当前使用模板化 Mock Service，真实供应商和提示词工程留到下一阶段。

## 目录结构

```text
.
├── backend/              # Flask API、请求模型、Mock AI service
├── docs/                 # 需求、架构、计划文档
├── frontend/             # Vue 3 + Vite 前端
├── tests/                # 后端 API 测试
├── docker-compose.yml    # PostgreSQL、Redis、后端服务编排
├── Dockerfile            # 后端容器镜像
├── pyproject.toml        # Python 工具配置
└── requirements.txt      # Python 依赖
```

## 本地启动

后端：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m flask --app backend.app run --host=0.0.0.0 --port=8000
```

前端：

```bash
cd frontend
npm install
npm run dev
```

如需修改前端 API 地址，可在 `frontend/.env.local` 中设置：

```text
VITE_API_BASE_URL=http://localhost:8000
```

基础设施：

```bash
cp .env.example .env
docker compose up postgres redis
docker compose --profile app up --build
```

## API 概览

- `GET /health`：服务状态、版本和配置摘要。
- `GET /api/capabilities`：当前能力清单与 endpoint。
- `POST /api/copy/generate`：生成商品标题、卖点、详情文案和广告语。
- `POST /api/guide/recommend`：生成导购推荐理由和备选建议。
- `POST /api/reviews/analyze`：分析评论情绪、关键词和痛点。
- `POST /api/scripts/live`：生成直播讲解流程和互动问题。

## 验证命令

```bash
python -m pytest -q
python -m flask --app backend.app routes
cd frontend && npm run build
```

## 小组分工建议

- 后端与接口：Flask API、Pydantic schema、数据库模型、Redis 缓存。
- AI 模块：提示词模板、模型供应商接入、情感分析策略、结果质量评估。
- 数据与爬虫：商品样本、评论样本、数据清洗和演示数据集。
- 前端展示：H5 导购页、运营后台、接口状态与结果可视化。
- 文档与汇报：需求说明、架构图、里程碑、PowerBI 或可视化展示材料。
