# 每日技术推送 🔥

每天早上 8:00，自动搜索 GitHub 优质开源项目 + Python 知识点，推送至飞书群。

## 工作原理

```
GitHub Actions（定时触发）
    ↓
digest.py（搜索 GitHub API + 格式化）
    ↓
飞书 Webhook（推送到群聊）
```

## 配置步骤

### 1. 创建飞书机器人

1. 在飞书中创建一个群（或使用已有群）
2. 群设置 → 群机器人 → 添加机器人 → **自定义机器人**
3. 复制 Webhook 地址（格式：`https://open.feishu.cn/open-apis/bot/v2/hook/xxx`）

### 2. 配置 GitHub Secrets

1. 在 GitHub 仓库 → Settings → Secrets and variables → Actions
2. 添加 Secret：`FEISHU_WEBHOOK`，值为上一步的 Webhook 地址

### 3. 启用 GitHub Actions

推送代码到 GitHub 后，GitHub Actions 会自动启用。每天早上 8:00（北京时间）自动运行。

如需手动测试：Actions → 每日技术推送 → Run workflow。

## 自定义

编辑 `digest.py` 中的配置：

- **`CATEGORIES`**：搜索类别（修改 query 关键词）
- **`PYTHON_TIPS`**：Python 知识卡片（添加/修改）
- **`search_github()` 的 `per_page`**：每个类别搜几个项目（默认 3）

## 本地测试

```bash
# 不设置 Webhook 时，只打印预览
python digest.py

# 设置 Webhook 后，发送到飞书
FEISHU_WEBHOOK=https://open.feishu.cn/open-apis/bot/v2/hook/xxx python digest.py
```

## 注意事项

- GitHub Actions 免费额度：每月 2000 分钟，每天跑一次不到 1 分钟
- 所有搜索来自 GitHub API，无需认证，但有速率限制（60次/小时）
- 如果 GitHub API 超时，当天该类别会显示为空