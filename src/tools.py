"""
🍸 Cocktail & Mocktail Tools

Tools:
1. recipe_search
2. save_recipe
"""

import json
from typing import Dict, Any


# ============================================================
# TOOL SCHEMAS
# ============================================================

TOOLS_SCHEMA = [

    {
        "name": "recipe_search",
        "description": (
            "Tra cứu công thức Cocktail hoặc Mocktail "
            "theo tên đồ uống, loại đồ uống hoặc nguyên liệu."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "drink_name": {
                    "type": "string",
                    "description": (
                        "Tên đồ uống cần tìm, "
                        "ví dụ Mojito hoặc Margarita."
                    )
                },
                "category": {
                    "type": "string",
                    "description": (
                        "Loại đồ uống: Cocktail hoặc Mocktail."
                    )
                },
                "ingredient": {
                    "type": "string",
                    "description": (
                        "Nguyên liệu muốn dùng để tìm công thức."
                    )
                }
            },
            "required": []
        }
    },

    {
        "name": "save_recipe",
        "description": (
            "Lưu công thức Cocktail hoặc Mocktail "
            "đã tìm thấy vào danh sách yêu thích."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "drink_name": {
                    "type": "string",
                    "description": (
                        "Tên đồ uống cần lưu."
                    )
                }
            },
            "required": ["drink_name"]
        }
    }
]


# ============================================================
# RECIPE DATABASE
# ============================================================

RECIPE_DATABASE = {

    "mojito": {
        "drink_name": "Mojito",
        "category": "Cocktail",
        "ingredients": [
            "50ml white rum",
            "25ml fresh lime juice",
            "20ml sugar syrup",
            "8-10 mint leaves",
            "Soda water",
            "Ice"
        ],
        "instructions": [
            "Cho bạc hà và sugar syrup vào ly.",
            "Thêm nước cốt chanh.",
            "Dầm nhẹ bạc hà.",
            "Thêm đá.",
            "Thêm white rum.",
            "Top soda.",
            "Khuấy nhẹ."
        ]
    },

    "virgin mojito": {
        "drink_name": "Virgin Mojito",
        "category": "Mocktail",
        "ingredients": [
            "30ml fresh lime juice",
            "20ml sugar syrup",
            "8-10 mint leaves",
            "Soda water",
            "Ice"
        ],
        "instructions": [
            "Cho bạc hà và syrup vào ly.",
            "Thêm nước cốt chanh.",
            "Dầm nhẹ.",
            "Thêm đá.",
            "Top soda.",
            "Khuấy nhẹ."
        ]
    },

    "margarita": {
        "drink_name": "Margarita",
        "category": "Cocktail",
        "ingredients": [
            "50ml tequila",
            "25ml triple sec",
            "25ml fresh lime juice",
            "Ice",
            "Salt"
        ],
        "instructions": [
            "Làm ướt miệng ly bằng lime.",
            "Nhúng miệng ly vào muối.",
            "Cho tequila, triple sec và lime juice vào shaker.",
            "Thêm đá.",
            "Shake mạnh.",
            "Strain vào ly."
        ]
    },

    "shirley temple": {
        "drink_name": "Shirley Temple",
        "category": "Mocktail",
        "ingredients": [
            "Ginger ale",
            "Grenadine",
            "Lime juice",
            "Ice",
            "Maraschino cherry"
        ],
        "instructions": [
            "Cho đá vào ly.",
            "Thêm ginger ale.",
            "Thêm grenadine.",
            "Thêm lime juice.",
            "Khuấy nhẹ.",
            "Trang trí bằng cherry."
        ]
    },

    "pina colada": {
        "drink_name": "Piña Colada",
        "category": "Cocktail",
        "ingredients": [
            "50ml white rum",
            "50ml coconut cream",
            "100ml pineapple juice",
            "Ice"
        ],
        "instructions": [
            "Cho nguyên liệu vào blender.",
            "Thêm đá.",
            "Blend đến khi mịn.",
            "Rót ra ly."
        ]
    },

    "virgin pina colada": {
        "drink_name": "Virgin Piña Colada",
        "category": "Mocktail",
        "ingredients": [
            "100ml pineapple juice (nước dứa)",
            "50ml coconut cream (nước cốt dừa)",
            "20ml sugar syrup",
            "Ice"
        ],
        "instructions": [
            "Cho nước dứa, nước cốt dừa và siro vào máy xay (blender).",
            "Thêm đá viên.",
            "Xay nhuyễn mịn.",
            "Rót ra ly và trang trí lát dứa."
        ]
    },

    "cinderella": {
        "drink_name": "Cinderella",
        "category": "Mocktail",
        "ingredients": [
            "50ml orange juice (nước cam)",
            "50ml pineapple juice (nước dứa)",
            "20ml fresh lemon juice (nước chanh)",
            "10ml grenadine syrup",
            "Soda water",
            "Ice"
        ],
        "instructions": [
            "Cho nước cam, dứa, chanh và grenadine vào shaker.",
            "Thêm đá và lắc đều tay.",
            "Rót ra ly có sẵn đá.",
            "Top soda lên trên cùng và thưởng thức."
        ]
    },

    "sunrise mocktail": {
        "drink_name": "Sunrise Mocktail",
        "category": "Mocktail",
        "ingredients": [
            "120ml orange juice (nước cam tươi)",
            "20ml grenadine syrup",
            "Soda water",
            "Ice",
            "Lát cam tươi trang trí"
        ],
        "instructions": [
            "Cho đá viên vào ly cao.",
            "Rót nước cam tươi vào ly.",
            "Rót từ từ siro grenadine theo thành ly để tạo hiệu ứng phân tầng hoàng hôn.",
            "Top nhẹ một lớp soda và trang trí lát cam tươi."
        ]
    }
}


