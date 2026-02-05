# import json

# # 顏色配置：每個層級使用不同顏色
# COLORS = [
#     "\033[34m",  # 藍色 (第 0 層)
#     "\033[32m",  # 綠色 (第 1 層)
#     "\033[36m",  # 青色 (第 2 層)
#     "\033[35m",  # 紫色 (第 3 層)
#     "\033[33m",  # 黃色 (第 4 層)
# ]
# RESET = "\033[0m"


# def print_colored_json(data, level=0, indent=0):
#     """
#     遞迴列印 dict / list 結構，根據層級顯示不同顏色。
#     """
#     color = COLORS[level % len(COLORS)]
#     space = "  " * indent  # 縮排

#     if isinstance(data, dict):
#         for key, value in data.items():
#             print(f"{space}{color}{key}{RESET}:", end=" ")
#             if isinstance(value, (dict, list)):
#                 print()  # 換行顯示巢狀結構
#                 print_colored_json(value, level + 1, indent + 1)
#             else:
#                 print(repr(value))
#     elif isinstance(data, list):
#         for i, item in enumerate(data):
#             print(f"{space}{color}- [#{i}]{RESET}")
#             print_colored_json(item, level + 1, indent + 1)
#     else:
#         print(f"{space}{repr(data)}")


# def view_model_response(response):
#     """
#     階層式查看 response 的內容，key 以不同顏色顯示。
#     """
#     try:
#         # 嘗試轉成可遍歷的 dict
#         if hasattr(response, "model_dump_json"):
#             data = json.loads(response.model_dump_json())
#         elif hasattr(response, "to_dict"):
#             data = response.to_dict()
#         elif isinstance(response, (dict, list)):
#             data = response
#         else:
#             # 嘗試將字符串轉成 JSON
#             data = json.loads(str(response))
#     except Exception as e:
#         print("⚠️ 無法解析 response 為可用的字典結構：", e)
#         return

#     print_colored_json(data)


# # ==== 使用範例 ====
# # 直接呼叫即可
# # view_model_response(response.choices[0].message.content  )








import json
from typing import Any

# 顏色配置：每個層級使用不同顏色
COLORS = [
    "\033[34m",  # 藍色 (第 0 層)
    "\033[32m",  # 綠色 (第 1 層)
    "\033[36m",  # 青色 (第 2 層)
    "\033[35m",  # 紫色 (第 3 層)
    "\033[33m",  # 黃色 (第 4 層)
]
RESET = "\033[0m"


def is_result_object(obj: Any) -> bool:
    """檢查物件是否為 Result 物件"""
    return (
        hasattr(obj, 'page_content') and 
        hasattr(obj, 'metadata') and
        isinstance(obj.metadata, dict)
    )


def convert_result_to_dict(result_obj: Any) -> dict:
    """將 Result 物件轉換為字典"""
    return {
        "page_content": result_obj.page_content,
        "metadata": result_obj.metadata
    }


def print_colored_json(data, level=0, indent=0):
    """
    遞迴列印 dict / list 結構，根據層級顯示不同顏色。
    自動檢測並展開 Result 物件。
    """
    color = COLORS[level % len(COLORS)]
    space = "  " * indent  # 縮排
    
    # 檢查是否為 Result 物件
    if is_result_object(data):
        print(f"{space}{color}<Result Object>{RESET}")
        # 將 Result 物件轉換為字典並遞迴處理
        print_colored_json(convert_result_to_dict(data), level, indent + 1)
        return

    if isinstance(data, dict):
        for key, value in data.items():
            print(f"{space}{color}{key}{RESET}:", end=" ")
            if isinstance(value, (dict, list)):
                print()  # 換行顯示巢狀結構
                print_colored_json(value, level + 1, indent + 1)
            else:
                # 檢查 value 是否為 Result 物件
                if is_result_object(value):
                    print()
                    print_colored_json(value, level + 1, indent + 1)
                else:
                    print(repr(value))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            print(f"{space}{color}- [#{i}]{RESET}")
            print_colored_json(item, level + 1, indent + 1)
    else:
        # 基本型別
        print(f"{space}{repr(data)}")


def view_model_response(response):
    """
    階層式查看 response 的內容，key 以不同顏色顯示。
    自動處理 Result 物件。
    """
    try:
        # 如果 response 是列表且包含 Result 物件，直接處理
        if isinstance(response, list) and all(is_result_object(item) for item in response):
            print("📚 檢索到的結果 (Result 物件列表):")
            print_colored_json(response)
            return
            
        # 嘗試轉成可遍歷的 dict
        if hasattr(response, "model_dump_json"):
            data = json.loads(response.model_dump_json())
        elif hasattr(response, "to_dict"):
            data = response.to_dict()
        elif isinstance(response, (dict, list)):
            # 如果已經是 dict 或 list，先檢查是否包含 Result 物件
            data = response
        else:
            # 嘗試將字符串轉成 JSON
            data = json.loads(str(response))
    except Exception as e:
        print("⚠️ 無法解析 response 為可用的字典結構：", e)
        return

    print_colored_json(data)


# ==== 使用範例 ====
# 直接呼叫即可
# view_model_response(chunks)

# 也可用於其他包含 Result 物件的資料結構
# result_dict = {
#     "key1": result_obj1,
#     "key2": [result_obj2, result_obj3],
#     "key3": {"nested": result_obj4}
# }
# view_model_response(result_dict)