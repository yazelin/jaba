# jaba (呷爸) - 系統精華

## 一句話描述

呷爸是一個讓團隊成員用自然語言對話來訂午餐的 AI 系統，說「我要雞腿便當」就能完成訂餐。

---

## 核心運作原理

使用者輸入訊息後，系統將「系統提示詞 + 動態上下文(店家/菜單/訂單) + 對話歷史 + 當前訊息」組合送給 AI CLI，AI 回傳 JSON 格式 `{message, actions[]}`，系統執行 actions（如建立訂單），然後透過 Socket.IO 廣播給所有連線者即時更新畫面。

---

## 技術選型

後端用 Python FastAPI + Socket.IO，前端是純 HTML/CSS/JS 無框架，資料全部存成 JSON 檔案不用資料庫，AI 透過 subprocess 呼叫 Claude CLI 或 Gemini CLI。套件用 uv 管理。

---

## 三個頁面

**看板頁 `/`**：顯示今日店家、所有人的訂單列表、品項統計。

**訂餐頁 `/order`**：三欄佈局，左側菜單、中間 AI 對話、右側我的訂單與聊天室。使用者輸入名字後與呷爸對話訂餐，也可點擊菜單快速加入。

**管理頁 `/manager`**：三欄佈局，左側店家管理、中間 AI 對話、右側訂單與付款狀態。管理員可設定今日店家、上傳菜單圖片讓 AI 辨識、標記付款。

---

## 資料組織

所有資料存在 `data/` 目錄下。`system/` 放系統設定(config.json)、今日店家(today.json)、AI設定(ai_config.json)、提示詞(prompts/)。`stores/{店家id}/` 放店家資訊(info.json)和菜單(menu.json)。`users/{使用者名}/` 放個人偏好(profile.json)、訂單(orders/)、對話歷史(chat_history/)。`orders/{日期}/` 放每日彙整(summary.json)和付款記錄(payments.json)。`chat/` 放團體聊天記錄。

---

## 菜單結構

菜單分成多個分類，每個分類有多個品項。品項有名稱、價格，可選的尺寸變體(variants陣列，如M/L杯各有不同價格)，可選的促銷設定(promo物件)。促銷類型有三種：買一送一(buy_one_get_one)、第二杯折扣(second_discount，可設固定價或折數)、限時特價(time_limited)。

---

## 訂單結構

訂單記錄使用者名、店家、品項陣列(含名稱、價格、尺寸、數量、備註、卡路里、促銷折扣)、總金額、總卡路里。訂單檔名用 `{日期}-{時間戳}.json` 格式。

---

## 付款邏輯

付款記錄每個使用者的應付金額(amount)、是否已付(paid)、已付金額(paid_amount)、備註(note)。標記付款時設 paid=true 並記錄 paid_amount。若已付款後訂單金額增加，改 paid=false 並註記「待補 $X」。若金額減少，維持 paid=true 並註記「待退 $X」。退款確認後清除記錄或調整 paid_amount。

---

## AI 整合架構

AI 模組 `app/ai.py` 負責組合訊息、呼叫 CLI、解析回應、執行動作。Provider 模組 `app/providers/` 抽象化不同 CLI 的差異，ClaudeProvider 用 `claude -p` 命令，GeminiProvider 用 `gemini` 命令。對話歷史由應用自行維護(最多20條)，不依賴 CLI 的 session 機制。

---

## AI 動作類型

AI 可回傳的動作包括：`create_order`(建立訂單)、`remove_item`(移除品項)、`cancel_order`(取消訂單)、`set_today_store`(設定單一今日店家)、`add_today_store`(新增多店家)、`mark_paid`(標記付款)、`update_user_profile`(更新使用者偏好如稱呼、飲食限制)。

---

## 呷爸個性

呷爸是親切可愛的訂餐助手，說話簡潔自然，用「我們」代替「你」營造參與感，優先用使用者設定的稱呼(preferred_name)，會估算卡路里並適時給健康建議。

---

## 菜單辨識流程

管理員上傳菜單圖片，AI Vision 辨識出品項結構(含尺寸變體和促銷標示)，系統比對現有菜單產生差異：新增(綠)、修改(黃)、刪除(紅)、未變(灰)。管理員勾選要套用的項目後儲存，未勾選的維持原狀。

---

## 促銷計價規則

買一送一：每2杯收1杯價，3杯=2杯價。第二杯折扣：第2、4、6杯享折扣價。限時特價：直接用特價計算。訂單會記錄促銷類型和折扣金額。

---

## 即時同步

所有訂單建立/修改/取消、店家變更、付款狀態更新都透過 Socket.IO 廣播，前端監聽後即時更新畫面。設定店家時還會在聊天室自動發一則系統訊息通知大家。

---

## 權限控制

一般使用者只能取消自己的訂單，管理員可取消任何人的訂單。管理頁需輸入密碼驗證(預設9898)。

---

## 設定檔

`ai_config.json` 指定對話和菜單辨識各用哪個 provider(claude/gemini)和模型(haiku/sonnet/opus)。`config.json` 設定管理員密碼和伺服器埠口。

---

## 啟動方式

`uv sync` 安裝依賴，`uv run uvicorn main:socket_app --reload --port 8098` 啟動。需設定 ANTHROPIC_API_KEY 環境變數供 Claude CLI 使用。

---

## 程式碼組織

`main.py` 是 FastAPI 入口，定義路由和 Socket.IO 事件。`app/ai.py` 處理 AI 整合。`app/data.py` 處理所有 JSON 檔案讀寫。`app/providers/` 封裝 CLI 差異。`templates/` 放三個 HTML 頁面。`static/` 放 CSS 和圖片。

---

## 本質總結

這是一個「對話即操作」的系統：使用者說話 → AI 理解意圖 → 產生動作 → 系統執行 → 即時廣播。所有狀態存 JSON 檔案，三個頁面共享同一份資料，透過 Socket.IO 保持同步。核心價值是讓訂餐從「填表單」變成「聊天」。
