import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.product import Product
from app.models.knowledge import KnowledgeItem
from app.models.review import Review
from app.utils.security import get_password_hash
from app.services import rag_service


def init():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # 创建商家账号
        if not db.query(User).filter(User.username == "merchant").first():
            merchant = User(
                username="merchant",
                password_hash=get_password_hash("merchant123"),
                nickname="商家管理员",
                role="merchant",
            )
            db.add(merchant)
            db.commit()
            print("商家账号已创建: merchant / merchant123")
        else:
            print("商家账号已存在")

        # 创建普通用户
        if not db.query(User).filter(User.username == "user").first():
            user = User(
                username="user",
                password_hash=get_password_hash("user123"),
                nickname="测试用户",
                role="user",
            )
            db.add(user)
            db.commit()
            print("普通用户已创建: user / user123")
        else:
            print("普通用户已存在")

        merchant = db.query(User).filter(User.username == "merchant").first()
        user = db.query(User).filter(User.username == "user").first()

        # 示例商品
        products_data = [
            {
                "name": "超声波电动牙刷 Pro",
                "category": "个护健康",
                "description": "31000次/分钟高频声波震动，智能压力感应，30天超长续航，IPX7级防水。",
                "price": 199.0,
                "stock": 500,
                "status": "on",
                "specs": ["珍珠白", "曜石黑", "樱花粉"],
                "image_url": "https://images.unsplash.com/photo-1559671088-795c5c1555a1?auto=format&fit=crop&w=600&q=80",
            },
            {
                "name": "智能降噪蓝牙耳机",
                "category": "数码影音",
                "description": "ANC主动降噪，40小时复合续航，蓝牙5.3低延迟，高清通话降噪。",
                "price": 349.0,
                "stock": 300,
                "status": "on",
                "specs": ["云岩白", "午夜黑", "薄荷绿"],
                "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=600&q=80",
            },
            {
                "name": "便携式挂脖风扇",
                "category": "生活电器",
                "description": "无叶设计安全不夹发，三档风力可调，Type-C快充，静音电机。",
                "price": 79.0,
                "stock": 800,
                "status": "on",
                "specs": ["清新蓝", "活力橙","简约白"],
                "image_url": "https://images.unsplash.com/photo-1617112848923-ccef2e6cf092?auto=format&fit=crop&w=600&q=80",
            },
            {
                "name": "纯棉亲肤四件套",
                "category": "家居家纺",
                "description": "100%新疆长绒棉，60支高密织造，亲肤透气，活性印染不易褪色。",
                "price": 289.0,
                "stock": 200,
                "status": "on",
                "specs": ["1.5m床", "1.8m床", "2.0m床"],
                "image_url": "https://images.unsplash.com/photo-1631679706909-1844bbd07221?auto=format&fit=crop&w=600&q=80",
            },
            {
                "name": "待上架新品-智能保温杯",
                "category": "生活电器",
                "description": "OLED水温显示，24小时长效保温，316不锈钢内胆。",
                "price": 129.0,
                "stock": 100,
                "status": "off",
                "specs": ["典雅黑", "象牙白"],
                "image_url": "https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?auto=format&fit=crop&w=600&q=80",
            },
        ]

        created_products = []
        for p in products_data:
            existing = db.query(Product).filter(Product.name == p["name"]).first()
            if existing:
                print(f"商品已存在: {p['name']}")
                created_products.append(existing)
                continue
            product = Product(**p)
            db.add(product)
            db.commit()
            db.refresh(product)
            created_products.append(product)
            print(f"商品已创建: {p['name']}")

        # 知识库条目
        knowledge_data = [
            # 电动牙刷
            {"product_id": None, "category": "common", "question": "你们的电动牙刷续航多久？", "answer": "超声波电动牙刷 Pro 内置大容量锂电池，充满一次可使用约30天，出差旅行无需带充电器。"},
            {"product_id": None, "category": "common", "question": "电动牙刷防水吗？", "answer": "整机支持 IPX7 级防水，可全身水洗，淋浴时也可放心使用。"},
            {"product_id": None, "category": "size", "question": "电动牙刷有几种颜色？", "answer": "提供珍珠白、曜石黑、樱花粉三种配色，满足不同风格需求。"},
            # 蓝牙耳机
            {"product_id": None, "category": "common", "question": "耳机降噪效果怎么样？", "answer": "采用 ANC 主动降噪技术，可有效过滤地铁、飞机等环境噪音，同时支持通透模式。"},
            {"product_id": None, "category": "common", "question": "蓝牙耳机续航多久？", "answer": "耳机单次续航约8小时，配合充电仓总续航可达40小时，支持快充。"},
            # 挂脖风扇
            {"product_id": None, "category": "common", "question": "挂脖风扇会夹头发吗？", "answer": "采用无叶涡轮设计，长发女生也能放心使用，安全不夹发。"},
            {"product_id": None, "category": "common", "question": "风扇噪音大吗？", "answer": "搭载静音无刷电机，最低档位噪音低于25分贝，图书馆使用也不打扰他人。"},
            # 四件套
            {"product_id": None, "category": "material", "question": "四件套是什么材质？", "answer": "选用100%新疆长绒棉，60支高密织造，触感柔软亲肤，透气性佳。"},
            {"product_id": None, "category": "aftersale", "question": "四件套支持退换吗？", "answer": "支持7天无理由退换，未下水、未使用、包装完好即可申请。"},
        ]

        # 按商品名称匹配 product_id
        name_to_product = {p.name: p for p in created_products}
        mapping = {
            "电动牙刷": "超声波电动牙刷 Pro",
            "牙刷": "超声波电动牙刷 Pro",
            "耳机": "智能降噪蓝牙耳机",
            "风扇": "便携式挂脖风扇",
            "四件套": "纯棉亲肤四件套",
        }

        for item in knowledge_data:
            q = item["question"]
            product_name = None
            for keyword, pname in mapping.items():
                if keyword in q:
                    product_name = pname
                    break
            if product_name and product_name in name_to_product:
                item["product_id"] = name_to_product[product_name].id

            existing = db.query(KnowledgeItem).filter(
                KnowledgeItem.question == item["question"],
                KnowledgeItem.product_id == item["product_id"],
            ).first()
            if existing:
                print(f"知识条目已存在: {item['question']}")
                continue
            ki = KnowledgeItem(**item)
            db.add(ki)
            db.commit()
            db.refresh(ki)
            text = f"问题：{ki.question}\n回答：{ki.answer}"
            eid = rag_service.add_knowledge(text, {
                "product_id": ki.product_id,
                "question": ki.question,
                "category": ki.category,
            })
            ki.embedding_id = eid
            db.commit()
            print(f"知识条目已创建: {ki.question}")

        # 同步商品基础信息到 RAG
        for p in created_products:
            items = db.query(KnowledgeItem).filter(KnowledgeItem.product_id == p.id).all()
            data = {
                "id": p.id,
                "name": p.name,
                "category": p.category,
                "description": p.description,
                "price": p.price,
                "specs": p.specs or [],
                "knowledge_items": [{"question": i.question, "answer": i.answer} for i in items],
            }
            pairs = rag_service.sync_product_knowledge(data)
            for text, meta in pairs:
                rag_service.add_knowledge(text, meta)
            print(f"商品信息已同步到 RAG: {p.name}")

        # 模拟评价
        reviews_data = [
            {"product_name": "超声波电动牙刷 Pro", "rating": 5, "content": "刷得很干净，续航也很给力，出差一周都没充电！", "sentiment": "positive"},
            {"product_name": "超声波电动牙刷 Pro", "rating": 4, "content": "整体不错，就是声音稍微有点大，可以接受。", "sentiment": "neutral"},
            {"product_name": "智能降噪蓝牙耳机", "rating": 5, "content": "降噪效果惊艳，地铁上完全听不到噪音，音质也很好。", "sentiment": "positive"},
            {"product_name": "智能降噪蓝牙耳机", "rating": 2, "content": "戴久了耳朵疼，通话时对方说声音小。", "sentiment": "negative"},
            {"product_name": "便携式挂脖风扇", "rating": 5, "content": "夏天通勤神器，风力够大而且不夹头发，推荐！", "sentiment": "positive"},
            {"product_name": "便携式挂脖风扇", "rating": 3, "content": "风量一般，最大档声音有点大。", "sentiment": "neutral"},
            {"product_name": "纯棉亲肤四件套", "rating": 5, "content": "面料很舒服，颜色也没有色差，会回购。", "sentiment": "positive"},
            {"product_name": "纯棉亲肤四件套", "rating": 1, "content": "洗了一次就起球了，质量没想象中好。", "sentiment": "negative"},
        ]

        for r in reviews_data:
            product = name_to_product.get(r["product_name"])
            if not product:
                continue
            existing = db.query(Review).filter(
                Review.user_id == user.id,
                Review.product_id == product.id,
                Review.content == r["content"],
            ).first()
            if existing:
                print(f"评价已存在: {r['content'][:20]}...")
                continue
            review = Review(
                user_id=user.id,
                product_id=product.id,
                order_id=None,
                rating=r["rating"],
                content=r["content"],
                sentiment=r["sentiment"],
            )
            db.add(review)
            db.commit()
            print(f"评价已创建: {r['content'][:20]}...")

        print("\n数据初始化完成！")
        print("商家账号: merchant / merchant123")
        print("普通用户: user / user123")
    finally:
        db.close()


if __name__ == "__main__":
    init()
