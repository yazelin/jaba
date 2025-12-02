# Project Context

## Purpose
jaba（呷爸）是一個由 AI Agent (Claude) 協助的午餐訂便當系統。系統英文名稱 "jaba"，中文顯示名稱為「呷爸」，同時也是 AI Agent 的名稱。這是一個供團隊內部使用的工具，目標是簡化午餐訂餐流程。

## Tech Stack
- **後端**: Python 3.12 + FastAPI + Socket.IO（即時通訊）
- **套件管理**: uv
- **前端**: 純 HTML/CSS/JavaScript（無框架）
- **資料儲存**: 檔案系統（資料夾 + JSON 檔案，不使用資料庫）
- **AI 整合**: Claude CLI

## Project Conventions

### Code Style
- Python 程式碼遵循 PEP 8 規範
- 使用 type hints 進行型別標註
- 變數和函數使用 snake_case 命名
- 類別使用 PascalCase 命名
- 保持程式碼簡潔，避免過度抽象

### Architecture Patterns
- 簡單直接的單體架構
- FastAPI 路由直接處理業務邏輯
- 檔案儲存使用結構化的目錄組織
- 保持最少的抽象層，優先可讀性

### Testing Strategy
- 使用 pytest 進行單元測試
- 關鍵業務邏輯需要測試覆蓋
- API 端點使用 FastAPI TestClient 測試

### Git Workflow
- 主分支：main
- 功能分支：feature/[功能名稱]
- 修復分支：fix/[問題描述]
- Commit 訊息使用中文或英文皆可

## Domain Context
- **午餐訂餐**: 系統協助團隊成員訂購午餐便當
- **AI Agent (呷爸)**: Claude 扮演的助手角色，協助處理訂餐相關事務
- **便當店**: 合作的便當店家資訊
- **訂單**: 團隊成員的午餐訂單
- **團隊聊天**: 團隊成員即時討論今日午餐

## Important Constraints
- 資料使用檔案系統儲存，無需資料庫
- 系統為內部使用，不需複雜的認證機制
- 保持架構簡單，避免過度工程化
- AI Agent 回應使用繁體中文

## External Dependencies
- **Anthropic Claude API**: AI Agent 核心功能
- **便當店 API/聯絡方式**: 取決於實際合作店家
