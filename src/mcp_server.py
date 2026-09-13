"""
🔌 MODEL CONTEXT PROTOCOL (MCP) SERVER MODULE
Mô phỏng kiến trúc MCP Server (Client-Server Architecture) cung cấp công cụ chuẩn hóa.
"""

import json
import os
import sys
from typing import Dict, Any, List
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from tools import TOOLS_SCHEMA, dispatch_tool_call
except ModuleNotFoundError:
    from src.tools import TOOLS_SCHEMA, dispatch_tool_call

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class MCPCocktailServer:
    """
    Giả lập MCP Server tuân thủ chuẩn giao thức Model Context Protocol
    """
    def __init__(self, server_name: str = "cocktail-mocktail-mcp-server"):
        self.server_name = "cocktail-mocktail-mcp-server"
        self.version = "2026.1.0"
        
    def list_tools(self) -> List[Dict[str, Any]]:
        """Trả về danh sách các Tools chuẩn giao thức MCP"""
        return TOOLS_SCHEMA
        
    def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        content = dispatch_tool_call(
            tool_name,
            arguments
        )

        result = json.loads(content)

        return {
            "jsonrpc": "2.0",
            "server": self.server_name,
            "tool": tool_name,
            "result": result
        }


# Tương thích ngược với các module khác
MCPAcademicServer = MCPCocktailServer


if __name__ == "__main__":
    print("==========================================================")
    print("🔌 KIỂM THỬ ĐỘC LẬP MCP SERVER (cocktail-mocktail-mcp-server)")
    print("==========================================================")
    
    server = MCPCocktailServer()
    tools = server.list_tools()
    print(f"✅ Khởi tạo thành công MCP Server: {server.server_name} (Version: {server.version})")
    print(f"📦 Số lượng Tools công bố: {len(tools)}")
    
    # Kiểm tra trạng thái TODO 1.2 (Tool Schema)
    test_tool = next((t for t in tools if t.get("name") in ["recipe_search", "save_recipe"]), None)
    if test_tool and not test_tool.get("parameters", {}).get("properties"):
        print("⏳ [TODO 1.2]: Tool chưa được định nghĩa properties trong 'src/tools.py'.")
    else:
        print(f"✅ [TODO 1.2]: Tool '{test_tool.get('name') if test_tool else ''}' đã có schema đầy đủ.")

    # Kiểm tra trạng thái TODO 2.1 (call_tool)
    test_result = server.call_tool("recipe_search", {"drink_name": "Mojito"})
    if not test_result:
        print("⏳ [TODO 2.1]: Hàm call_tool() đang trả về rỗng. Học viên hãy hoàn thiện TODO 2.1 trong 'src/mcp_server.py'!")
    else:
        print(f"✅ [TODO 2.1]: Test dispatch tool 'recipe_search' thành công:")
        print(f"   Phản hồi JSON-RPC: {json.dumps(test_result, ensure_ascii=False)}")