# ============================================================
# SAVED RECIPES
# ============================================================

SAVED_RECIPES = []


# ============================================================
# TOOL 1: SEARCH
# ============================================================

def execute_recipe_search(
    drink_name: str = "",
    category: str = "",
    ingredient: str = ""
) -> str:

    drink_name = drink_name.strip().lower()
    category = category.strip().lower()
    ingredient = ingredient.strip().lower()

    # Search by exact name
    if drink_name:

        recipe = RECIPE_DATABASE.get(drink_name)

        if recipe:
            return json.dumps({
                "status": "SUCCESS",
                "data": recipe
            }, ensure_ascii=False)

    # Search by category / ingredient if provided
    matches = []

    if category or ingredient:
        for recipe in RECIPE_DATABASE.values():

            if category:
                if recipe["category"].lower() != category:
                    continue

            if ingredient:
                # Hỗ trợ cả tiếng Việt và tiếng Anh cho nguyên liệu phổ biến
                synonyms = [ingredient]
                if "bạc hà" in ingredient:
                    synonyms.append("mint")
                elif "chanh" in ingredient:
                    synonyms.append("lime")
                    synonyms.append("lemon")

                ingredient_found = any(
                    any(syn in item.lower() for syn in synonyms)
                    for item in recipe["ingredients"]
                )

                if not ingredient_found:
                    continue

            matches.append(recipe)

    if matches:

        return json.dumps({
            "status": "SUCCESS",
            "count": len(matches),
            "data": matches
        }, ensure_ascii=False)

    return json.dumps({
        "status": "NOT_FOUND",
        "message": "Không tìm thấy công thức phù hợp."
    }, ensure_ascii=False)


# ============================================================
# TOOL 2: SAVE
# ============================================================

def execute_save_recipe(drink_name: str) -> str:

    key = drink_name.strip().lower()

    recipe = RECIPE_DATABASE.get(key)

    if not recipe:

        return json.dumps({
            "status": "NOT_FOUND",
            "message": (
                f"Không thể lưu '{drink_name}' "
                "vì công thức không tồn tại."
            )
        }, ensure_ascii=False)

    if recipe["drink_name"] not in SAVED_RECIPES:

        SAVED_RECIPES.append(
            recipe["drink_name"]
        )

    return json.dumps({
        "status": "SUCCESS",
        "message": (
            f"Đã lưu {recipe['drink_name']} "
            "vào danh sách yêu thích."
        ),
        "drink_name": recipe["drink_name"]
    }, ensure_ascii=False)


# ============================================================
# TOOL ROUTER
# ============================================================

TOOL_ROUTER = {
    "recipe_search": execute_recipe_search,
    "save_recipe": execute_save_recipe
}


def dispatch_tool_call(
    tool_name: str,
    arguments: Dict[str, Any]
) -> str:

    if tool_name not in TOOL_ROUTER:

        return json.dumps({
            "status": "UNKNOWN_TOOL",
            "error": f"Tool '{tool_name}' không tồn tại."
        }, ensure_ascii=False)

    try:

        return TOOL_ROUTER[tool_name](**arguments)

    except Exception as e:

        return json.dumps({
            "status": "EXECUTION_ERROR",
            "error": str(e)
        }, ensure_ascii=False)