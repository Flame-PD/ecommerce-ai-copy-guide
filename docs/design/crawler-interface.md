# 爬虫数据入库接口文档

> 写给爬虫程序的对接说明。本文档定义爬虫输出的数据格式和后端接收接口。

---

## 一、商品数据导入

### 接口

```
POST /api/products/import
Content-Type: multipart/form-data
认证: 需要商家 token（Header: Authorization: Bearer <token>）
```

### 支持格式

`.xlsx` 或 `.json`

### Excel 模板（推荐）

| 列名 | 必填 | 类型 | 示例 |
|---|---|---|---|
| name | ✅ | 文本 | 云感护腰办公椅 |
| category | | 文本 | 办公家具 |
| description | | 文本 | 人体工学设计，久坐不累 |
| price | | 数字 | 299.00 |
| stock | | 整数 | 100 |
| status | | `on` / `off` | on |
| specs | | 逗号分隔 | 黑色,白色,灰色 |
| images | | 逗号分隔 URL | https://img.example.com/1.jpg,https://... |
| video_url | | URL | https://video.example.com/demo.mp4 |

### JSON 格式（备选）

```json
[
  {
    "name": "云感护腰办公椅",
    "category": "办公家具",
    "description": "人体工学设计，久坐不累",
    "price": 299.0,
    "stock": 100,
    "status": "on",
    "specs": "黑色,白色,灰色",
    "images": "https://img.example.com/1.jpg,https://img.example.com/2.jpg",
    "video_url": ""
  }
]
```

### 返回示例

```json
{"ok": true, "count": 15}
```

### 后端处理逻辑

1. 读取文件，按扩展名选择解析器（pandas.read_excel 或 json.loads）
2. 逐行校验必填字段
3. specs 和 images 从逗号分隔字符串转为数组
4. 逐条 `db.add(Product(...))` + `db.commit()`
5. 每件商品自动分配 display_id（格式：P + 年月日 + 序号）

---

## 二、评论数据导入

### 接口

```
POST /api/reviews/import
Content-Type: multipart/form-data
认证: 需要商家 token
```

### 支持格式

`.xlsx` / `.xls`

### Excel 模板

| 列名 | 必填 | 类型 | 示例 |
|---|---|---|---|
| product_name | ✅ | 文本 | 云感护腰办公椅 |
| rating | | 整数 1-5 | 5 |
| content | ✅ | 文本 | 坐着很舒服，腰部支撑很好 |

### 重要说明

- `product_name` 必须和商品表中已有商品名称**完全一致**（精确匹配）
- 匹配不到的商品名，该行评论会被**静默跳过**
- sentiment（好评/中评/差评）由后端自动分析标注，**不需要爬虫提供**
- 导入的评论 `source` 字段统一标记为 `"merchant"`

### 返回示例

```json
{"ok": true, "count": 42}
```

### 后端处理逻辑

1. pandas 读取 Excel
2. 按 `product_name` 查询商品表找到 `product_id`（找不到就跳过）
3. 每条评论调 `sentiment_service.analyze(content)` 自动标注情感
4. 批量写入 Review 表（user_id 使用导入者身份）
5. 一次 commit

---

## 三、情感分析接口（不上传文件，直接分析）

### 接口

```
POST /api/reviews/analyze
Content-Type: multipart/form-data
认证: 需要商家 token
```

### 支持格式

`.txt` / `.md` / `.xlsx` / `.docx`

- txt/md: 每行一条评论
- xlsx: 读取 `content` 列（或第一列）
- docx: 每段一条评论

### 参数

| 参数 | 必填 | 说明 |
|---|---|---|
| file | ✅ | 上传文件 |
| product_id | | 如果提供，分析结果同时存入该商品的评论表 |

### 返回示例

```json
{
  "ok": true,
  "count": 50,
  "stats": {
    "positive": 32,
    "neutral": 10,
    "negative": 8,
    "avg_rating": 4.2,
    "positive_keywords": ["舒服", "好用", "推荐"],
    "negative_keywords": ["贵", "慢", "异味"]
  }
}
```

---

## 四、对接 Checklist

请爬虫同学确认以下事项：

- [ ] 商品数据能否输出为上述 Excel 格式？
- [ ] 评论中能否包含 `product_name` 列用于关联商品？
- [ ] 如果某件商品爬不到评论，如何处理（空着 / 标记 / 跳过）？
- [ ] 数据量预估？（影响是否需要分批导入）
- [ ] 是否需要后端提供 token 用于脚本直接调 API？

---

## 五、测试方式

爬虫同学可以用 curl 测试接口连通性：

```bash
# 登录获取 token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456","role":"merchant"}'

# 导入评论（用拿到的 token 替换 <TOKEN>）
curl -X POST http://localhost:8000/api/reviews/import \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@reviews.xlsx"
```
