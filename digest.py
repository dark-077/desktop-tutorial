#!/usr/bin/env python3
"""
每日技术推送 — 精选工具推荐 + Python 知识点，推送到飞书群机器人
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


# ========== 精选工具库（手动维护，每个都有「怎么用」说明）==========

TOOLS = {
    "📹 免费视频/屏幕工具": [
        {
            "name": "OBS Studio",
            "url": "https://obsproject.com/",
            "desc": "免费开源录屏+直播软件，B站/YouTube 主播标配",
            "why": "想做视频教程、录制网课、或者直播？OBS 是免费里最强的，没有水印没有时长限制。",
            "how_to_use": "① 官网下载安装 → ② 点「+」添加「显示器采集」→ ③ 点「开始录制」即可。5 分钟搞定第一支视频。",
        },
        {
            "name": "Screenity（浏览器插件）",
            "url": "https://github.com/alyssaxuu/screenity",
            "desc": "Chrome 插件，一键录屏+标注+画圈，不用装软件",
            "why": "不想装软件？Screenity 直接在浏览器里录，还能边录边在屏幕上画圈、写字，做教程超方便。",
            "how_to_use": "① Chrome 应用商店搜「Screenity」安装 → ② 点插件图标 → ③ 选「整个屏幕」或「当前标签页」→ 开始录。",
        },
        {
            "name": "HandBrake",
            "url": "https://handbrake.fr/",
            "desc": "免费视频压缩/格式转换工具",
            "why": "录完视频太大发不出去？HandBrake 能把 1GB 视频压到 100MB，画质几乎不变。",
            "how_to_use": "① 打开 HandBrake → ② 拖入视频文件 → ③ 预设选「Fast 1080p30」→ ④ 点「开始编码」。",
        },
        {
            "name": "剪映（CapCut）",
            "url": "https://www.capcut.cn/",
            "desc": "国内最流行的免费剪辑软件，自动字幕生成",
            "why": "完全免费、自动生成字幕、海量模板。做短视频、vlog、学习笔记视频的首选。",
            "how_to_use": "① 官网下载 → ② 导入视频 → ③ 点「文本」→「智能字幕」自动加字幕 → ④ 导出。",
        },
    ],
    "🤖 AI 实用工具": [
        {
            "name": "DeepSeek",
            "url": "https://chat.deepseek.com/",
            "desc": "国产 AI 对话，免费，代码+写作+翻译都很强",
            "why": "你已经用过了！写代码、学英语、翻译论文都可以问它。关键是免费，不限次数。",
            "how_to_use": "① 网页打开直接对话 → ② 问任何问题 → ③ 上传文件（PDF/Word）让它帮你总结。App 也支持语音输入。",
        },
        {
            "name": "豆包（字节跳动）",
            "url": "https://www.doubao.com/",
            "desc": "字节跳动的 AI 助手，界面友好，免费",
            "why": "比 DeepSeek 更贴近日常生活场景，支持图片生成、AI 搜索、文档分析。适合不折腾的普通用户。",
            "how_to_use": "① 网页或 App 打开 → ② 直接对话 → ③ 可以上传图片让它识别、上传文档让它总结。",
        },
        {
            "name": "GitHub Copilot",
            "url": "https://github.com/features/copilot",
            "desc": "AI 编程助手，在你写代码时自动补全",
            "why": "学 Python 的时候开着它，就像旁边坐了个助教。你写注释，它帮你生成代码。学生认证免费！",
            "how_to_use": "① GitHub 学生认证（edu 邮箱）→ ② VS Code 装 Copilot 插件 → ③ 写注释它就自动建议代码。",
        },
        {
            "name": "通义千问（阿里）",
            "url": "https://tongyi.aliyun.com/",
            "desc": "阿里的 AI 对话，对接阿里生态",
            "why": "处理中文长文档（论文、报告）能力很强，支持 1000 万字上下文，一次塞一本书进去。",
            "how_to_use": "① 网页打开 → ② 上传 PDF/Word → ③ 让它总结、翻译、提取要点。全部免费。",
        },
    ],
    "✍️ 英语学习/写作工具": [
        {
            "name": "DeepL Write",
            "url": "https://www.deepl.com/write",
            "desc": "AI 英语写作润色，比 Grammarly 更自然",
            "why": "写完英语作文不知道有没有语法错误？DeepL Write 帮你改语法、换表达，针对非母语者设计。",
            "how_to_use": "① 网页打开 → ② 把英语作文粘贴进去 → ③ 右边出润色结果，可切换风格（正式/商务/日常）。",
        },
        {
            "name": "Language Reactor",
            "url": "https://www.languagereactor.com/",
            "desc": "浏览器插件，看 YouTube/Netflix 时显示双语字幕",
            "why": "用英语视频学英语的利器——同时显示中英字幕，点单词查释义，自动暂停让你跟读。",
            "how_to_use": "① Chrome 应用商店安装 → ② 打开 YouTube 视频 → ③ 右边出现字幕面板，点单词查意思。",
        },
        {
            "name": "欧路词典",
            "url": "https://www.eudic.net/",
            "desc": "支持导入第三方词库的词典 App",
            "why": "可以导入牛津、柯林斯等专业词库，鼠标取词翻译。考研/四六级必装。",
            "how_to_use": "① 官网下载安装 → ② 设置里勾选「鼠标取词」→ ③ 浏览器/PDF 里划词就能查。",
        },
        {
            "name": "Grammarly",
            "url": "https://www.grammarly.com/",
            "desc": "全球最流行的英语写作检查工具",
            "why": "不只是改拼写——会告诉你为什么错，帮你养成正确的写作习惯。免费版就够日常用。",
            "how_to_use": "① 注册 → ② 装浏览器插件 → ③ 在任何网页文本框（邮件、作业）里写英语，自动纠错。",
        },
    ],
    "🛠 开发者效率工具": [
        {
            "name": "VS Code",
            "url": "https://code.visualstudio.com/",
            "desc": "微软免费代码编辑器，Python/前端/后端通吃",
            "why": "全球开发者首选——轻量、免费、插件丰富。写 Python、Vue、Markdown 都有最好的支持。",
            "how_to_use": "① 官网下载 → ② 装 Python 插件（点左侧扩展图标搜索）→ ③ Ctrl+` 打开终端直接运行代码。",
        },
        {
            "name": "Everything（文件搜索）",
            "url": "https://www.voidtools.com/",
            "desc": "Windows 文件秒搜工具，比系统自带快 100 倍",
            "why": "Windows 自带搜索太慢？Everything 输入文件名瞬间出结果，1TB 硬盘也能秒搜。",
            "how_to_use": "① 下载安装 → ② 打开后直接打字 → ③ 搜索结果即时显示，双击打开文件。",
        },
        {
            "name": "Snipaste（截图+贴图）",
            "url": "https://www.snipaste.com/",
            "desc": "截图后可以「贴」在屏幕上的工具",
            "why": "截完图直接贴在屏幕上当参考（比如把题目贴在屏幕角落对照着写代码）。程序员效率提升神器。",
            "how_to_use": "① 下载 → ② F1 截图 → ③ F3 把截图贴到屏幕上 → ④ 按 Esc 关闭。",
        },
        {
            "name": "uTools",
            "url": "https://www.u.tools/",
            "desc": "一个快捷键调出所有小工具：翻译、计算、二维码、颜色…",
            "why": "装一个 uTools = 装了几十个小工具。Alt+空格呼出，搜什么用什么。",
            "how_to_use": "① 官网下载 → ② Alt+空格呼出 → ③ 输入「翻译 hello」就能翻译，输入「颜色」就能取色。",
        },
        {
            "name": "Ditto（剪贴板管理）",
            "url": "https://ditto-cp.sourceforge.io/",
            "desc": "保存你复制过的所有内容，随时找回",
            "why": "刚复制的东西被覆盖了？Ditto 记住你复制过的所有内容（甚至重启后还在）。写论文、写代码必备。",
            "how_to_use": "① 安装 → ② 正常 Ctrl+C → ③ Ctrl+` 打开 Ditto 列表 → ④ 双击历史记录粘贴。",
        },
    ],
}


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


# ========== 格式化飞书消息 ==========

def build_feishu_card(tools_today, python_tip):
    """tools_today: { "分类名": 工具dict, ... } 每天每个分类挑一个"""
    today = datetime.now(timezone.utc)
    beijing = today + timedelta(hours=8)
    date_str = beijing.strftime("%Y-%m-%d")

    elements = []
    for cat_name, tool in tools_today.items():
        if not tool:
            continue

        text = (
            f"**{cat_name}**\n\n"
            f"🔧 **{tool['name']}** — {tool['desc']}\n\n"
            f"📌 为什么推荐？\n{tool['why']}\n\n"
            f"🚀 一分钟上手：\n{tool['how_to_use']}\n\n"
            f"🔗 {tool['url']}"
        )
        elements.append({"tag": "markdown", "content": text})
        elements.append({"tag": "hr"})

    # Python 知识点
    tip_text = (
        f"**🐍 Python 今日知识点：{python_tip['title']}**\n\n"
        f"```python\n{python_tip['code']}\n```\n\n"
        f"💡 {python_tip['takeaway']}"
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

    # 每个分类随机选 1 个工具
    tools_today = {}
    for cat_name, tool_list in TOOLS.items():
        picked = random.choice(tool_list)
        tools_today[cat_name] = picked
        print(f"🔧 [{cat_name}] → {picked['name']}")

    # 随机选一个 Python 知识点
    tip = random.choice(PYTHON_TIPS)
    print(f"🐍 Python 知识点: {tip['title']}")

    # 构建卡片并发送
    card = build_feishu_card(tools_today, tip)
    print(f"\n📤 发送到飞书...")
    success = send_to_feishu(FEISHU_WEBHOOK, card, FEISHU_SECRET)

    if success:
        print("\n✅ 全部完成！")
    else:
        print("\n⚠️ 发送未完成（可能缺少 Webhook 配置）")
    print("=" * 50)


if __name__ == "__main__":
    main()