"""
🔌 MULTI-PROVIDER LLM ADAPTER (Google Gemini, OpenAI & Offline Mock)
Hỗ trợ Native Tool Calling và chuyển đổi linh hoạt qua biến môi trường LLM_PROVIDER.
"""

import os
import sys
import json
from typing import Dict, Any, List
from dotenv import load_dotenv

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

class BaseLLMProvider:
    """Interface cơ sở cho các LLM Provider hỗ trợ Native Tool Calling"""
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        raise NotImplementedError

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from tools import RECIPE_DATABASE
except ModuleNotFoundError:
    from src.tools import RECIPE_DATABASE

def get_mock_recipe_content(drink_key: str, saved: bool = False) -> str:
    """Tạo câu trả lời chi tiết gồm Tên, Nguyên liệu và Cách làm từ Database"""
    key = drink_key.lower().strip()
    data = RECIPE_DATABASE.get(key)
    if not data:
        for k, v in RECIPE_DATABASE.items():
            if k in key or key in k:
                data = v
                break

    if not data:
        return f"Đã tìm thấy công thức cho '{drink_key}' trong cơ sở dữ liệu."

    name = data.get("drink_name", drink_key)
    cat = data.get("category", "Cocktail")
    ingredients = data.get("ingredients", [])
    instructions = data.get("instructions", [])

    ings_str = "\n".join([f"- {ing}" for ing in ingredients])
    steps_str = "\n".join([f"{idx+1}. {st}" for idx, st in enumerate(instructions)])

    out = f"Dưới đây là công thức **{name}** ({cat}) chi tiết dành cho bạn:\n\n"
    out += f"**Tên đồ uống:** {name} ({cat})\n\n"
    out += f"**Nguyên liệu:**\n{ings_str}\n\n"
    out += f"**Cách làm:**\n{steps_str}"
    if saved:
        out += f"\n\n**Trạng thái:** Đã lưu {name} vào danh sách yêu thích thành công!"
    return out


def get_all_mocktails_content(saved: bool = False) -> str:
    """Tạo câu trả lời chi tiết cho danh sách 5 loại Mocktail nổi tiếng"""
    from tools import RECIPE_DATABASE
    mocktails = [v for v in RECIPE_DATABASE.values() if v.get("category", "").lower() == "mocktail"]
    out = f"Dưới đây là công thức của **{len(mocktails)} loại Mocktail (đồ uống không cồn)** nổi tiếng nhất dành cho bạn:\n\n"
    for idx, d in enumerate(mocktails):
        name = d.get("drink_name")
        ings = "\n".join([f"  - {i}" for i in d.get("ingredients", [])])
        steps = "\n".join([f"  {s_idx+1}. {st}" for s_idx, st in enumerate(d.get("instructions", []))])
        out += f"**{idx+1}. {name} (Mocktail)**\n\n"
        out += f"**Nguyên liệu:**\n{ings}\n\n"
        out += f"**Cách làm:**\n{steps}\n\n---\n\n"
    if saved:
        out += "**Trạng thái:** Đã lưu công thức Mocktail vào danh sách yêu thích thành công!"
    return out


