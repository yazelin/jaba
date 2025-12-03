#!/bin/bash
# 安裝 jaba systemd 服務

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="$SCRIPT_DIR/jaba.service"

if [ "$EUID" -ne 0 ]; then
    echo "請使用 sudo 執行此腳本"
    echo "用法: sudo $0"
    exit 1
fi

echo "安裝 jaba 服務..."

# 複製 service 檔案
cp "$SERVICE_FILE" /etc/systemd/system/jaba.service

# 重新載入 systemd
systemctl daemon-reload

# 啟用服務（開機自動啟動）
systemctl enable jaba

echo "服務安裝完成！"
echo ""
echo "常用指令："
echo "  sudo systemctl start jaba   # 啟動服務"
echo "  sudo systemctl stop jaba    # 停止服務"
echo "  sudo systemctl restart jaba # 重啟服務"
echo "  sudo systemctl status jaba  # 查看狀態"
echo "  journalctl -u jaba -f       # 查看即時日誌"
