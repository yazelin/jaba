#!/bin/bash
# jaba (呷爸) 啟動腳本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# 檢查 uv 是否安裝
if ! command -v uv &> /dev/null; then
    echo "錯誤: 找不到 uv，請先安裝 uv"
    echo "安裝指令: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# 解析參數
MODE="${1:-prod}"

case "$MODE" in
    dev|development)
        echo "啟動開發模式 (auto-reload)..."
        uv run uvicorn main:socket_app --reload --host 0.0.0.0 --port 8098
        ;;
    prod|production)
        echo "啟動生產模式..."
        uv run uvicorn main:socket_app --host 0.0.0.0 --port 8098
        ;;
    *)
        echo "用法: $0 [dev|prod]"
        echo "  dev  - 開發模式 (自動重載)"
        echo "  prod - 生產模式 (預設)"
        exit 1
        ;;
esac