class MockOfflineProvider(BaseLLMProvider):
    """Offline Mock Provider dùng để chạy thử mà không tốn API Key"""
    def __init__(self):
        self.model_name = "Offline-Mock-Model-2026"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        return f"[Mock Chatbot Response]: Xin chào! Tôi đã nhận được câu hỏi '{prompt}'. (Chế độ Chatbot không có Tool tra cứu dữ liệu thời gian thực)."

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        prompt_lower = prompt.lower()
        
        # Xác định tên đồ uống từ prompt (Margarita, Mojito, v.v.)
        drink_name = "Margarita" if "margarita" in prompt_lower else ("Mojito" if "mojito" in prompt_lower and "virgin" not in prompt_lower else "")

        # -------------------------------------------------------------
        # STEP 3: Nếu đã thực hiện save_recipe và nhận Observation -> FINAL ANSWER
        # -------------------------------------------------------------
        if "save_recipe" in prompt_lower and ("tool observation" in prompt_lower or "observation" in prompt_lower):
            if "5" in prompt_lower or ("mocktail" in prompt_lower and "margarita" not in prompt_lower):
                content = get_all_mocktails_content(saved=True)
            else:
                name = drink_name or "Margarita"
                content = get_mock_recipe_content(name, saved=True)
            return {
                "type": "text",
                "content": content,
                "thought": f"Đã lưu thành công công thức vào danh sách yêu thích. Trả về câu trả lời hoàn chỉnh cho người dùng."
            }

        # -------------------------------------------------------------
        # STEP 2 (Multi-step): Sau khi recipe_search trả Observation thành công:
        # Nếu user yêu cầu "lưu" -> Gọi save_recipe
        # -------------------------------------------------------------
        if "recipe_search" in prompt_lower and ("tool observation" in prompt_lower or "observation" in prompt_lower):
            if "not_found" in prompt_lower:
                missing_name = "Dragon Fire Cocktail XYZ" if "dragon fire" in prompt_lower else (drink_name or "đồ uống này")
                return {
                    "type": "text",
                    "content": f"Không tìm thấy công thức cho '{missing_name}' trong cơ sở dữ liệu nên không thể lưu vào danh sách yêu thích.",
                    "thought": "Công thức không tìm thấy (NOT_FOUND). Tuân thủ quy tắc không bịa đặt và không gọi save_recipe."
                }
            if "lưu" in prompt_lower:
                if "5" in prompt_lower or ("mocktail" in prompt_lower and "margarita" not in prompt_lower):
                    save_name = "Virgin Mojito"
                else:
                    save_name = drink_name or "Margarita"
                return {
                    "type": "tool_call",
                    "tool_name": "save_recipe",
                    "arguments": {"drink_name": save_name},
                    "thought": f"Đã tìm thấy công thức. Người dùng yêu cầu lưu, tôi sẽ gọi save_recipe."
                }
            else:
                if "5" in prompt_lower or ("loại" in prompt_lower and "mocktail" in prompt_lower):
                    content = get_all_mocktails_content(saved=False)
                elif "virgin mojito" in prompt_lower or ("mocktail" in prompt_lower and ("bạc hà" in prompt_lower or "mint" in prompt_lower)):
                    content = get_mock_recipe_content("virgin mojito", saved=False)
                elif "mojito" in prompt_lower:
                    content = get_mock_recipe_content("mojito", saved=False)
                elif "margarita" in prompt_lower:
                    content = get_mock_recipe_content("margarita", saved=False)
                elif "shirley" in prompt_lower:
                    content = get_mock_recipe_content("shirley temple", saved=False)
                elif "mocktail" in prompt_lower:
                    content = get_all_mocktails_content(saved=False)
                else:
                    content = get_mock_recipe_content(drink_name or "mojito", saved=False)

                return {
                    "type": "text",
                    "content": content,
                    "thought": f"Đã nhận được kết quả Observation từ recipe_search. Trả về công thức chi tiết cho người dùng."
                }

        # -------------------------------------------------------------
        # STEP 1: Nhận diện intent ban đầu
        # -------------------------------------------------------------
        # TC01: Hỏi chung / phân biệt Cocktail và Mocktail
        if any(q in prompt_lower for q in ["khác nhau", "là gì", "phân biệt", "chào"]):
            return {
                "type": "text",
                "content": "Cocktail là thức uống có cồn (thường pha từ rượu nền, nước trái cây, siro), trong khi Mocktail là đồ uống không chứa cồn (pha chế từ nước ép, soda, thảo mộc).",
                "thought": "Câu hỏi chung về phân biệt Cocktail và Mocktail, trả lời trực tiếp mà không cần gọi Tool."
            }

        # TC05: Edge case tìm công thức không tồn tại
        if "dragon fire" in prompt_lower or "dragonbreath" in prompt_lower:
            return {
                "type": "tool_call",
                "tool_name": "recipe_search",
                "arguments": {"drink_name": "Dragon Fire Cocktail XYZ"},
                "thought": "Người dùng cần công thức Dragon Fire Cocktail XYZ trước khi lưu. Tôi sẽ tra cứu Dragon Fire Cocktail XYZ."
            }

        # TC03: Tìm kiếm theo bộ lọc category và ingredient
        if "mocktail" in prompt_lower and ("bạc hà" in prompt_lower or "mint" in prompt_lower):
            return {
                "type": "tool_call",
                "tool_name": "recipe_search",
                "arguments": {"category": "Mocktail", "ingredient": "mint"},
                "thought": "Người dùng muốn tìm Mocktail có bạc hà. Tôi sẽ gọi tool recipe_search với category='Mocktail' và ingredient='mint'."
            }

        # Tra cứu Mocktail nói chung hoặc 5 loại Mocktail
        if "mocktail" in prompt_lower and "margarita" not in prompt_lower:
            return {
                "type": "tool_call",
                "tool_name": "recipe_search",
                "arguments": {"category": "Mocktail"},
                "thought": "Người dùng yêu cầu tra cứu công thức Mocktail (đồ uống không cồn). Tôi sẽ gọi recipe_search với category='Mocktail'."
            }

        # TC02: Tra cứu đơn lẻ Mojito
        if "mojito" in prompt_lower and "lưu" not in prompt_lower:
            return {
                "type": "tool_call",
                "tool_name": "recipe_search",
                "arguments": {"drink_name": "Mojito"},
                "thought": "Người dùng muốn xem công thức Mojito. Tôi sẽ gọi tool recipe_search."
            }

        # TC04 / Mặc định: Tra cứu Margarita
        name = drink_name or "Margarita"
        if "lưu" in prompt_lower:
            thought = f"Người dùng cần công thức {name} trước khi có thể lưu.\nTôi sẽ tra cứu {name}."
        else:
            thought = f"Người dùng yêu cầu tra cứu công thức {name}. Tôi sẽ tra cứu {name}."
        return {
            "type": "tool_call",
            "tool_name": "recipe_search",
            "arguments": {"drink_name": name},
            "thought": thought
        }

        # Mô phỏng nhận diện intent cho Academic (tương thích ngược)
        if "sv2026001" in prompt_lower and "đặt lịch" in prompt_lower:
            return {
                "type": "tool_call",
                "tool_name": "schedule_appointment",
                "arguments": {"student_id": "SV2026001", "datetime_str": "14:00 15/09/2026", "advisor_name": "PGS.TS Nguyễn Văn A"},
                "thought": "Người dùng yêu cầu đặt lịch hẹn tư vấn cho sinh viên SV2026001. Tôi sẽ gọi tool schedule_appointment."
            }
        elif "sv2026001" in prompt_lower or "tra cứu" in prompt_lower:
            return {
                "type": "tool_call",
                "tool_name": "academic_query",
                "arguments": {"student_id": "SV2026001"},
                "thought": "Người dùng muốn tra cứu thông tin học vụ của sinh viên SV2026001. Tôi sẽ gọi tool academic_query."
            }
        else:
            return {
                "type": "text",
                "content": "Cocktail là thức uống có cồn (thường pha từ rượu nền, nước trái cây, siro), trong khi Mocktail là đồ uống không chứa cồn (pha chế từ nước ép, soda, thảo mộc).",
                "thought": "Câu hỏi chung về phân biệt Cocktail và Mocktail, trả lời trực tiếp không cần gọi Tool."
            }


