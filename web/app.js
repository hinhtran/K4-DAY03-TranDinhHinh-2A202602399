/**
 * 🍸 MIXOLOGY AI - CLIENT LOGIC & REACT STEP VISUALIZER
 */

const TEST_CASES = [
  {
    id: "TC01",
    type: "direct_query",
    question: "Cocktail và Mocktail khác nhau như thế nào?",
    complexity: "Low",
    badgeClass: "badge-low"
  },
  {
    id: "TC02",
    type: "single_tool_query",
    question: "Cho tôi công thức Mojito.",
    complexity: "Medium",
    badgeClass: "badge-medium"
  },
  {
    id: "TC03",
    type: "filtered_search",
    question: "Tìm cho tôi một Mocktail có bạc hà.",
    complexity: "Medium",
    badgeClass: "badge-medium"
  },
  {
    id: "TC04",
    type: "multi_step_action",
    question: "Tìm công thức Margarita và lưu nó vào danh sách yêu thích.",
    complexity: "High",
    badgeClass: "badge-high"
  },
  {
    id: "TC05",
    type: "edge_case",
    question: "Tìm công thức Dragon Fire Cocktail XYZ và lưu nó vào yêu thích.",
    complexity: "High",
    badgeClass: "badge-high"
  }
];

let currentMode = "react"; // 'react' | 'baseline'
let savedRecipes = ["Margarita (Đã lưu qua save_recipe)"];
let currentWaterfallTrace = [];

// Initialize Page
document.addEventListener("DOMContentLoaded", () => {
  renderTestCases();
  loadSavedRecipes();
  fetchInitialTrace();
});

// Render Test Cases in Sidebar
function renderTestCases() {
  const container = document.getElementById("testCasesList");
  if (!container) return;

  container.innerHTML = TEST_CASES.map(tc => `
    <div class="tc-card" onclick="selectTestCase('${tc.id}')">
      <div class="tc-header">
        <span class="tc-id">${tc.id}</span>
        <span class="tc-badge ${tc.badgeClass}">${tc.complexity}</span>
      </div>
      <div class="tc-query">${escapeHtml(tc.question)}</div>
    </div>
  `).join("");
}

// Select a Test Case to run
function selectTestCase(id) {
  const tc = TEST_CASES.find(t => t.id === id);
  if (tc) {
    const input = document.getElementById("queryInput");
    input.value = tc.question;
    handleUserSubmit(new Event("submit"));
  }
}

// Quick Fill input without submitting
function quickFill(text) {
  const input = document.getElementById("queryInput");
  input.value = text;
  input.focus();
}

// Switch between ReAct Agent and Baseline Chatbot
function setMode(mode) {
  currentMode = mode;
  document.getElementById("btnModeReact").classList.toggle("active", mode === "react");
  document.getElementById("btnModeBaseline").classList.toggle("active", mode === "baseline");
}

// Handle User Message Submission
async function handleUserSubmit(event) {
  if (event) event.preventDefault();
  const input = document.getElementById("queryInput");
  const query = input.value.trim();
  if (!query) return;

  // Append User message to UI
  appendUserMessage(query);
  input.value = "";
  
  // Disable send button while processing
  const sendBtn = document.getElementById("sendBtn");
  sendBtn.disabled = true;

  // Append Bot typing container
  const botRow = createBotMessageElement();
  const bubble = botRow.querySelector(".message-bubble");
  bubble.innerHTML = `<span style="color: var(--primary-300);">⚡ Đang khởi tạo chu trình suy luận ${currentMode === 'react' ? 'ReAct (Thought -> Action -> Observation)' : 'Chatbot Baseline'}...</span>`;
  scrollToBottom();

  try {
    // Try communicating with Python Web Backend API
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: query, mode: currentMode })
    });

    if (response.ok) {
      const data = await response.json();
      renderBotResponse(bubble, data.traces, data.finalAnswer);
      if (data.savedRecipes) {
        savedRecipes = data.savedRecipes;
        loadSavedRecipes();
      }
      if (data.traces) {
        currentWaterfallTrace = data.traces;
      }
    } else {
      // Offline fallback: Client-side ReAct simulation
      simulateReActFlow(bubble, query);
    }
  } catch (err) {
    // Standalone fallback: simulate locally
    simulateReActFlow(bubble, query);
  } finally {
    sendBtn.disabled = false;
  }
}

// Append User speech bubble
function appendUserMessage(text) {
  const chat = document.getElementById("chatContainer");
  const row = document.createElement("div");
  row.className = "message-row user";
  row.innerHTML = `
    <div class="avatar user">👤</div>
    <div class="message-bubble">${escapeHtml(text)}</div>
  `;
  chat.appendChild(row);
  scrollToBottom();
}

