#!/usr/bin/env python3
"""
每日技术推送 — 搜索 GitHub 开源项目 + Python 知识点，推送到飞书群机器人
触发：GitHub Actions 定时执行，或手动运行
"""

import json
import os
import random
import ssl
import time
import hmac
import hashlib
import base64
import urllib.request
from datetime import datetime, timezone, timedelta


# ========== 配置 ==========

FEISHU_WEBHOOK = os.environ.get("FEISHU_WEBHOOK", "")
FEISHU_SECRET = os.environ.get("FEISHU_SECRET", "")

CATEGORIES = [
    {"name": "📹 免费视频/屏幕工具", "query": "video+screen+record+tool+free"},
    {"name": "🤖 AI 实用工具", "query": "AI+tool+awesome+2026"},
    {"name": "✍️ 英语学习/写作工具", "query": "english+writing+translation+tool"},
    {"name": "🛠 开发者效率工具", "query": "developer+productivity+tool"},
]

# ========== Python 知识卡片库 ==========

PYTHON_TIPS = [
    {
        "title": "zip() 的隐藏陷阱：静默截断",
        "code": '''users = ["Alice", "Bob", "Charlie"]
scores = [85, 92]

# ❌ zip() 以最短的为准，Charlie 被静默丢弃！
for u, s in zip(users, scores):
    print(f"{u}: {s}")  # Alice, Bob — Charlie 没了

# ✅ 用 zip_longest 暴露不匹配
from itertools import zip_longest
for u, s in zip_longest(users, scores, fillvalue=None):
    if s is None:
        print(f"⚠️ {u} 缺少成绩！")''',
        "takeaway": "处理 CSV 列、API 返回值时，zip() 不会报错，只会截断。用 zip_longest 保平安。",
    },
    {
        "title": "列表的「+=」和「= x + y」不一样",
        "code": '''a = [1, 2, 3]
b = a
a = a + [4]     # 创建新列表，a 指向新对象
print(b)        # [1, 2, 3] ← b 没变

a = [1, 2, 3]
b = a
a += [4]        # extend，原地修改！
print(b)        # [1, 2, 3, 4] ← b 也变了！''',
        "takeaway": "+= 是原地修改（__iadd__），= x + y 创建新对象。函数传参时尤其小心。",
    },
    {
        "title": "默认参数只计算一次",
        "code": '''# ❌ 默认参数在函数定义时计算，不是每次调用时
def add_item(item, lst=[]):
    lst.append(item)
    return lst

print(add_item(1))  # [1]
print(add_item(2))  # [1, 2] ← 同一个列表！
print(add_item(3))  # [1, 2, 3]

# ✅ 正确做法
def add_item(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst''',
        "takeaway": "可变默认参数是 Python 面试第一坑。永远用 None 做默认值，函数体内再初始化。",
    },
    {
        "title": "f-string 里的表达式和调试技巧",
        "code": '''name = "Alice"
score = 95.6789

# 基本用法
print(f"{name} 考了 {score}")          # Alice 考了 95.6789

# 格式化
print(f"{name} 考了 {score:.1f}")      # Alice 考了 95.7

# Python 3.8+ 调试语法：{var=}
print(f"{name=}")                       # name='Alice'
print(f"{score=:.2f}")                  # score=95.68

# 表达式
print(f"2+3={2+3}")                     # 2+3=5''',
        "takeaway": "f-string 比 % 和 .format() 快且可读。{var=} 是 Python 3.8 调试神器。",
    },
    {
        "title": "try/except/else/finally 的执行顺序",
        "code": '''def demo():
    try:
        print("1. try")
        return "try 返回"
    except:
        print("2. except")
    else:
        print("3. else（没异常才执行）")
    finally:
        print("4. finally（无论如何都执行）")

result = demo()
print(f"结果: {result}")
# 输出：
# 1. try
# 4. finally（finally 在 return 之前执行！）
# 结果: try 返回''',
        "takeaway": "finally 总在 return 之前执行。else 只在没异常时执行（很多人不知道 else 的存在）。",
    },
    {
        "title": "is 和 == 的区别：99% 的新手都踩过",
        "code": '''a = [1, 2, 3]
b = [1, 2, 3]

print(a == b)   # True  ← 值相等
print(a is b)   # False ← 不是同一个对象

# 小整数缓存（-5 到 256）是特例
x = 256
y = 256
print(x is y)   # True  ← 缓存了

x = 257
y = 257
print(x is y)   # False ← 没缓存！''',
        "takeaway": "== 比值，is 比身份。只有和 None 比较时用 is（if x is None），其余用 ==。",
    },
    {
        "title": "列表推导式 vs 生成器表达式：内存天差地别",
        "code": '''import sys

# 列表推导式：一次性生成所有数据到内存
nums_list = [i * 2 for i in range(1_000_000)]
print(sys.getsizeof(nums_list))  # ~8MB

# 生成器表达式：懒加载，逐个产出
nums_gen = (i * 2 for i in range(1_000_000))
print(sys.getsizeof(nums_gen))   # ~200 bytes！

# 用 sum() 消费生成器
print(sum(nums_gen))  # 计算过程中内存只占 200 bytes''',
        "takeaway": "方括号 [] 是列表（占内存），圆括号 () 是生成器（省内存）。大数据量时优先用生成器。",
    },
    {
        "title": "dict.get() 一行搞定「取值 + 默认值」",
        "code": '''config = {"host": "localhost", "port": 8080}

# ❌ 啰嗦写法
timeout = config["timeout"] if "timeout" in config else 30

# ✅ Pythonic 写法
timeout = config.get("timeout", 30)

# 嵌套取值也不怕
user = {"profile": {"name": "Alice"}}
city = user.get("profile", {}).get("city", "未知")
print(city)  # 未知（不会抛 KeyError）''',
        "takeaway": "从不存在的 key 取值用 .get() 而不是 []，避免 KeyError 崩溃。",
    },
    {
        "title": "enumerate()：遍历时同时拿索引和值",
        "code": '''items = ["苹果", "香蕉", "橙子"]

# ❌ 新手写法
for i in range(len(items)):
    print(f"{i+1}. {items[i]}")

# ✅ Pythonic 写法
for i, item in enumerate(items, start=1):
    print(f"{i}. {item}")

# 输出：
# 1. 苹果
# 2. 香蕉
# 3. 橙子''',
        "takeaway": "需要索引时用 enumerate()，不要用 range(len())。start 参数可以自定义起始值。",
    },
    {
        "title": "浅拷贝 vs 深拷贝：嵌套对象的地雷",
        "code": '''import copy

original = [[1, 2], [3, 4]]

# 浅拷贝：外层新对象，内层还是引用
shallow = original.copy()   # 或 list(original)，或 original[:]
shallow[0][0] = 99
print(original[0])  # [99, 2] ← 原对象内层也被改了！

# 深拷贝：完全独立
original = [[1, 2], [3, 4]]
deep = copy.deepcopy(original)
deep[0][0] = 99
print(original[0])  # [1, 2] ← 不受影响''',
        "takeaway": ".copy() / list() / [:] 都是浅拷贝。嵌套结构要独立，用 copy.deepcopy()。",
    },
]