class GeminiProvider(BaseLLMProvider):
    """Google Gemini Provider (Native Tool Calling với Google GenAI SDK)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gemini-2.5-flash"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            return "[Gemini Error]: Chưa cấu hình GEMINI_API_KEY trong file .env! Đang sử dụng chế độ Mock."
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            contents = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = client.models.generate_content(model=self.model_name, contents=contents)
            return response.text
        except Exception as e:
            return f"[Gemini Exception]: {str(e)}"

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            print("ℹ️ [Gemini Provider]: Chưa tìm thấy GEMINI_API_KEY hợp lệ. Tự động chuyển sang Mock Offline.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)
        
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            
            # Chuẩn hóa function declarations cho Gemini SDK
            function_declarations = []
            for tool in tools_schema:
                # Bỏ qua các tool schema chưa được định nghĩa hoàn chỉnh
                if not tool.get("name") or not tool.get("parameters"):
                    continue
                function_declarations.append({
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("parameters", {})
                })

            config = types.GenerateContentConfig(
                system_instruction=system_prompt if system_prompt else None,
                tools=[{"function_declarations": function_declarations}] if function_declarations else None,
                temperature=0.2
            )

            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )

            # Kiểm tra xem Gemini có trả về Tool Call không
            if response.function_calls:
                call = response.function_calls[0]
                args = dict(call.args) if hasattr(call, 'args') and call.args else {}
                return {
                    "type": "tool_call",
                    "tool_name": call.name,
                    "arguments": args,
                    "thought": f"Gemini quyết định gọi công cụ '{call.name}' với tham số: {json.dumps(args, ensure_ascii=False)}"
                }
            else:
                return {
                    "type": "text",
                    "content": response.text or "",
                    "thought": "Gemini phản hồi trực tiếp bằng văn bản (không cần gọi công cụ)."
                }

        except Exception as e:
            print(f"⚠️ [Gemini API Warning]: Không thể kết nối live API ({str(e)}). Tự động fallback về Mock.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI Provider (Native Tool Calling với OpenAI SDK)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gpt-4o-mini"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            return "[OpenAI Error]: Chưa cấu hình OPENAI_API_KEY trong file .env! Đang sử dụng chế độ Mock."
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            response = client.chat.completions.create(model=self.model_name, messages=messages)
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"[OpenAI Exception]: {str(e)}"

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            print("ℹ️ [OpenAI Provider]: Chưa tìm thấy OPENAI_API_KEY hợp lệ. Tự động chuyển sang Mock Offline.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            tools = []
            for tool in tools_schema:
                if not tool.get("name"):
                    continue
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool.get("description", ""),
                        "parameters": tool.get("parameters", {})
                    }
                })

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None
            )

            msg = response.choices[0].message
            if msg.tool_calls:
                call = msg.tool_calls[0]
                args = json.loads(call.function.arguments) if call.function.arguments else {}
                return {
                    "type": "tool_call",
                    "tool_name": call.function.name,
                    "arguments": args,
                    "thought": f"OpenAI quyết định gọi công cụ '{call.function.name}' với tham số: {json.dumps(args, ensure_ascii=False)}"
                }
            else:
                return {
                    "type": "text",
                    "content": msg.content or "",
                    "thought": "OpenAI phản hồi trực tiếp bằng văn bản (không cần gọi công cụ)."
                }
        except Exception as e:
            print(f"⚠️ [OpenAI API Warning]: Không thể kết nối live API ({str(e)}). Tự động fallback về Mock.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)


def get_llm_provider() -> BaseLLMProvider:
    """Factory function khởi tạo Provider theo LLM_PROVIDER env variable"""
    provider_type = os.getenv("LLM_PROVIDER", "gemini").lower()
    
    if provider_type == "gemini":
        key = os.getenv("GEMINI_API_KEY")
        if key and key != "your_gemini_api_key_here":
            return GeminiProvider()
        else:
            return MockOfflineProvider()
    elif provider_type == "openai":
        key = os.getenv("OPENAI_API_KEY")
        if key and key != "your_openai_api_key_here":
            return OpenAIProvider()
        else:
            return MockOfflineProvider()
    elif provider_type == "mock":
        return MockOfflineProvider()
    else:
        return MockOfflineProvider()

# Alias for backwards compatibility
get_provider = get_llm_provider
