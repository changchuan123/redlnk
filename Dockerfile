# ============================================
# 红墨 AI图文生成器 - Docker 镜像
# ============================================

# 阶段1: 构建前端
FROM node:22-slim AS frontend-builder

WORKDIR /app/frontend

# 安装特定版本的 pnpm 以确保兼容性
RUN npm install -g pnpm@8

# 复制前端依赖文件
COPY frontend/package.json frontend/pnpm-lock.yaml ./

# 如果锁文件不兼容，强制重新生成
RUN pnpm install --frozen-lockfile || \
    (echo "Lockfile incompatible, regenerating..." && \
     rm -f pnpm-lock.yaml && \
     pnpm install && \
     pnpm install > /dev/null 2>&1)

# 复制前端源码
COPY frontend/ ./

# 构建前端
RUN pnpm build

# ============================================
# 阶段2: 最终镜像
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv
RUN pip install --no-cache-dir uv

# 复制 Python 项目配置
COPY pyproject.toml uv.lock* ./

# 安装 Python 依赖
RUN uv sync --no-dev

# 复制后端代码
COPY backend/ ./backend/

# 复制配置文件模板（用户可在 Web 界面配置 API Key）
COPY docker/text_providers.yaml ./text_providers.yaml
COPY docker/image_providers.yaml ./image_providers.yaml

# 从构建阶段复制前端产物
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# 创建输出目录
RUN mkdir -p output

# 设置环境变量（Zeabur 会自动设置 PORT 环境变量）
ENV FLASK_DEBUG=False
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=10008

# 暴露端口（Zeabur 会自动映射，这里使用默认端口）
EXPOSE 10008

# 健康检查（Zeabur 会自动处理，这里保留作为备用）
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#     CMD python -c "import os, urllib.request; port=os.getenv('PORT', '10008'); urllib.request.urlopen(f'http://localhost:{port}/api/health')" || exit 1

# 启动命令
CMD ["uv", "run", "python", "-m", "backend.app"]