# ========== 搜索 GitHub ==========

def search_github(query, per_page=3):
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    url = (
        f"https://api.github.com/search/repositories"
        f"?q={query}+pushed:>{week_ago}"
        f"&sort=stars&order=desc&per_page={per_page}"
    )
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(url, headers={
        "User-Agent": "DailyDigest/1.0",
        "Accept": "application/vnd.github.v3+json",
    })
    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e:
        print(f"  ⚠️ GitHub API 失败: {e}")
        return []

    results = []
    for item in data.get("items", [])[:per_page]:
        results.append({
            "name": item["full_name"],
            "url": item["html_url"],
            "stars": item["stargazers_count"],
            "desc": (item.get("description") or "无描述")[:150],
            "lang": item.get("language") or "N/A",
        })
    return results


# ========== 格式化飞书消息 ==========

def build_feishu_card(categories_data, python_tip):
    today = datetime.now(timezone.utc)
    beijing = today + timedelta(hours=8)
    date_str = beijing.strftime("%Y-%m-%d")

    elements = []
    for cat in CATEGORIES:
        items = categories_data.get(cat["name"], [])
        if not items:
            continue
        lines = [f"**{cat['name']}**\n"]
        for i, item in enumerate(items, 1):
            stars = f"⭐ {item['stars']:,}"
            lines.append(
                f"{i}. [{item['name']}]({item['url']})  {stars}\n"
                f"   {item['desc']}\n"
            )
        elements.append({"tag": "markdown", "content": "".join(lines)})
        elements.append({"tag": "hr"})

    tip = python_tip
    tip_text = (
        f"**🐍 Python 今日知识点：{tip['title']}**\n\n"
        f"```python\n{tip['code']}\n```\n\n"
        f"💡 {tip['takeaway']}"
    )
    elements.append({"tag": "markdown", "content": tip_text})

    return {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"🔥 每日技术推送 | {date_str}",
                },
                "template": "blue",
            },
            "elements": elements,
            "config": {"wide_screen_mode": True},
        },
    }


# ========== 发送到飞书 ==========

def send_to_feishu(webhook_url, card, secret=""):
    if not webhook_url:
        print("⚠️ 未设置 FEISHU_WEBHOOK，跳过发送")
        print(json.dumps(card, ensure_ascii=False, indent=2))
        return False

    url = webhook_url
    if secret:
        ts = str(int(time.time()))
        sign_string = f"{ts}\n{secret}"
        hmac_code = hmac.new(
            secret.encode("utf-8"),
            sign_string.encode("utf-8"),
            digestmod=hashlib.sha256,
        )
        signature = base64.b64encode(hmac_code.digest()).decode("utf-8")
        url = f"{webhook_url}?timestamp={ts}&sign={signature}"

    data = json.dumps(card, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            result = json.loads(resp.read().decode())
            if result.get("code") == 0:
                print("✅ 飞书推送成功")
                return True
            else:
                print(f"❌ 飞书返回错误: {result}")
                return False
    except Exception as e:
        print(f"❌ 飞书请求失败: {e}")
        return False


# ========== 主流程 ==========

def main():
    print("=" * 50)
    print("  每日技术推送 — 开始")
    print("=" * 50)

    categories_data = {}
    for cat in CATEGORIES:
        print(f"\n🔍 搜索: {cat['name']} ...")
        items = search_github(cat["query"])
        categories_data[cat["name"]] = items
        print(f"   找到 {len(items)} 个项目")
        for item in items:
            print(f"   - {item['name']} ⭐{item['stars']}")

    tip = random.choice(PYTHON_TIPS)
    print(f"\n🐍 今日 Python 知识点: {tip['title']}")

    card = build_feishu_card(categories_data, tip)
    print(f"\n📤 发送到飞书...")
    success = send_to_feishu(FEISHU_WEBHOOK, card, FEISHU_SECRET)

    if success:
        print("\n✅ 全部完成！")
    else:
        print("\n⚠️ 发送未完成（可能缺少 Webhook 配置）")
    print("=" * 50)


if __name__ == "__main__":
    main()