# Week 7：開源模型微調（QLoRA / Llama）導覽

本週延續 Week 6 的 **「The Price Is Right」** 估價專題，改為在 **本機或 Colab GPU** 上 **微調開源語言模型**（課程主軸為 **Llama 3.2** 與 **QLoRA**），與 Week 6 使用 OpenAI API 微調封閉模型的路線互相對照。

> **檔名說明**：本週沒有獨立的 `day3.ipynb` / `day4.ipynb`，訓練兩階段合併在 **`day3 and 4.ipynb`**（內容為連到 Colab 的導引）。

---

## `day1.ipynb` — QLoRA 概念（Day 1）

- **主題**：什麼是 **QLoRA**（量化＋ LoRA 低秩調適），以及為何在消費級／單卡 GPU 上仍能微調大型模型。
- **本機 notebook**：以週次大綱與 **Google Colab 連結** 為主，實際動畫與說明多在 Colab 完成。
- **可學重點**：理解「全參數微調 vs 參數高效微調（PEFT）」、量化對記憶體的影響，以及本週後續 Day 2～5 在管線中的位置。

---

## `day2.ipynb` — 提示資料與基底模型（Day 2：Prompt Data & Base Model）

- **資料來源**：自 Hugging Face 載入 Week 6 已處理好的 `items_lite` / `items_full`（`Item.from_hub`），含 `summary` 與價格等欄位。
- **基底模型與分詞**：使用 **`meta-llama/Llama-3.2-3B`** 與 `AutoTokenizer`，分析 **`summary` 的 token 數分佈**（直方圖、平均與最大值）。
- **截斷策略**：設定 **`CUTOFF`**（例如 110 tokens），評估若截斷過長摘要會影響多少筆資料，以在 **上下文長度** 與 **資料保留** 之間取捨。
- **監督式微調格式**：對 train/validation/test 呼叫 **`Item.make_prompts(tokenizer, CUTOFF, do_round)`**，產生因果式 LM 用的 **`prompt`**（問題＋截斷後摘要＋價格前綴）與 **`completion`**（價格字串）；test 與 train/val 在 `do_round` 上可區分格式需求。
- **整段序列長度**：統計 **prompt＋completion** 的 token 數，確認適合餵給訓練流程。
- **上架資料集**：使用 **`Item.push_prompts_to_hub()`** 將 `prompt` / `completion` 欄位推到 Hub（如 `items_prompts_lite`、`items_prompts_full`），供 Colab 訓練直接 `load_dataset`。
- **延伸**：notebook 末尾提供 **Colab 連結**，接續基底模型載入與訓練環境。

相關實作可對照本目錄 `pricer/items.py` 中的 `count_tokens`、`make_prompts`、`to_datapoint`、`push_prompts_to_hub`。

---

## `day3 and 4.ipynb` — 訓練 Part 1 與 Part 2（Day 3 & 4）

- **形式**：以 **Google Colab 連結** 為主（本地僅標題與連結），對應課程大綱的 **Train Part 1** 與 **Train Part 2**。
- **典型會涵蓋的內容**（依 Colab 實作為準）：
  - 載入 **4-bit 量化** 的 Llama 與 **PEFT/LoRA** 設定（即 QLoRA 管線）。
  - 載入 **`items_prompts_*`** 類資料集，對齊 tokenizer 與 **SFT（監督式微調）** 資料格式。
  - **訓練迴圈**：loss、learning rate、epochs、儲存 **checkpoint**、可選 **W&B** 或 Colab 內建紀錄。
  - **Part 2** 常接續：較長訓練、除錯、合併 adapter 或匯出供推論用的模型等（以該週 Colab 儲格為準）。
- **可學重點**：在真實 GPU 預算下完成一輪 **開源 LLM 估價任務** 的端到端訓練，並熟悉 Hugging Face / PEFT 生態。

---

## `day5.ipynb` — 評估（Day 5：Eval）

- **形式**：同樣以 **Google Colab 連結** 為主。
- **可學重點**：載入 **微調後** 模型（或 adapter＋基底），在 **測試集** 上對 `summary`（或與訓練一致的 prompt）做 **推理**，並用與 Week 6 相同的 **`pricer.evaluator.evaluate`** 概念比較 **平均誤差**。
- **對照**：可與 Week 6 的 API 微調、傳統 ML、零樣本大模型等結果比較，理解「開源 QLoRA」在成本與效果上的取捨。

---

## 選讀：`results.ipynb`

- 以 **Plotly** 長條圖彙整專題中多種方法（常數基線、傳統 ML、神經網路、各家 LLM、API 微調、**Llama 基底與 fine-tuned lite/full** 等）的 **預測誤差**，方便一眼比較整條 capstone 的演進。

---

## 建議學習順序

1. **Day 1**：建立 QLoRA／PEFT 背景知識（Colab）。  
2. **Day 2**：在本機完成 **token 分析 → prompt/completion 建構 → 推上 Hub**（Colab 前唯一較長的本地 notebook）。  
3. **Day 3 & 4**：依 `day3 and 4.ipynb` 的 Colab 分兩段跑完訓練。  
4. **Day 5**：Colab 上做微調模型評估，並與 Week 6 結果對照。

**環境提示**：Day 2 需要 `HF_TOKEN`、可選的 Llama 權限與足夠磁碟以下載 tokenizer／資料；訓練與評估主要依賴 Colab GPU，請一併準備 Colab 與（若需要）W&B 等帳號。
