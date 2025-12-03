# Gemini CLI 使用指南

> 版本: 0.19.1

Gemini CLI 是 Google 的命令列介面工具，可直接呼叫 Gemini AI 協助完成各種任務。

## 基本用法

```bash
gemini [options] [query...]
```

預設啟動互動式會話，使用位置參數 query 可進行單次查詢。

---

## 主要選項

### 會話（Session）管理

| 選項 | 說明 |
|------|------|
| `-r, --resume <index\|latest>` | 接續之前的會話，使用 `latest` 接續最近一次，或指定索引編號 |
| `--list-sessions` | 列出當前專案可用的會話並結束 |
| `--delete-session <index>` | 刪除指定索引的會話 |

#### Session 操作範例

```bash
# 開新 session（直接執行，不加 --resume）
gemini

# 查看所有 session
gemini --list-sessions

# 接續最近的 session
gemini --resume latest
gemini -r latest

# 接續特定編號的 session（編號從 --list-sessions 查看）
gemini -r 5

# 刪除 session
gemini --delete-session 5
```

### 輸出模式

| 選項 | 說明 |
|------|------|
| `-o, --output-format <format>` | 輸出格式：`text`、`json`、`stream-json` |

### 模型設定

| 選項 | 說明 |
|------|------|
| `-m, --model <model>` | 指定模型（使用 Model ID） |

#### 可用模型

| 選項 | Model ID | 說明 |
|------|----------|------|
| Auto | (系統自動選擇) | 讓系統選擇最佳模型 |
| Pro | `gemini-2.5-pro` | 複雜任務，深度推理和創意 |
| Flash | `gemini-2.5-flash` | 平衡速度與推理 |
| Flash-Lite | `gemini-2.5-flash-lite` | 簡單任務，快速完成 |

> **Gemini 3 預覽版**：可在互動模式中進入 `/settings` 啟用 "Preview features" 來使用。

```bash
# 指定模型範例
gemini -m gemini-2.5-pro
gemini -m gemini-2.5-flash
gemini -m gemini-2.5-flash-lite
```

### 提示模式

| 選項 | 說明 |
|------|------|
| `-p, --prompt <prompt>` | 提示（已棄用，建議使用位置參數） |
| `-i, --prompt-interactive <prompt>` | 執行提供的提示後繼續互動模式 |

### 工具與權限

| 選項 | 說明 |
|------|------|
| `-y, --yolo` | 自動接受所有操作（YOLO 模式） |
| `--approval-mode <mode>` | 核准模式：`default`（提示核准）、`auto_edit`（自動核准編輯工具）、`yolo`（自動核准所有工具） |
| `--allowed-tools <tools...>` | 允許無需確認即可執行的工具 |

### 其他設定

| 選項 | 說明 |
|------|------|
| `-d, --debug` | 啟用除錯模式 |
| `-s, --sandbox` | 在沙盒中執行 |
| `--include-directories <dirs...>` | 額外包含在工作區的目錄（逗號分隔或多次指定） |
| `--screen-reader` | 啟用螢幕閱讀器模式（無障礙功能） |
| `-v, --version` | 顯示版本號 |
| `-h, --help` | 顯示幫助 |

### 擴充功能相關

| 選項 | 說明 |
|------|------|
| `-e, --extensions <extensions...>` | 指定要使用的擴充功能列表（不指定則使用全部） |
| `-l, --list-extensions` | 列出所有可用的擴充功能並結束 |

### MCP 相關

| 選項 | 說明 |
|------|------|
| `--allowed-mcp-server-names <names...>` | 允許的 MCP 伺服器名稱 |
| `--experimental-acp` | 以 ACP 模式啟動 agent |

---

## 子命令

### `gemini mcp` - MCP 伺服器管理

MCP（Model Context Protocol）伺服器擴展 Gemini 的能力。

```bash
gemini mcp [command]
```

#### MCP 子命令

| 命令 | 說明 |
|------|------|
| `add <name> <commandOrUrl> [args...]` | 新增 MCP 伺服器 |
| `remove <name>` | 移除 MCP 伺服器 |
| `list` | 列出已設定的 MCP 伺服器 |

---

### `gemini extensions` - 擴充功能管理

管理 Gemini CLI 的擴充功能。

```bash
gemini extensions <command>
```

別名：`gemini extension`

#### Extensions 子命令

| 命令 | 說明 |
|------|------|
| `install <source> [--auto-update] [--pre-release]` | 從 git 倉庫 URL 或本地路徑安裝擴充功能 |
| `uninstall <names...>` | 解除安裝一個或多個擴充功能 |
| `list` | 列出已安裝的擴充功能 |
| `update [<name>] [--all]` | 更新所有擴充功能或指定的擴充功能到最新版本 |
| `disable [--scope] <name>` | 停用擴充功能 |
| `enable [--scope] <name>` | 啟用擴充功能 |
| `link <path>` | 連結本地路徑的擴充功能（本地更改會即時反映） |
| `new <path> [template]` | 從範本建立新的擴充功能 |
| `validate <path>` | 驗證本地路徑的擴充功能 |

---

## 常用使用情境

### 互動式會話
```bash
gemini
```

### 單次查詢
```bash
gemini "解釋這段程式碼的功能"
```

### 執行提示後繼續互動
```bash
gemini -i "先幫我分析這個專案結構"
```

### 恢復上次對話
```bash
gemini --resume latest
```

### YOLO 模式（自動接受所有操作）
```bash
gemini -y "幫我重構這個函數"
```

### 指定核准模式
```bash
gemini --approval-mode auto_edit "修改這個檔案"
```

### JSON 輸出
```bash
gemini -o json "總結這個專案"
```

### 列出可用會話
```bash
gemini --list-sessions
```

---

## 與 Claude CLI 的對照

| 功能 | Claude CLI | Gemini CLI |
|------|------------|------------|
| 繼續對話 | `-c, --continue` | `-r latest, --resume latest` |
| 非互動輸出 | `-p, --print` | 位置參數 query |
| 指定模型 | `--model` | `-m, --model` |
| 輸出格式 | `--output-format` | `-o, --output-format` |
| 自動核准 | `--dangerously-skip-permissions` | `-y, --yolo` 或 `--approval-mode yolo` |
| MCP 管理 | `claude mcp` | `gemini mcp` |
| 擴充/插件 | `claude plugin` | `gemini extensions` |
| 除錯模式 | `-d, --debug` | `-d, --debug` |

---

## 相關資源

- 使用 `gemini --help` 取得完整幫助
- 使用 `gemini mcp --help` 取得 MCP 相關幫助
- 使用 `gemini extensions --help` 取得擴充功能相關幫助
