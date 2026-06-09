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


# ========== 精选工具库 v3 — 开发者成长路线 ==========
TOOLS = {
    "🤖 AI Agent & 框架": [
        {"name": "Ollama + Open-WebUI", "url": "https://ollama.com/", "desc": "本地运行大模型，一行命令", "why": "学 AI 第一步：自己电脑跑模型。Ollama 一行命令下载 DeepSeek/Qwen，Open-WebUI 套 ChatGPT 同款界面，完全免费离线。", "how_to_use": "① 下载 Ollama → ② 终端 ollama run deepseek-r1:7b → ③ 装 Open-WebUI 界面 → ④ 浏览器打开对话"},
        {"name": "Dify", "url": "https://github.com/langgenius/dify", "desc": "不写代码搭 AI 应用 (144k⭐)", "why": "想做 AI 批改作文？Dify 拖拽搭出来。LLM+知识库+工作流全可视化。先做原型验证想法。", "how_to_use": "① cloud.dify.ai 注册 → ② 创建聊天助手 → ③ 写 Prompt → ④ 发布，得到可分享链接"},
        {"name": "LangChain + LangGraph", "url": "https://github.com/langchain-ai/langchain", "desc": "AI Agent 工业标准 (138k+34k⭐)", "why": "需要精确控制 agent？LangChain 是行业标配。LangGraph 用状态机限制行为——不靠希望，靠代码。", "how_to_use": "pip install langchain langchain-openai → 用 create_tool_calling_agent 写第一个 agent"},
        {"name": "MetaGPT", "url": "https://github.com/FoundationAgents/MetaGPT", "desc": "一句话生成完整项目 (68k⭐)", "why": "模拟完整软件公司：产品经理→架构师→程序员→测试员。「写贪吃蛇」→完整代码+文档+测试。", "how_to_use": "pip install metagpt → 配置 API key → metagpt 写一个命令行待办事项工具"},
        {"name": "Microsoft AutoGen", "url": "https://github.com/microsoft/autogen", "desc": "微软多 Agent 框架 (58k⭐)", "why": "对话即编程——多个 agent 对话协作。大厂背书，工业界在用。适合多轮交互复杂场景。", "how_to_use": "pip install autogen-agentchat → 创建 AssistantAgent + UserProxyAgent → 给任务"},
        {"name": "CrewAI", "url": "https://github.com/crewAIInc/crewAI", "desc": "多 Agent 任务编排 (53k⭐)", "why": "你正用 Hermes+Claude 双 agent，CrewAI 把这种模式框架化了。学完从经验上升到方法论。", "how_to_use": "pip install crewai → 定义 Agent(role=研究员) + Task → crew.kickoff()"},
    ],
    "🎨 AI 创作工具": [
        {"name": "Stable Diffusion WebUI", "url": "https://github.com/AUTOMATIC1111/stable-diffusion-webui", "desc": "AI 绘画的 Photoshop (163k⭐)", "why": "想做 AI 绘画？这是所有教程的起点。图生图、ControlNet 精准控制全支持。", "how_to_use": "需 NVIDIA 显卡 6GB+ → git clone → 下载模型 → 运行 webui-user.bat → localhost:7860"},
        {"name": "Open-Generative-AI", "url": "https://github.com/Anil-matcha/Open-Generative-AI", "desc": "200+ AI 模型的免费工作室 (18k⭐)", "why": "集成图片/视频/音乐生成，浏览器直接用。快速体验 AI 创作，找到方向再深入。", "how_to_use": "git clone → npm install && npm run dev → 浏览器打开 → 选模型生成"},
        {"name": "Duix-Avatar", "url": "https://github.com/duixcom/Duix-Avatar", "desc": "AI 数字人：照片+音频=视频 (13k⭐)", "why": "想做虚拟老师/主播？真开源 C 语言方案。读源码学音视频同步、实时渲染。", "how_to_use": "克隆项目 → 下载模型 → 准备照片+音频 → 运行脚本生成数字人视频"},
        {"name": "KrillinAI", "url": "https://github.com/krillinai/KrillinAI", "desc": "视频翻译配音一条龙 (10k⭐)", "why": "YouTube/B站视频自动翻译成中文配音。看国外教程效率翻倍。", "how_to_use": "下载桌面版 → 粘贴视频链接 → 选语言 → 点开始"},
        {"name": "Toonflow", "url": "https://github.com/HBAI-Ltd/Toonflow-app", "desc": "AI 短剧：小说→动画 (9.7k⭐)", "why": "国内团队开源。NLP→分镜→角色→合成，全链路源码可读。", "how_to_use": "下载桌面版 → 导入剧本 → AI 拆分分镜 → 导出视频"},
        {"name": "FireRed-OpenStoryline", "url": "https://github.com/FireRedTeam/FireRed-OpenStoryline", "desc": "自然语言操作剪辑 (2.8k⭐)", "why": "说「删第三段」它自动操作 FFmpeg。LangChain+FFmpeg，学 Agent 操作真实工具的好案例。", "how_to_use": "git clone → pip install → 导入视频 → 自然语言告诉它怎么剪"},
    ],
    "🛠 开发者效率工具": [
        {"name": "VS Code", "url": "https://code.visualstudio.com/", "desc": "全球开发者首选编辑器", "why": "轻量免费插件丰富。Python/Vue/Markdown 全支持。", "how_to_use": "① 官网下载 → ② 装 Python 插件 → ③ Ctrl+` 打开终端"},
        {"name": "Everything", "url": "https://www.voidtools.com/", "desc": "Windows 文件秒搜", "why": "输入文件名瞬间出结果，1TB 硬盘秒搜。", "how_to_use": "① 下载安装 → ② 打开打字 → ③ 双击打开文件"},
        {"name": "Snipaste", "url": "https://www.snipaste.com/", "desc": "截图后贴屏幕上", "why": "截完图贴在屏幕当参考。程序员效率神器。", "how_to_use": "① 下载 → ② F1 截图 → ③ F3 贴到屏幕"},
        {"name": "uTools", "url": "https://www.u.tools/", "desc": "Alt+空格万能工具箱", "why": "一个工具 = 翻译+计算+二维码+颜色… 用完即走。", "how_to_use": "① 下载 → ② Alt+空格 → ③ 输入翻译 hello"},
        {"name": "Ditto", "url": "https://ditto-cp.sourceforge.io/", "desc": "剪贴板历史管理", "why": "记住所有复制历史，重启后还在。写代码写论文必备。", "how_to_use": "① 安装 → ② Ctrl+C → ③ Ctrl+` 打开列表 → ④ 双击粘贴"},
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