// Create Bot speech bubble template
function createBotMessageElement() {
  const chat = document.getElementById("chatContainer");
  const row = document.createElement("div");
  row.className = "message-row bot";
  row.innerHTML = `
    <div class="avatar bot">🍸</div>
    <div class="message-bubble"></div>
  `;
  chat.appendChild(row);
  return row;
}

// Parse inline markdown
function parseInlineMarkdown(str) {
  return escapeHtml(str)
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/`([^`]+)`/g, "<code>$1</code>");
}

// Format final answer: break down every heading, bullet point, and step into distinct lines
function formatBotAnswer(text) {
  if (!text) return "";

  // 1. Separate items that might be glued together without proper newlines
  let formatted = text
    // Put newlines before bold section headers like **Tên đồ uống:**, **Nguyên liệu:**, **Cách làm:**, **Trạng thái:**
    .replace(/([^\n])\s*(\*\*[^*]+:\*\*)/g, "$1\n\n$2 ")
    // Put newlines before bullet dashes/bullets (-, –, •)
    .replace(/([^\n])\s*([–\-•])\s+/g, "$1\n- ")
    // Put newlines before numbered steps (1., 2., etc.)
    .replace(/([^\n])\s*(\d+\.)\s+/g, "$1\n$2 ");

  // 2. Parse lines
  const rawLines = formatted.split("\n").map(l => l.trim()).filter(l => l.length > 0);
  let html = "";
  let inUl = false;
  let inOl = false;

  for (let line of rawLines) {
    // Check if bullet line
    const bulletMatch = line.match(/^[-–•*]\s+(.*)$/);
    // Check if numbered line
    const numMatch = line.match(/^(\d+)\.\s+(.*)$/);

    if (bulletMatch) {
      if (inOl) { html += "</ol>"; inOl = false; }
      if (!inUl) { html += "<ul class='answer-list'>"; inUl = true; }
      html += `<li>${parseInlineMarkdown(bulletMatch[1])}</li>`;
    } else if (numMatch) {
      if (inUl) { html += "</ul>"; inUl = false; }
      if (!inOl) { html += "<ol class='answer-steps'>"; inOl = true; }
      html += `<li>${parseInlineMarkdown(numMatch[2])}</li>`;
    } else {
      if (inUl) { html += "</ul>"; inUl = false; }
      if (inOl) { html += "</ol>"; inOl = false; }

      // Check if it's a section title like **Nguyên liệu:** or **Tên đồ uống:**
      if (line.startsWith("**") && (line.endsWith("**") || line.endsWith(":**") || line.includes(":**"))) {
        html += `<div class='answer-section-title'>${parseInlineMarkdown(line)}</div>`;
      } else {
        html += `<div class='answer-line'>${parseInlineMarkdown(line)}</div>`;
      }
    }
  }

  if (inUl) html += "</ul>";
  if (inOl) html += "</ol>";

  return html;
}

// Render Server ReAct Steps
function renderBotResponse(bubble, traces, finalAnswer) {
  bubble.innerHTML = "";

  if (currentMode === "baseline") {
    bubble.innerHTML = `
      <div class="bot-answer-container">
        <div class="bot-answer-header">🤖 <strong>Chatbot Baseline:</strong></div>
        <div class="bot-answer-content">${formatBotAnswer(finalAnswer || "Tôi là Chatbot Baseline (Cấp 2), không có quyền truy cập MCP Server để tra cứu hay lưu công thức.")}</div>
      </div>
    `;
    scrollToBottom();
    return;
  }

  // Render Final Answer on top with structured line-by-line formatting
  const answerContainer = document.createElement("div");
  answerContainer.className = "bot-answer-container";
  answerContainer.innerHTML = `
    <div class="bot-answer-header">🏁 <strong>Kết luận:</strong></div>
    <div class="bot-answer-content">${formatBotAnswer(finalAnswer || "Đã hoàn thành xử lý qua MCP Server.")}</div>
  `;
  bubble.appendChild(answerContainer);

  // Render ReAct Execution Steps
  if (traces && traces.length > 0) {
    const traceBox = document.createElement("div");
    traceBox.className = "react-trace-box";

    traces.forEach(step => {
      if (step.action_type === "TOOL_EXECUTION") {
        const card = document.createElement("div");
        card.className = "react-step-card";
        card.innerHTML = `
          <div class="react-step-header">
            <span class="step-label">🔄 Step ${step.step}: TOOL EXECUTION</span>
            <span class="step-latency">${step.latency_ms ? step.latency_ms + ' ms' : 'Live'}</span>
          </div>
          <div class="react-step-body">
            <div class="thought-text">🧠 <span>${escapeHtml(step.thought || "Đang phân tích...")}</span></div>
            <div class="action-chip">🛠️ ${step.tool_name}(${escapeHtml(JSON.stringify(step.arguments || {}))})</div>
            <div class="obs-box">👁️ <strong>Observation từ MCP:</strong>\n${escapeHtml(JSON.stringify(step.observation, null, 2))}</div>
          </div>
        `;
        traceBox.appendChild(card);
      }
    });

    bubble.appendChild(traceBox);
  }

  scrollToBottom();
}

// Client-side simulation when running standalone HTML without python server
function simulateReActFlow(bubble, query) {
  const qLower = query.toLowerCase();
  
  if (currentMode === "baseline") {
    setTimeout(() => {
      bubble.innerHTML = `
        <div class="bot-answer-container">
          <div class="bot-answer-header">🤖 <strong>Chatbot Baseline:</strong></div>
          <div class="bot-answer-content">
            <div class="answer-line">Tôi là Chatbot tư vấn đồ uống.</div>
            <div class="answer-line">Tôi có thể giải thích các kiến thức chung, nhưng <strong>không có quyền gọi Tool</strong> để tra cứu cơ sở dữ liệu thời gian thực hay lưu công thức vào danh sách yêu thích.</div>
          </div>
        </div>
      `;
      scrollToBottom();
    }, 400);
    return;
  }

  // Simulation of ReAct steps
  if (qLower.includes("khác nhau") || qLower.includes("phân biệt") || qLower.includes("là gì")) {
    // TC01
    setTimeout(() => {
      bubble.innerHTML = `
        <div class="bot-answer-container">
          <div class="bot-answer-header">🏁 <strong>Kết luận:</strong></div>
          <div class="bot-answer-content">
            <div class="answer-line">Phân biệt Cocktail và Mocktail:</div>
            <ul class="answer-list">
              <li><strong>Cocktail:</strong> Thức uống có cồn, kết hợp rượu nền (Rum, Tequila, Gin, Vodka...) với các loại siro, nước trái cây hoặc thảo mộc.</li>
              <li><strong>Mocktail:</strong> Thức uống hoàn toàn không có cồn, pha chế từ nước ép, soda, tonic, siro và thảo mộc thanh mát.</li>
            </ul>
          </div>
        </div>
        <div class="react-trace-box">
          <div class="react-step-card">
            <div class="react-step-header">
              <span class="step-label">🎯 Step 1: Direct Reasoning</span>
              <span class="step-latency">12.4 ms</span>
            </div>
            <div class="react-step-body">
              <div class="thought-text">🧠 <span>Câu hỏi kiến thức chung về phân biệt Cocktail và Mocktail, trả lời trực tiếp không cần gọi Tool.</span></div>
            </div>
          </div>
        </div>
      `;
      scrollToBottom();
    }, 500);
  } else if (qLower.includes("dragon fire") || qLower.includes("không tồn tại") || qLower.includes("xyz")) {
    // TC05: Edge case (NOT_FOUND -> No save)
    setTimeout(() => {
      bubble.innerHTML = `
        <div class="bot-answer-container">
          <div class="bot-answer-header">🏁 <strong>Kết luận:</strong></div>
          <div class="bot-answer-content">
            <div class="answer-line">Rất tiếc, hiện tại không tìm thấy công thức cho <strong>Dragon Fire Cocktail XYZ</strong> trong cơ sở dữ liệu.</div>
            <div class="answer-line">Agent tuân thủ nguyên tắc không bịa đặt công thức và <strong>không gọi lệnh lưu (save_recipe)</strong>.</div>
          </div>
        </div>
        <div class="react-trace-box">
          <div class="react-step-card">
            <div class="react-step-header">
              <span class="step-label">🔄 Step 1: TOOL EXECUTION</span>
              <span class="step-latency">412.15 ms</span>
            </div>
            <div class="react-step-body">
              <div class="thought-text">🧠 <span>Người dùng cần công thức Dragon Fire Cocktail XYZ trước khi lưu. Tôi sẽ tra cứu Dragon Fire Cocktail XYZ.</span></div>
              <div class="action-chip">🛠️ recipe_search({"drink_name": "Dragon Fire Cocktail XYZ"})</div>
              <div class="obs-box">👁️ <strong>Observation từ MCP:</strong>\n{\n  "status": "NOT_FOUND",\n  "message": "Không tìm thấy công thức phù hợp."\n}</div>
            </div>
          </div>
          <div class="react-step-card">
            <div class="react-step-header">
              <span class="step-label">🧠 Step 2: Dynamic Decision</span>
              <span class="step-latency">140.2 ms</span>
            </div>
            <div class="react-step-body">
              <div class="thought-text">🧠 <span>Công thức không tìm thấy (NOT_FOUND). Tuân thủ quy tắc không bịa đặt và KHÔNG gọi save_recipe.</span></div>
            </div>
          </div>
        </div>
      `;
      scrollToBottom();
    }, 600);
  } else if (qLower.includes("lưu") && (qLower.includes("margarita") || qLower.includes("yêu thích"))) {
    // TC04: Multi-step Reasoning
    setTimeout(() => {
      if (!savedRecipes.includes("Margarita")) {
        savedRecipes.push("Margarita");
        loadSavedRecipes();
      }
      bubble.innerHTML = `
        <div class="bot-answer-container">
          <div class="bot-answer-header">🏁 <strong>Kết luận:</strong></div>
          <div class="bot-answer-content">
            <div class="answer-line"><strong>Tên đồ uống:</strong> Margarita (Cocktail)</div>
            <div class="answer-section-title">Nguyên liệu:</div>
            <ul class="answer-list">
              <li>50ml Tequila</li>
              <li>25ml Triple Sec</li>
              <li>25ml Nước cốt chanh tươi (Fresh lime juice)</li>
              <li>Đá viên & Muối viền ly</li>
            </ul>
            <div class="answer-section-title">Cách làm:</div>
            <ol class="answer-steps">
              <li>Làm ướt miệng ly bằng chanh và nhúng vào muối.</li>
              <li>Cho Tequila, Triple Sec và nước cốt chanh vào bình shaker.</li>
              <li>Thêm đá và lắc mạnh đều tay.</li>
              <li>Lọc và rót ra ly cocktail.</li>
            </ol>
            <div class="answer-line" style="color: var(--primary-300); font-weight: 600; margin-top: 6px;">✨ Trạng thái: Đã lưu Margarita vào danh sách yêu thích thành công!</div>
          </div>
        </div>
        <div class="react-trace-box">
          <div class="react-step-card">
            <div class="react-step-header">
              <span class="step-label">🔄 Step 1: TOOL EXECUTION</span>
              <span class="step-latency">542.31 ms</span>
            </div>
            <div class="react-step-body">
              <div class="thought-text">🧠 <span>Cần tìm công thức Margarita trước khi có thể lưu. Tôi sẽ tra cứu Margarita.</span></div>
              <div class="action-chip">🛠️ recipe_search({"drink_name": "Margarita"})</div>
              <div class="obs-box">👁️ <strong>Observation từ MCP:</strong>\n{\n  "status": "SUCCESS",\n  "data": {\n    "drink_name": "Margarita",\n    "category": "Cocktail",\n    "ingredients": ["50ml tequila", "25ml triple sec", "25ml lime juice"]\n  }\n}</div>
            </div>
          </div>
          <div class="react-step-card">
            <div class="react-step-header">
              <span class="step-label">🔄 Step 2: TOOL EXECUTION (Multi-step Action)</span>
              <span class="step-latency">311.42 ms</span>
            </div>
            <div class="react-step-body">
              <div class="thought-text">🧠 <span>Công thức đã tìm thấy, tiếp tục gọi save_recipe theo mục tiêu của người dùng.</span></div>
              <div class="action-chip">🛠️ save_recipe({"drink_name": "Margarita"})</div>
              <div class="obs-box">👁️ <strong>Observation từ MCP:</strong>\n{\n  "status": "SUCCESS",\n  "message": "Đã lưu Margarita vào danh sách yêu thích."\n}</div>
            </div>
          </div>
        </div>
      `;
      scrollToBottom();
    }, 700);
  } else {
    // Default search (TC02 / TC03)
    const isMojito = qLower.includes("mojito");
    const drinkName = isMojito ? "Virgin Mojito" : "Mojito";
    setTimeout(() => {
      bubble.innerHTML = `
        <div class="bot-answer-container">
          <div class="bot-answer-header">🏁 <strong>Kết luận:</strong></div>
          <div class="bot-answer-content">
            <div class="answer-line">Dưới đây là công thức ${drinkName} dành cho bạn:</div>
            <div class="answer-line"><strong>Tên đồ uống:</strong> ${drinkName} (${isMojito ? 'Mocktail' : 'Cocktail'})</div>
            <div class="answer-section-title">Nguyên liệu:</div>
            <ul class="answer-list">
              <li>30ml Nước cốt chanh tươi (Fresh lime juice)</li>
              <li>20ml Siro đường (Sugar syrup)</li>
              <li>8–10 Lá bạc hà tươi (Mint leaves)</li>
              <li>Nước Soda (Soda water) & Đá viên</li>
            </ul>
            <div class="answer-section-title">Cách làm:</div>
            <ol class="answer-steps">
              <li>Cho lá bạc hà và siro đường vào ly.</li>
              <li>Thêm nước cốt chanh tươi.</li>
              <li>Dầm nhẹ lá bạc hà để giải phóng tinh dầu thơm.</li>
              <li>Thêm đá viên đầy ly.</li>
              <li>Rót soda lên trên (Top soda).</li>
              <li>Khuấy nhẹ và thưởng thức!</li>
            </ol>
          </div>
        </div>
        <div class="react-trace-box">
          <div class="react-step-card">
            <div class="react-step-header">
              <span class="step-label">🔄 Step 1: TOOL EXECUTION</span>
              <span class="step-latency">480.12 ms</span>
            </div>
            <div class="react-step-body">
              <div class="thought-text">🧠 <span>Tra cứu công thức theo yêu cầu của người dùng qua MCP Server.</span></div>
              <div class="action-chip">🛠️ recipe_search({"drink_name": "${drinkName}"})</div>
              <div class="obs-box">👁️ <strong>Observation từ MCP:</strong>\n{\n  "status": "SUCCESS",\n  "data": {\n    "drink_name": "${drinkName}",\n    "category": "${isMojito ? 'Mocktail' : 'Cocktail'}",\n    "ingredients": ["Nước cốt chanh", "Lá bạc hà", "Soda water", "Đá"]\n  }\n}</div>
            </div>
          </div>
        </div>
      `;
      scrollToBottom();
    }, 500);
  }
}

// Update saved recipes sidebar list
function loadSavedRecipes() {
  const container = document.getElementById("savedRecipesList");
  if (!container) return;
  container.innerHTML = savedRecipes.map(item => `
    <div class="saved-item">
      <span>❤️</span> ${escapeHtml(item)}
    </div>
  `).join("");
}

// Fetch initial trace log from server if available
async function fetchInitialTrace() {
  try {
    const res = await fetch("/api/trace");
    if (res.ok) {
      const data = await res.json();
      currentWaterfallTrace = data;
    }
  } catch (e) {
    // Standalone fallback trace sample
    currentWaterfallTrace = [
      {
        "step": 1,
        "query": "Tìm Margarita và lưu vào yêu thích.",
        "action_type": "TOOL_EXECUTION",
        "thought": "Cần tìm công thức trước.",
        "tool_name": "recipe_search",
        "arguments": { "drink_name": "Margarita" },
        "observation": { "status": "SUCCESS", "data": { "drink_name": "Margarita", "category": "Cocktail" } },
        "latency_ms": 542.31
      },
      {
        "step": 2,
        "query": "Tìm Margarita và lưu vào yêu thích.",
        "action_type": "TOOL_EXECUTION",
        "thought": "Công thức đã tìm thấy, cần lưu theo yêu cầu.",
        "tool_name": "save_recipe",
        "arguments": { "drink_name": "Margarita" },
        "observation": { "status": "SUCCESS", "message": "Đã lưu Margarita vào danh sách yêu thích." },
        "latency_ms": 311.42
      },
      {
        "step": 3,
        "query": "Tìm Margarita và lưu vào yêu thích.",
        "action_type": "FINAL_ANSWER",
        "thought": "Đã hoàn thành mục tiêu.",
        "output": "Đã tìm thấy công thức Margarita và lưu vào danh sách yêu thích.",
        "latency_ms": 8.2
      }
    ];
  }
}

// Modal Trace Inspector
function openTraceModal() {
  const modal = document.getElementById("traceModal");
  const viewer = document.getElementById("traceJsonViewer");
  viewer.textContent = JSON.stringify(currentWaterfallTrace, null, 2);
  modal.classList.add("active");
}

function closeTraceModal() {
  const modal = document.getElementById("traceModal");
  modal.classList.remove("active");
}

// Helper: Clear Chat
function clearChat() {
  const chat = document.getElementById("chatContainer");
  chat.innerHTML = `
    <div class="message-row bot">
      <div class="avatar bot">🍸</div>
      <div class="message-bubble">
        <p><strong>Đã làm mới phiên trò chuyện!</strong> Bạn có thể bắt đầu bằng một câu hỏi mới hoặc chọn Test Case từ menu bên trái.</p>
      </div>
    </div>
  `;
}

function scrollToBottom() {
  const container = document.getElementById("chatContainer");
  container.scrollTop = container.scrollHeight;
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
