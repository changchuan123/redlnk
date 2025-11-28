# 🚀 Zeabur 一键部署

本项目已配置好 Zeabur 部署，可以直接在 [Zeabur](https://zeabur.com/projects) 上一键部署。

## 📦 快速开始

### 1. 连接到 GitHub

1. 访问 [Zeabur Dashboard](https://zeabur.com/projects)
2. 点击 **"New Project"**
3. 选择 **"Import from GitHub"**
4. 授权 Zeabur 访问你的 GitHub 仓库
5. 选择 `redink` 仓库
6. 点击 **"Deploy"**

### 2. 配置 API Keys

部署完成后，访问 Zeabur 提供的域名，进入 **设置页面** (`/settings`) 配置：

#### 文本生成服务商（DeepSeek）
- 服务商名称：`deepseek`
- 类型：`openai_compatible`
- API Key：`sk-be7d4e5786a044f98f6231ab18ff52a9`
- Base URL：`https://api.deepseek.com/v1`
- Model：`deepseek-chat`

#### 图片生成服务商（Gemini）
- 服务商名称：`gemini`
- 类型：`google_genai`
- API Key：`AIzaSyBK3EIfnkKg1pejpcPZd8BA7MH2LHMQSss`
- Model：`gemini-3-pro-image-preview`

### 3. 开始使用

配置完成后，即可开始使用应用生成小红书图文内容！

## 🔧 技术栈

- **后端**: Python 3.11 + Flask
- **前端**: Vue 3 + TypeScript + Vite
- **部署**: Docker + Zeabur
- **包管理**: uv (Python) + pnpm (Node.js)

## 📝 详细文档

查看 [ZEABUR_DEPLOY.md](./ZEABUR_DEPLOY.md) 获取完整的部署说明。

## ⚙️ 环境变量

Zeabur 会自动设置以下环境变量：
- `PORT`: 应用端口（自动分配）

可选环境变量：
- `FLASK_DEBUG`: `False`（生产环境）
- `CORS_ORIGINS`: CORS 允许的来源

## 🎯 特性

- ✅ 自动构建和部署
- ✅ 支持 GitHub 自动部署
- ✅ 健康检查
- ✅ 环境变量配置
- ✅ 文件持久化（通过 Zeabur 存储）

---

**立即部署**: [https://zeabur.com/projects](https://zeabur.com/projects)

