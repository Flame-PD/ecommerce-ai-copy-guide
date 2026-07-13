# 电商AI商品文案生成与智能导购助手

基于《系统设计构想》实现的一套电商AI系统，面向中小电商商家与普通消费者，提供AI文案生成、RAG智能导购、评论情感分析、直播脚本生成、商品管理与模拟购物流程。

## 功能概览

- **统一登录**：一个登录入口，根据身份自动分流到商家后台或用户前台。
- **商家后台**
  - 商品信息管理（新增、编辑、上下架、库存、批量导入导出）
  - AI 商品文案生成（标题、卖点、详情、广告语）
  - AI 直播/短视频脚本生成
  - RAG 知识库管理
  - 用户评论情感分析与统计
  - 订单管理与发货
- **用户前台**
  - 商品浏览、搜索、分类筛选
  - AI 智能导购问答
  - 加入购物车、模拟下单、模拟支付
  - 订单查看与评价
  - 个人中心（收藏、浏览记录、地址、问答历史）

## 技术栈

- **后端**：Python 3.12, FastAPI, SQLAlchemy, SQLite, python-jose, passlib, OpenAI SDK, scikit-learn, SnowNLP
- **前端**：Vue 3, Vue Router, Pinia, Axios, TailwindCSS, Vite
- **AI**：DeepSeek API（文案/脚本/导购增强）
- **RAG**：scikit-learn TF-IDF + 余弦相似度（本地持久化）

## 环境准备

1. 克隆仓库：
   ```bash
   git clone https://github.com/ddy314/ecommerce-ai-copy-guide.git
   cd ecommerce-ai-copy-guide
   ```

2. 创建并激活 Conda 环境（推荐）：
   ```bash
   conda create -n ecommerce-ai python=3.12 -y
   conda activate ecommerce-ai
   ```

3. 后端依赖：
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. 前端依赖：
   ```bash
   cd ../frontend
   npm install
   ```

5. 配置环境变量：
   ```bash
   cd ../backend
   cp .env.example .env
   # 编辑 .env，填入你的 DeepSeek API Key
   ```

6. 初始化数据（创建默认账号与示例商品）：
   ```bash
   python scripts/init_data.py
   ```

## 启动方式

1. 启动后端（在 `backend` 目录下）：
   ```bash
   uvicorn app.main:app --reload
   ```
   后端默认运行在 `http://127.0.0.1:8000`，API 文档见 `http://127.0.0.1:8000/docs`。

2. 启动前端（在 `frontend` 目录下）：
   ```bash
   npm run dev
   ```
   前端默认运行在 `http://localhost:5173`。

3. 浏览器访问 `http://localhost:5173`。

## 默认账号

- **商家管理员**：`merchant` / `merchant123`
- **普通用户**：`user` / `user123`

普通用户也可以在登录页自行注册。

## 项目结构

```
ecommerce-ai-copy-guide/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI 入口
│   │   ├── config.py         # 配置读取
│   │   ├── database.py       # 数据库连接
│   │   ├── models/           # SQLAlchemy 数据模型
│   │   ├── routes/           # API 路由
│   │   ├── services/         # AI / RAG / 情感分析服务
│   │   └── utils/            # 安全与工具
│   ├── scripts/
│   │   └── init_data.py      # 数据初始化脚本
│   ├── requirements.txt
│   └── .env                  # 本地环境变量（不提交）
├── frontend/
│   ├── src/
│   │   ├── api/              # Axios 封装
│   │   ├── components/       # 公共组件
│   │   ├── layouts/          # 布局组件
│   │   ├── router/           # 路由配置
│   │   ├── stores/           # Pinia 状态管理
│   │   └── views/            # 页面视图
│   ├── package.json
│   └── vite.config.js
├── .gitignore
└── README.md
```

## 注意事项

- `backend/.env` 包含 DeepSeek API Key 等敏感信息，默认已被 `.gitignore` 排除，请勿手动提交。
- 数据库文件 `ecommerce_ai.db` 与 RAG 数据目录 `backend/rag_data/` 同样被排除在版本控制之外。
- 支付流程为纯模拟，无真实资金交易。

## 许可证

MIT
