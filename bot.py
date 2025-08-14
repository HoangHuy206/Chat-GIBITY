# bot.py
from flask import Flask, request, jsonify, render_template_string
import google.generativeai as genai
import os

# --- Cấu hình API ---
API_KEY =("AIzaSyDwlowb3Wf2ynjqKduU8t9auZKnbJLoEBk")  # thay nếu muốn hard-code
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# --- Giao diện HTML + CSS + JS (trong 1 file) ---
PAGE = """
<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <title>Google GIBITY</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <style>
    :root { --bg:#0f172a; --panel:#111827; --user:#22c55e20; --bot:#60a5fa20; --text:#e5e7eb; }
    *{box-sizing:border-box}
    body{margin:0;background:var(--bg);color:var(--text);font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial}
    .wrap{max-width:800px;margin:0 auto;padding:16px}
    .title{font-weight:700;text-align:center;margin:12px 0 16px}
    .chat{height:70vh;overflow-y:auto;background:var(--panel);border-radius:14px;padding:12px;box-shadow:0 6px 30px #0004}
    .msg{margin:8px 0;padding:10px 12px;border-radius:12px;line-height:1.5;white-space:pre-wrap}
    .user{background:var(--user);text-align:right;border:1px solid #22c55e40}
    .bot{background:var(--bot);border:1px solid #60a5fa40}
    .row{display:flex;gap:8px;margin-top:12px}
    #message{flex:1;padding:12px;border-radius:12px;border:1px solid #374151;background:#0b1220;color:var(--text)}
    button{padding:12px 18px;border:none;border-radius:12px;background:#3b82f6;color:white;cursor:pointer}
    button:disabled{opacity:.6;cursor:not-allowed}
    .hint{opacity:.7;font-size:14px;text-align:center;margin-top:8px}
  </style>
</head>
<body>
  <div class="wrap">
    <h2 class="title">Google GIBITY (By Hoàng Huy)</h2>
    <div id="chat" class="chat"></div>
    <div class="row">
      <input id="message" placeholder="Nhập câu hỏi và nhấn Gửi..." autocomplete="off">
      <button id="send">Gửi</button>
    </div>
    <div class="hint">Gõ <b>tạm biệt</b> để kết thúc phiên làm việc (ở phía server sẽ không thoát app).</div>
  </div>

<script>
const chat = document.getElementById("chat");
const input = document.getElementById("message");
const sendBtn = document.getElementById("send");

function addMsg(text, who){
  const div = document.createElement("div");
  div.className = "msg " + (who === "user" ? "user":"bot");
  div.textContent = text;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

async function askServer(msg){
  sendBtn.disabled = true;
  try{
    const res = await fetch("/ask", {
      method:"POST",
      headers:{ "Content-Type":"application/json" },
      body: JSON.stringify({ message: msg })
    });
    const data = await res.json();
    addMsg(data.reply || "(không có phản hồi)", "bot");
  }catch(err){
    addMsg("Lỗi: " + err, "bot");
  }finally{
    sendBtn.disabled = false;
  }
}

function sendMessage(){
  const msg = input.value.trim();
  if(!msg) return;
  addMsg(msg, "user");
  input.value = "";
  askServer(msg);
}

sendBtn.addEventListener("click", sendMessage);
input.addEventListener("keydown", e => {
  if(e.key === "Enter"){ sendMessage(); }
});
</script>
</body>
</html>
"""

app = Flask(__name__)

@app.get("/")
def index():
    return render_template_string(PAGE)

@app.post("/ask")
def ask():
    data = request.get_json(silent=True) or {}
    question = (data.get("message") or "").strip()
    if not question:
        return jsonify({"reply": "Bạn chưa nhập câu hỏi."})

    # Không tắt server khi người dùng gõ 'tạm biệt' — chỉ phản hồi lịch sự
    if question.lower() == "tạm biệt":
        return jsonify({"reply": "Tạm biệt! Hẹn gặp lại bạn 👋"})

    try:
        resp = model.generate_content(f"Trả lời bằng tiếng Việt, ngắn gọn, mạch lạc: {question}")
        return jsonify({"reply": resp.text})
    except Exception as e:
        return jsonify({"reply": f"Đã xảy ra lỗi: {e}"})

if __name__ == "__main__":
    # Chạy ở cổng 5000: http://localhost:5000
    app.run(host="0.0.0.0", port=5000, debug=True)
