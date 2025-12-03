# Claude Code CLI 使用指南

> 版本: 2.0.57

Claude Code 是 Anthropic 官方的命令列介面工具，可直接呼叫 AI agent 協助完成各種軟體工程任務。

## 基本用法

```bash
claude [options] [command] [prompt]
```

預設啟動互動式會話，使用 `-p/--print` 可進行非互動式輸出。

---

## 主要選項

### 會話控制

| 選項 | 說明 |
|------|------|
| `-c, --continue` | 繼續最近一次對話 |
| `-r, --resume [sessionId]` | 恢復指定會話（可互動選擇） |
| `--fork-session` | 恢復時建立新會話 ID（搭配 --resume 或 --continue） |
| `--session-id <uuid>` | 使用指定的會話 ID |

### 輸出模式

| 選項 | 說明 |
|------|------|
| `-p, --print` | 輸出回應後結束（適用於 pipe） |
| `--output-format <format>` | 輸出格式：`text`（預設）、`json`、`stream-json` |
| `--input-format <format>` | 輸入格式：`text`（預設）、`stream-json` |
| `--json-schema <schema>` | 結構化輸出的 JSON Schema 驗證 |
| `--include-partial-messages` | 即時串流包含部分訊息 |
| `--replay-user-messages` | 從 stdin 讀取的使用者訊息回傳到 stdout（僅串流模式） |

### 模型設定

| 選項 | 說明 |
|------|------|
| `--model <model>` | 指定模型（可用別名如 `sonnet`、`opus` 或完整名稱） |
| `--fallback-model <model>` | 預設模型過載時的備用模型（僅 --print 模式） |

#### 可用模型

**別名（簡短）：**

| 別名 | 對應模型 | 適用場景 |
|------|----------|----------|
| `haiku` | Claude Haiku（最新版） | 快速、簡單任務，成本較低 |
| `sonnet` | Claude Sonnet 4.5（最新版） | 平衡效能與成本，日常使用 |
| `opus` | Claude Opus 4.5（最新版） | 複雜推理、深度分析任務 |

**完整模型名稱範例：**

- `claude-sonnet-4-5-20250929`
- `claude-opus-4-5-20251101`
- `claude-3-5-haiku-20241022`

### 系統提示

| 選項 | 說明 |
|------|------|
| `--system-prompt <prompt>` | **取代**預設系統提示，使用自訂的提示 |
| `--append-system-prompt <prompt>` | **附加**到預設系統提示後面（保留內建提示） |

### 工具與權限

| 選項 | 說明 |
|------|------|
| `--allowedTools <tools...>` | 允許的工具清單（如 `"Bash(git:*) Edit"`） |
| `--disallowedTools <tools...>` | 禁用的工具清單 |
| `--tools <tools...>` | 指定可用工具（`""`=全部禁用, `default`=全部啟用） |
| `--permission-mode <mode>` | 權限模式：`acceptEdits`, `bypassPermissions`, `default`, `dontAsk`, `plan` |
| `--dangerously-skip-permissions` | 跳過所有權限檢查（僅建議用於沙盒環境） |
| `--allow-dangerously-skip-permissions` | 允許跳過權限檢查作為選項，但預設不啟用 |

### 其他設定

| 選項 | 說明 |
|------|------|
| `-d, --debug [filter]` | 啟用除錯模式（可過濾類別） |
| `--verbose` | 詳細模式 |
| `--add-dir <directories...>` | 增加允許工具存取的目錄 |
| `--settings <file-or-json>` | 載入設定檔或 JSON 字串 |
| `--setting-sources <sources>` | 設定來源：`user`, `project`, `local`（逗號分隔） |
| `--agents <json>` | 定義自訂 agents |
| `--ide` | 自動連接 IDE |
| `--mcp-config <configs...>` | 從 JSON 檔案或字串載入 MCP 伺服器 |
| `--strict-mcp-config` | 僅使用 --mcp-config 指定的 MCP 伺服器，忽略其他設定 |
| `--plugin-dir <paths...>` | 僅本次會話載入指定目錄的插件 |

---

## 子命令

### `claude mcp` - MCP 伺服器管理

MCP（Model Context Protocol）伺服器擴展 Claude 的能力。

```bash
claude mcp [command]
```

#### MCP 子命令

| 命令 | 說明 |
|------|------|
| `serve` | 啟動 Claude Code MCP 伺服器 |
| `add <name> <commandOrUrl> [args...]` | 新增 MCP 伺服器 |
| `remove <name>` | 移除 MCP 伺服器 |
| `list` | 列出已設定的 MCP 伺服器 |
| `get <name>` | 取得 MCP 伺服器詳情 |
| `add-json <name> <json>` | 以 JSON 字串新增 MCP 伺服器 |
| `add-from-claude-desktop` | 從 Claude Desktop 匯入 MCP 伺服器 |
| `reset-project-choices` | 重設專案範圍的 MCP 伺服器核准狀態 |

#### MCP 新增範例

```bash
# HTTP 伺服器
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp

# SSE 伺服器
claude mcp add --transport sse asana https://mcp.asana.com/sse

# stdio 伺服器（含環境變數）
claude mcp add --transport stdio airtable \
  --env AIRTABLE_API_KEY=YOUR_KEY \
  -- npx -y airtable-mcp-server
```

#### MCP add 選項

| 選項 | 說明 |
|------|------|
| `-s, --scope <scope>` | 設定範圍：`local`、`user`、`project`（預設：local） |
| `-t, --transport <transport>` | 傳輸類型：`stdio`、`sse`、`http` |
| `-e, --env <env...>` | 設定環境變數 |
| `-H, --header <header...>` | 設定 WebSocket headers |

---

### `claude plugin` - 插件管理

```bash
claude plugin [command]
```

| 命令 | 說明 |
|------|------|
| `validate <path>` | 驗證插件或市場清單 |
| `marketplace` | 管理插件市場 |
| `install <plugin>` | 安裝插件（可用 `plugin@marketplace` 指定來源） |
| `uninstall <plugin>` | 解除安裝插件 |
| `enable <plugin>` | 啟用插件 |
| `disable <plugin>` | 停用插件 |

---

### 其他命令

| 命令 | 說明 |
|------|------|
| `migrate-installer` | 從全域 npm 安裝遷移到本地安裝 |
| `setup-token` | 設定長期認證 token（需 Claude 訂閱） |
| `doctor` | 檢查自動更新器健康狀態 |
| `update` | 檢查並安裝更新 |
| `install [target]` | 安裝原生版本（`stable`、`latest` 或指定版本） |

---

## 常用使用情境

### 互動式會話
```bash
claude
```

### 單次查詢
```bash
claude -p "解釋這段程式碼的功能"
```

### 繼續上次對話
```bash
claude -c
```

### 指定模型
```bash
claude --model opus "幫我重構這個函數"
```

### 管線處理
```bash
cat file.py | claude -p "review this code"
```

### JSON 結構化輸出
```bash
claude -p --output-format json --json-schema '{"type":"object","properties":{"summary":{"type":"string"}}}' "總結這個專案"
```

---

## 自訂 Agents

透過 `--agents` 選項可定義自訂 agents：

```bash
claude --agents '{"reviewer": {"description": "Reviews code", "prompt": "You are a code reviewer"}}'
```

---

## 相關資源

- 問題回報: https://github.com/anthropics/claude-code/issues
- 使用 `/help` 取得互動式幫助
