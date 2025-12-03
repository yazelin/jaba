#!/bin/bash
# 移除 jaba systemd 服務

set -e

if [ "$EUID" -ne 0 ]; then
    echo "請使用 sudo 執行此腳本"
    echo "用法: sudo $0"
    exit 1
fi

echo "移除 jaba 服務..."

# 停止服務
systemctl stop jaba 2>/dev/null || true

# 停用開機自動啟動
systemctl disable jaba 2>/dev/null || true

# 刪除 service 檔案
rm -f /etc/systemd/system/jaba.service

# 重新載入 systemd
systemctl daemon-reload

echo "服務已移除！"
