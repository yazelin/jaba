# jaba (呷爸) AI 午餐訂便當系統
FROM python:3.12-slim

# 安裝 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# 複製依賴檔案
COPY pyproject.toml uv.lock* ./

# 安裝依賴
RUN uv sync --frozen --no-cache

# 複製應用程式
COPY . .

# 建立資料目錄
RUN mkdir -p data

# 暴露 port
EXPOSE 8098

# 啟動應用（20MB 請求大小限制以支援圖片上傳）
CMD ["uv", "run", "uvicorn", "main:socket_app", "--host", "0.0.0.0", "--port", "8098", "--limit-max-request-size", "20971520"]
