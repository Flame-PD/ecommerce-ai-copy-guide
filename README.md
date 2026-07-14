# 电商AI商品文案生成与智能导购助手

一套面向中小电商商家与普通消费者的 AI 驱动电商系统，集**商品文案生成、直播/短视频脚本生成、RAG 智能导购、评论情感分析、商家-用户在线客服、模拟购物流程**于一体。界面采用 **CVPR 论文风格的浅色系配色**（浅紫、浅蓝、浅黄），清新活泼，适合长时间操作。

> 商家可以管理商品、运营知识库、查看评论分析；用户可以浏览商品、AI 导购问答、加入购物车、下单、评价，并与商家实时沟通。

---

## 功能亮点

- **CVPR 浅色系 UI**：浅紫主色 + 浅蓝/浅黄点缀，卡片化布局、圆角、微动效，视觉更灵动。
- **AI 文案与脚本**：输入商品信息即可生成标题、卖点、详情、广告语；支持一键生成直播/短视频脚本并直接编辑。
- **RAG 智能导购**：基于知识库 + 当前已上架商品信息综合回答用户问题，告别陈旧答案。
- **用户-商家客服**：仿淘宝对话页面，用户提问、商家回复，支持未读消息提醒。
- **评论情感分析**：自动判断正面/中性/负面评价，商家可快速掌握口碑趋势。
- **订单自动处理**：未支付订单 15 分钟后自动取消；商家后台可发货、查看销量。
- **图片/视频评价**：用户评论可上传图片与视频，商品详情页以更美观的卡片展示。
- **关键字搜订单**：用户无需记住订单号，输入商品名、规格等关键字即可查找历史订单。
- **头像同步**：用户/商家上传头像后，右上角导航栏实时同步显示。
- **批量导入导出**：商品、知识库、评论均支持 Excel 模板批量操作与导出。

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.12, FastAPI, SQLAlchemy, SQLite, Uvicorn |
| 前端 | Vue 3, Vue Router, Pinia, Axios, TailwindCSS, Vite |
| AI | DeepSeek API（文案/脚本/导购/情感分析增强） |
| RAG | scikit-learn TF-IDF + 余弦相似度（本地持久化） |
| 安全 | python-jose, passlib/bcrypt |
| 文件处理 | pandas, openpyxl, python-docx |

---

## 快速开始（Windows 推荐）

### 1. 环境要求

- Python 3.12+
- Node.js LTS（含 npm）
- Git

### 2. 克隆仓库

```bash
git clone https://github.com/ddy314/ecommerce-ai-copy-guide.git
cd ecommerce-ai-copy-guide
```

### 3. 一键配置环境

在文件资源管理器中双击运行：

```
setup.bat
```

脚本会自动完成：
- 检测 Python 与 Node.js
- 创建 `backend/.venv` 虚拟环境
- 安装后端依赖 `requirements.txt`
- 安装前端依赖 `npm install`
- 复制 `backend/.env.example` 为 `backend/.env`
- 初始化数据库与默认账号、示例商品、知识库、评价

> 配置完成后，**请打开 `backend/.env`，将 `DEEPSEEK_API_KEY` 替换为您自己的 DeepSeek API Key**，否则 AI 功能无法调用。

### 4. 一键启动系统

双击运行：

```
start.bat
```

脚本会弹出两个命令行窗口：
- 后端服务：`http://127.0.0.1:8000`
- 前端页面：`http://localhost:5173`

浏览器打开 `http://localhost:5173` 即可使用。

---

## 手动环境准备（可选）

如果你不想使用一键脚本，也可以按以下步骤手动配置：

```bash
# 后端
conda create -n ecommerce-ai python=3.12 -y
conda activate ecommerce-ai
cd backend
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入 DeepSeek API Key
python scripts/init_data.py

# 前端
cd ../frontend
npm install
npm run dev
```

启动后端：

