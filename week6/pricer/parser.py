from pricer.items import Item
import json
import re

MIN_CHARS = 600
MIN_PRICE = 0.5
MAX_PRICE = 999.49
MAX_TEXT_EACH = 3000
MAX_TEXT_TOTAL = 4000

REMOVALS = [
    "Part Number",
    "Best Sellers Rank",
    "Batteries Included?",
    "Batteries Required?",
    "Item model number",
]


def simplify(text_list) -> str:
    """
    Return a simplified string without too much whitespace and limited to MAX_TEXT characters
    """
    return (
        str(text_list)
        .replace("\n", " ")
        .replace("\r", "")
        .replace("\t", "")
        .replace("  ", " ")
        .strip()[:MAX_TEXT_EACH]
    )


def scrub(title, description, features, details) -> bool:
    """
    Return a cleansed full string with product numbers and unimportant details removed
    """
    for remove in REMOVALS:
        details.pop(remove, None)
    result = title + "\n"
    if description:
        result += simplify(description) + "\n"
    if features:
        result += simplify(features) + "\n"
    if details:
        result += json.dumps(details) + "\n"
    pattern = r"\b(?=[A-Z0-9]{7,}\b)(?=.*[A-Z])(?=.*\d)[A-Z0-9]+\b"
    return re.sub(pattern, "", result).strip()[:MAX_TEXT_TOTAL]


def get_weight(details):
    weight_str = details.get("Item Weight")
    if weight_str:
        parts = weight_str.split(" ")
        amount = float(parts[0])
        unit = parts[1].lower()
        if unit == "pounds":
            return amount
        elif unit == "ounces":
            return amount / 16
        elif unit == "grams":
            return amount / 453.592
        elif unit == "milligrams":
            return amount / 453592
        elif unit == "kilograms":
            return amount / 0.453592
        elif unit == "hundredths" and parts[2].lower() == "pounds":
            return amount / 100
    return 0


def parse(datapoint, category):
    """
    將單筆資料 datapoint 解析為 Item 物件。

    參數：
    - datapoint (dict): 一筆原始資料，應包含以下欄位：
        - "price": 商品價格（字串或數字）
        - "title": 商品標題
        - "description": 商品描述
        - "features": 商品特徵（通常是 list 或文字）
        - "details": JSON 字串，需可被 json.loads 解析
    - category (str): 商品類別名稱，例如 "Appliances"

    回傳：
    - Item: 若資料有效（價格在範圍內且文字長度足夠），回傳 Item 物件
    - None: 若資料不符合條件（例如價格轉換失敗或內容過短）

    使用範例：
    >>> item = parse(datapoint, "Appliances")
    >>> if item:
    ...     print(item.title, item.price)

    注意：
    - datapoint 必須是 dict，不能是字串或其他型別
    - datapoint["details"] 必須是合法 JSON 字串
    - 會使用外部變數 MIN_PRICE, MAX_PRICE, MIN_CHARS
    - 依賴函式 get_weight() 與 scrub()
    """
    try:
        price = float(datapoint["price"])
    except ValueError:
        return None
    if MIN_PRICE <= price <= MAX_PRICE:
        title = datapoint["title"]
        description = datapoint["description"]
        features = datapoint["features"]
        details = json.loads(datapoint["details"])
        weight = get_weight(details)
        full = scrub(title, description, features, details)
        if len(full) >= MIN_CHARS:
            return Item(
                title=title,
                category=category,
                price=price,
                full=full,
                weight=weight,
            )
