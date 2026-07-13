import re
from typing import List, Dict
from snownlp import SnowNLP


_POSITIVE_WORDS = {"好", "不错", "满意", "喜欢", "推荐", "值得", "棒", "优秀", "舒服", "漂亮", "好看", "好用", "超值", "惊喜"}
_NEGATIVE_WORDS = {"差", "失望", "垃圾", "糟糕", "破", "烂", "坑", "不值", "后悔", "难闻", "不舒服", "不紧", "松", "假"}


def analyze(text: str) -> str:
    if not text:
        return "neutral"
    s = SnowNLP(text)
    score = s.sentiments
    # 规则修正
    has_pos = any(w in text for w in _POSITIVE_WORDS)
    has_neg = any(w in text for w in _NEGATIVE_WORDS)
    if has_neg:
        return "negative"
    if has_pos or score > 0.6:
        return "positive"
    if score < 0.4:
        return "negative"
    return "neutral"


def extract_keywords(texts: List[str], sentiment: str) -> List[str]:
    words: Dict[str, int] = {}
    stop = {"的", "了", "是", "我", "很", "非常", "真的", "这个", "一个", "感觉", "就是", "有点", "没有", "不会", "可以", "但是"}
    for text in texts:
        if not text:
            continue
        s = SnowNLP(text)
        for w in s.words:
            w = w.strip()
            if len(w) < 2 or w in stop or re.match(r"[0-9a-zA-Z\s]+", w):
                continue
            words[w] = words.get(w, 0) + 1
    return [w for w, c in sorted(words.items(), key=lambda x: -x[1])[:10]]


def batch_analyze(reviews: List[dict]) -> dict:
    for r in reviews:
        r["sentiment"] = analyze(r.get("content", ""))
    positive = [r for r in reviews if r["sentiment"] == "positive"]
    neutral = [r for r in reviews if r["sentiment"] == "neutral"]
    negative = [r for r in reviews if r["sentiment"] == "negative"]
    ratings = [r.get("rating", 5) for r in reviews]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0.0
    return {
        "positive": len(positive),
        "neutral": len(neutral),
        "negative": len(negative),
        "avg_rating": round(avg_rating, 2),
        "positive_keywords": extract_keywords([r["content"] for r in positive], "positive"),
        "negative_keywords": extract_keywords([r["content"] for r in negative], "negative"),
    }
