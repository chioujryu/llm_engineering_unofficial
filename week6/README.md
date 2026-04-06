# Week 6：「The Price Is Right」專案導覽

本週實作一個 **依商品文字描述預測價格** 的模型，資料來自 [McAuley-Lab/Amazon-Reviews-2023](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023) 的產品 metadata。下方依 notebook 說明各日可學到的內容；實作程式多數在 `pricer/` 目錄。

---

## `day1.ipynb` — 資料整理（Data Curation）

- **專題定位**：為何「資料品質」與探索式分析（EDA）會直接影響後續模型表現。
- **Hugging Face**：使用 `datasets` 載入子資料集（如 `raw_meta_Appliances`）、`HF_TOKEN` 與 `login`。
- **解析管線**：`parse()` 將原始欄位清洗、合併為 `Item.full`，並依價格與長度篩選；`Item`（Pydantic）作為標準資料結構。
- **單一類別探索**：價格分佈直方圖、`Item` 欄位與 `full` 長度分析。
- **多類別載入**：`ItemLoader` 從 Hub 平行載入多個 `raw_meta_{category}`，合併為單一列表。
- **去重**：對 `title` 與 `full` 以可重現亂數順序做不重複篩選。
- **加權抽樣**：依價格（平方加權）與類別權重調整，抽出固定大小子樣本（例如 82 萬筆）供後續使用。
- **視覺化**：各類別筆數長條圖、文字長度 vs 價格散佈圖（檢查簡單相關性）。
- **（選用）**：將 train / validation / test 以 `Item.push_to_hub()` 推到自己的 Hugging Face Hub。

---

## `day2.ipynb` — 資料前處理（Data Pre-processing）

- **目標**：用 LLM 把冗長原始描述 **改寫成固定格式** 的簡短摘要（`Item.summary`），利於後續傳統 ML 與 API。
- **資料來源**：`LITE_MODE` 切換輕量（約 2 萬筆）與完整（約 80 萬筆）的 **預處理結果**；可直接從 Hub `Item.from_hub()` 載入，無需自費跑批次。
- **提示設計**：`SYSTEM_PROMPT` 要求 Title / Category / Brand / Description / Details 等結構化輸出。
- **單筆呼叫**：LiteLLM `completion`（如 Groq、Ollama）試跑單一商品，觀察 token 與成本。
- **批次 API**：建構 JSONL（每行一筆 chat completion 請求）、上傳、建立 **Groq Batch**、輪詢完成、下載結果，並依 `custom_id` 寫回 `items[id].summary`。
- **`Batch` 類別**：封裝「每 1000 筆一組、建立／執行／取回批次」的流程。
- **資料切分**：區分 train / validation / test，並可 `Item.push_to_hub()` 發布 `items_lite` / `items_full` 等資料集。

---

## `day3.ipynb` — 評估、基線與傳統機器學習

- **資料**：從 Hub 載入已含 `summary` 的 `items_lite` 或 `items_full`。
- **評估框架**：`pricer.evaluator.evaluate()` 對「價格預測函式」在測試集上算誤差（與課程定義的指標一致）。
- **愚蠢基線**：隨機價格、**訓練集平均價**（constant pricer），建立「再差也不能比這差」的下限參考。
- **表格特徵**：`weight`、`weight_unknown`、`len(summary)` 等 → **線性迴歸**（含係數解讀、MSE、R²）。
- **文字袋模型**：`CountVectorizer` 將 `summary` 轉為詞頻稀疏矩陣 → **線性迴歸**（自然語言線性模型）。
- **樹模型**：`RandomForestRegressor`（可選子集加速）、**XGBoost**（可選，梯度提升；環境需裝好 `xgboost`／部分系統需 `libomp`）。
- **心得**：傳統 ML 在結構化＋稀疏文字特徵上仍可有實務級表現，適合對照後續深度學習與 LLM。

---

## `day4.ipynb` — 神經網路與大型語言模型（推理）

- **人類基線**：將測試集摘要匯出 CSV，人工填價格後讀回，評估「人類在測試集上的表現」作為對照。
- **PyTorch 前馈網路**：`HashingVectorizer`（固定維度、適合大資料）將 `summary` 向量化 → 多層 MLP（ReLU）→ MSE、`Adam`、簡單 train/val 迴圈 → 自訂 `neural_network(item)` 再送 `evaluate`。
- **Frontier LLM（零樣本）**：不透過本資料集訓練，只用 **LiteLLM** 呼叫雲端模型（如 GPT-4.1-nano、Claude、Gemini 等），依 `summary` 估價並評估。
- **定位**：從傳統 ML → 小型神經網路 → 通用大模型推理，理解能力階梯與成本／延遲取捨。

---

## `day5.ipynb` — 微調前沿模型（Fine-tuning）

- **目標**：用 **OpenAI Fine-tuning API** 在既有小模型（如 `gpt-4.1-nano`）上微調出專用「估價」模型。
- **資料量**：教材建議可從極小（約 50–100 筆、成本低）到較大子集；以 **JSONL** 格式準備多輪對話（user：商品摘要＋指令，assistant：價格字串）。
- **流程**：撰寫 `make_jsonl` / `write_jsonl` → `openai.files.create` 上傳訓練與驗證檔 → `fine_tuning.jobs.create`（模型、epoch、batch 等超參數）→ 查詢 job 狀態與事件。
- **使用微調模型**：取得 `fine_tuned_model` 名稱後，以 `openai.chat.completions.create` 對測試集估價，再 `evaluate` 與 Day 4 零樣本結果比較。

---

## 建議閱讀順序

依檔名 **Day 1 → Day 5** 與資料管線一致：先整理與抽樣 → 可選 LLM 改寫與上架 → 基線與傳統 ML → 神經網路與現成 LLM → 微調專用模型。

若你只打算 **跟跑課程、不自行跑昂貴批次**，Day 2 可改為直接 `Item.from_hub()` 載入教學用已處理資料，再從 Day 3 開始。