```bash
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

## 默认账号

| 角色 | 账号 | 密码 |
|------|------|------|
| 商家管理员 | `merchant` | `123456` |
| 普通用户 | `user` | `123456` |

普通用户也可以在登录页自行注册。

---

## 项目结构

```
ecommerce-ai-copy-guide/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 入口
│   │   ├── config.py            # 环境变量配置
│   │   ├── database.py          # SQLite 数据库连接
│   │   ├── models/              # SQLAlchemy 数据模型
│   │   ├── routes/              # RESTful API 路由
│   │   ├── services/            # AI / RAG / 情感分析服务
│   │   └── utils/               # 安全、ID 生成、上传目录等
│   ├── scripts/
│   │   └── init_data.py         # 初始化默认数据
│   ├── uploads/                 # 上传文件（头像、评论图片/视频等）
│   ├── requirements.txt
│   ├── .env.example
│   └── .env                     # 本地环境变量（不提交）
├── frontend/
│   ├── src/
│   │   ├── api/                 # Axios 封装
│   │   ├── components/          # 公共组件（NavBar、SideBar、ChatWidget 等）
│   │   ├── layouts/             # 用户端/商家端布局
│   │   ├── router/              # 路由配置
│   │   ├── stores/              # Pinia 状态管理
│   │   ├── assets/global.css    # CVPR 浅色主题变量
│   │   └── views/               # 页面视图
│   ├── package.json
│   └── vite.config.js
├── setup.bat                    # Windows 一键环境配置
├── start.bat                    # Windows 一键启动
├── README.md
├── 技术文档.md
└── .gitignore
```

---

## AI 客服说明

系统内置两种 AI 能力：

1. **用户端 AI 导购（ChatWidget）**
   - 入口：用户端右下角悬浮机器人。
   - 回答来源：知识库 RAG 检索 + 当前已上架商品实时信息。
   - 当用户询问价格、库存、规格等动态信息时，会优先结合数据库中的最新商品数据作答。

2. **商家-用户人工客服**
   - 入口：用户端「联系客服」页面、商家端「客服管理」页面。
   - 用户发送消息，商家在后台回复，支持会话列表、未读提醒、历史记录。
   - 真实对话流程，类似淘宝旺旺。

---

## 注意事项

- `backend/.env` 包含 DeepSeek API Key 等敏感信息，已被 `.gitignore` 排除，请勿手动提交。
- 数据库文件 `ecommerce_ai.db` 与 RAG 数据目录 `backend/rag_data/` 同样被排除在版本控制之外。
- 用户上传的头像、评论图片/视频存放于 `backend/uploads/`，已被 `.gitignore` 排除，不会提交到仓库；首次克隆后运行 `setup.bat` 会自动创建该目录。
- 支付流程为纯模拟，无真实资金交易。

---

## 许可证

MIT


架构调用链

前端 (Vue3 :5173)
    │
    ▼
后端 (FastAPI :8001)
    │
    ├── /api/ai/copy ────→ ai_client.generate_titles() ──→ AI Service :8000
    │                     ai_client.generate_description()   (优先)
    │                     ┆ 失败回退 ┆
    │                     ai_service.generate_product_copy()  (本地 DeepSeek)
    │
    ├── /api/ai/script ──→ ai_client.generate_livestream() ──→ AI Service :8000
    │
    ├── /api/chat/ask ───→ ai_client.chat() ──→ AI Service :8000 (RAG)
    │                      ┆ 失败/无结果 ┆
    │                      rag_service + ai_service (本地 TF-IDF + DeepSeek)
    │
    └── /api/chat/sync-to-ai-service ──→ ai_client.ingest() ──→ AI Service :8000
启动方式

# 终端 1 — 启动 AI Service
cd ecommerce-ai-copy-guide
uvicorn ai_service.app:app --host 0.0.0.0 --port 8000

# 终端 2 — 启动后端
cd ecommerce-ai-copy-guide
uvicorn backend.app.main:app --host 0.0.0.0 --port 8001

# 终端 3 — 启动前端
cd ecommerce-ai-copy-guide/frontend
npm run dev
关键特性
优雅降级：AI Service 不可用时，自动回退到后端原有的直接 DeepSeek 调用
零破坏：不改动后端数据库、认证、CRUD 等业务逻辑
一键同步：调用 POST /api/chat/sync-to-ai-service 将数据库商品推送到 AI Service 的 FAISS 知识库
配置开关：.env 中设 AI_SERVICE_ENABLED=false 即可完全禁用 AI Service，只用本地逻辑