     1|#!/usr/bin/env python3
     2|"""
     3|每日技术推送 — 搜索 GitHub 开源项目 + Python 知识点，推送到飞书群机器人
     4|触发：GitHub Actions 定时执行，或手动运行
     5|"""
     6|
     7|import json
     8|import os
     9|import random
    10|import ssl
    11|import time
    12|import hmac
    13|import hashlib
    14|import base64
    15|import urllib.request
    16|from datetime import datetime, timezone, timedelta
    17|
    18|
    19|# ========== 配置 ==========
    20|
    21|FEISHU_WEBHOOK = os.environ.get("FEISHU_WEBHOOK", "")
    22|FEISHU_SECRET = os.environ.get("FEISHU_SECRET", "")
    23|
    24|CATEGORIES = [
    25|    {"name": "📹 免费视频/屏幕工具", "query": "video+screen+record+tool+free"},
    26|    {"name": "🤖 AI 实用工具", "query": "AI+tool+awesome+2026"},
    27|    {"name": "✍️ 英语学习/写作工具", "query": "english+writing+translation+tool"},
    28|    {"name": "🛠 开发者效率工具", "query": "developer+productivity+tool"},
    29|]
    30|
    31|# ========== Python 知识卡片库 ==========
    32|
    33|PYTHON_TIPS = [
    34|    {
    35|        "title": "zip() 的隐藏陷阱：静默截断",
    36|        "code": '''users = ["Alice", "Bob", "Charlie"]
    37|scores = [85, 92]
    38|
    39|# ❌ zip() 以最短的为准，Charlie 被静默丢弃！
    40|for u, s in zip(users, scores):
    41|    print(f"{u}: {s}")  # Alice, Bob — Charlie 没了
    42|
    43|# ✅ 用 zip_longest 暴露不匹配
    44|from itertools import zip_longest
    45|for u, s in zip_longest(users, scores, fillvalue=None):
    46|    if s is None:
    47|        print(f"⚠️ {u} 缺少成绩！")''',
    48|        "takeaway": "处理 CSV 列、API 返回值时，zip() 不会报错，只会截断。用 zip_longest 保平安。",
    49|    },
    50|    {
    51|        "title": "列表的「+=」和「= x + y」不一样",
    52|        "code": '''a = [1, 2, 3]
    53|b = a
    54|a = a + [4]     # 创建新列表，a 指向新对象
    55|print(b)        # [1, 2, 3] ← b 没变
    56|
    57|a = [1, 2, 3]
    58|b = a
    59|a += [4]        # extend，原地修改！
    60|print(b)        # [1, 2, 3, 4] ← b 也变了！''',
    61|        "takeaway": "+= 是原地修改（__iadd__），= x + y 创建新对象。函数传参时尤其小心。",
    62|    },
    63|    {
    64|        "title": "默认参数只计算一次",
    65|        "code": '''# ❌ 默认参数在函数定义时计算，不是每次调用时
    66|def add_item(item, lst=[]):
    67|    lst.append(item)
    68|    return lst
    69|
    70|print(add_item(1))  # [1]
    71|print(add_item(2))  # [1, 2] ← 同一个列表！
    72|print(add_item(3))  # [1, 2, 3]
    73|
    74|# ✅ 正确做法
    75|def add_item(item, lst=None):
    76|    if lst is None:
    77|        lst = []
    78|    lst.append(item)
    79|    return lst''',
    80|        "takeaway": "可变默认参数是 Python 面试第一坑。永远用 None 做默认值，函数体内再初始化。",
    81|    },
    82|    {
    83|        "title": "f-string 里的表达式和调试技巧",
    84|        "code": '''name = "Alice"
    85|score = 95.6789
    86|
    87|# 基本用法
    88|print(f"{name} 考了 {score}")          # Alice 考了 95.6789
    89|
    90|# 格式化
    91|print(f"{name} 考了 {score:.1f}")      # Alice 考了 95.7
    92|
    93|# Python 3.8+ 调试语法：{var=}
    94|print(f"{name=}")                       # name='Alice'
    95|print(f"{score=:.2f}")                  # score=95.68
    96|
    97|# 表达式
    98|print(f"2+3={2+3}")                     # 2+3=5''',
    99|        "takeaway": "f-string 比 % 和 .format() 快且可读。{var=} 是 Python 3.8 调试神器。",
   100|    },
   101|    {
   102|        "title": "try/except/else/finally 的执行顺序",
   103|        "code": '''def demo():
   104|    try:
   105|        print("1. try")
   106|        return "try 返回"
   107|    except:
   108|        print("2. except")
   109|    else:
   110|        print("3. else（没异常才执行）")
   111|    finally:
   112|        print("4. finally（无论如何都执行）")
   113|
   114|result = demo()
   115|print(f"结果: {result}")
   116|# 输出：
   117|# 1. try
   118|# 4. finally（finally 在 return 之前执行！）
   119|# 结果: try 返回''',
   120|        "takeaway": "finally 总在 return 之前执行。else 只在没异常时执行（很多人不知道 else 的存在）。",
   121|    },
   122|    {
   123|        "title": "is 和 == 的区别：99% 的新手都踩过",
   124|        "code": '''a = [1, 2, 3]
   125|b = [1, 2, 3]
   126|
   127|print(a == b)   # True  ← 值相等
   128|print(a is b)   # False ← 不是同一个对象
   129|
   130|# 小整数缓存（-5 到 256）是特例
   131|x = 256
   132|y = 256
   133|print(x is y)   # True  ← 缓存了
   134|
   135|x = 257
   136|y = 257
   137|print(x is y)   # False ← 没缓存！''',
   138|        "takeaway": "== 比值，is 比身份。只有和 None 比较时用 is（if x is None），其余用 ==。",
   139|    },
   140|    {
   141|        "title": "列表推导式 vs 生成器表达式：内存天差地别",
   142|        "code": '''import sys
   143|
   144|# 列表推导式：一次性生成所有数据到内存
   145|nums_list = [i * 2 for i in range(1_000_000)]
   146|print(sys.getsizeof(nums_list))  # ~8MB
   147|
   148|# 生成器表达式：懒加载，逐个产出
   149|nums_gen = (i * 2 for i in range(1_000_000))
   150|print(sys.getsizeof(nums_gen))   # ~200 bytes！
   151|
   152|# 用 sum() 消费生成器
   153|print(sum(nums_gen))  # 计算过程中内存只占 200 bytes''',
   154|        "takeaway": "方括号 [] 是列表（占内存），圆括号 () 是生成器（省内存）。大数据量时优先用生成器。",
   155|    },
   156|    {
   157|        "title": "dict.get() 一行搞定「取值 + 默认值」",
   158|        "code": '''config = {"host": "localhost", "port": 8080}
   159|
   160|# ❌ 啰嗦写法
   161|timeout = config["timeout"] if "timeout" in config else 30
   162|
   163|# ✅ Pythonic 写法
   164|timeout = config.get("timeout", 30)
   165|
   166|# 嵌套取值也不怕
   167|user = {"profile": {"name": "Alice"}}
   168|city = user.get("profile", {}).get("city", "未知")
   169|print(city)  # 未知（不会抛 KeyError）''',
   170|        "takeaway": "从不存在的 key 取值用 .get() 而不是 []，避免 KeyError 崩溃。",
   171|    },
   172|    {
   173|        "title": "enumerate()：遍历时同时拿索引和值",
   174|        "code": '''items = ["苹果", "香蕉", "橙子"]
   175|
   176|# ❌ 新手写法
   177|for i in range(len(items)):
   178|    print(f"{i+1}. {items[i]}")
   179|
   180|# ✅ Pythonic 写法
   181|for i, item in enumerate(items, start=1):
   182|    print(f"{i}. {item}")
   183|
   184|# 输出：
   185|# 1. 苹果
   186|# 2. 香蕉
   187|# 3. 橙子''',
   188|        "takeaway": "需要索引时用 enumerate()，不要用 range(len())。start 参数可以自定义起始值。",
   189|    },
   190|    {
   191|        "title": "浅拷贝 vs 深拷贝：嵌套对象的地雷",
   192|        "code": '''import copy
   193|
   194|original = [[1, 2], [3, 4]]
   195|
   196|# 浅拷贝：外层新对象，内层还是引用
   197|shallow = original.copy()   # 或 list(original)，或 original[:]
   198|shallow[0][0] = 99
   199|print(original[0])  # [99, 2] ← 原对象内层也被改了！
   200|
   201|# 深拷贝：完全独立
   202|original = [[1, 2], [3, 4]]
   203|deep = copy.deepcopy(original)
   204|deep[0][0] = 99
   205|print(original[0])  # [1, 2] ← 不受影响''',
   206|        "takeaway": ".copy() / list() / [:] 都是浅拷贝。嵌套结构要独立，用 copy.deepcopy()。",
   207|    },
   208|]
   209|
   210|
   211|# ========== 搜索 GitHub ==========
   212|
   213|def search_github(query, per_page=3):
   214|    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
   215|    url = (
   216|        f"https://api.github.com/search/repositories"
   217|        f"?q={query}+pushed:>{week_ago}"
   218|        f"&sort=stars&order=desc&per_page={per_page}"
   219|    )
   220|    ctx = ssl.create_default_context()
   221|    ctx.check_hostname = False
   222|    ctx.verify_mode = ssl.CERT_NONE
   223|
   224|    req = urllib.request.Request(url, headers={
   225|        "User-Agent": "DailyDigest/1.0",
   226|        "Accept": "application/vnd.github.v3+json",
   227|    })
   228|    try:
   229|        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
   230|            data = json.loads(resp.read().decode())
   231|    except Exception as e:
   232|        print(f"  ⚠️ GitHub API 失败: {e}")
   233|        return []
   234|
   235|    results = []
   236|    for item in data.get("items", [])[:per_page]:
   237|        results.append({
   238|            "name": item["full_name"],
   239|            "url": item["html_url"],
   240|            "stars": item["stargazers_count"],
   241|            "desc": (item.get("description") or "无描述")[:150],
   242|            "lang": item.get("language") or "N/A",
   243|        })
   244|    return results
   245|
   246|
   247|# ========== 格式化飞书消息 ==========
   248|
   249|def build_feishu_card(categories_data, python_tip):
   250|    today = datetime.now(timezone.utc)
   251|    beijing = today + timedelta(hours=8)
   252|    date_str = beijing.strftime("%Y-%m-%d")
   253|
   254|    elements = []
   255|    for cat in CATEGORIES:
   256|        items = categories_data.get(cat["name"], [])
   257|        if not items:
   258|            continue
   259|        lines = [f"**{cat['name']}**\n"]
   260|        for i, item in enumerate(items, 1):
   261|            stars = f"⭐ {item['stars']:,}"
   262|            lines.append(
   263|                f"{i}. <a href='{item['url']}'>{item['name']}</a>  {stars}\n"
   264|                f"   {item['desc']}\n"
   265|            )
   266|        elements.append({"tag": "markdown", "content": "".join(lines)})
   267|        elements.append({"tag": "hr"})
   268|
   269|    tip = python_tip
   270|    tip_text = (
   271|        f"**🐍 Python 今日知识点：{tip['title']}**\n\n"
   272|        f"```python\n{tip['code']}\n```\n\n"
   273|        f"💡 {tip['takeaway']}"
   274|    )
   275|    elements.append({"tag": "markdown", "content": tip_text})
   276|
   277|    return {
   278|        "msg_type": "interactive",
   279|        "card": {
   280|            "header": {
   281|                "title": {
   282|                    "tag": "plain_text",
   283|                    "content": f"🔥 每日技术推送 | {date_str}",
   284|                },
   285|                "template": "blue",
   286|            },
   287|            "elements": elements,
   288|            "config": {"wide_screen_mode": True},
   289|        },
   290|    }
   291|
   292|
   293|# ========== 发送到飞书 ==========
   294|
   295|def send_to_feishu(webhook_url, card, secret=""):
   296|    if not webhook_url:
   297|        print("⚠️ 未设置 FEISHU_WEBHOOK，跳过发送")
   298|        print(json.dumps(card, ensure_ascii=False, indent=2))
   299|        return False
   300|
   301|    url = webhook_url
   302|    if secret:
   303|        ts = str(int(time.time()))
   304|        sign_string = f"{ts}\n{secret}"
   305|        hmac_code = hmac.new(
   306|            secret.encode("utf-8"),
   307|            sign_string.encode("utf-8"),
   308|            digestmod=hashlib.sha256,
   309|        )
   310|        signature = base64.b64encode(hmac_code.digest()).decode("utf-8")
   311|        url = f"{webhook_url}?timestamp={ts}&sign={signature}"
   312|
   313|    data = json.dumps(card, ensure_ascii=False).encode("utf-8")
   314|    req = urllib.request.Request(
   315|        url, data=data,
   316|        headers={"Content-Type": "application/json; charset=utf-8"},
   317|    )
   318|    ctx = ssl.create_default_context()
   319|    ctx.check_hostname = False
   320|    ctx.verify_mode = ssl.CERT_NONE
   321|
   322|    try:
   323|        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
   324|            result = json.loads(resp.read().decode())
   325|            if result.get("code") == 0:
   326|                print("✅ 飞书推送成功")
   327|                return True
   328|            else:
   329|                print(f"❌ 飞书返回错误: {result}")
   330|                return False
   331|    except Exception as e:
   332|        print(f"❌ 飞书请求失败: {e}")
   333|        return False
   334|
   335|
   336|# ========== 主流程 ==========
   337|
   338|def main():
   339|    print("=" * 50)
   340|    print("  每日技术推送 — 开始")
   341|    print("=" * 50)
   342|
   343|    categories_data = {}
   344|    for cat in CATEGORIES:
   345|        print(f"\n🔍 搜索: {cat['name']} ...")
   346|        items = search_github(cat["query"])
   347|        categories_data[cat["name"]] = items
   348|        print(f"   找到 {len(items)} 个项目")
   349|        for item in items:
   350|            print(f"   - {item['name']} ⭐{item['stars']}")
   351|
   352|    tip = random.choice(PYTHON_TIPS)
   353|    print(f"\n🐍 今日 Python 知识点: {tip['title']}")
   354|
   355|    card = build_feishu_card(categories_data, tip)
   356|    print(f"\n📤 发送到飞书...")
   357|    success = send_to_feishu(FEISHU_WEBHOOK, card, FEISHU_SECRET)
   358|
   359|    if success:
   360|        print("\n✅ 全部完成！")
   361|    else:
   362|        print("\n⚠️ 发送未完成（可能缺少 Webhook 配置）")
   363|    print("=" * 50)
   364|
   365|
   366|if __name__ == "__main__":
   367|    main()/bin/bash: line 5: C:/Users/16485/.hermes/cache/terminal/hermes-snap-65c6e6b5391f.sh: No such file or directory
   368|/bin/bash: line 6: C:/Users/16485/.hermes/cache/terminal/hermes-cwd-65c6e6b5391f.txt: No such file or directory
   369|/bin/bash: line 5: C:/Users/16485/.hermes/cache/terminal/hermes-snap-65c6e6b5391f.sh: No such file or directory
   370|/bin/bash: line 6: C:/Users/16485/.hermes/cache/terminal/hermes-cwd-65c6e6b5391f.txt: No such file or directory
   371|