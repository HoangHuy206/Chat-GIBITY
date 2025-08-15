from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import os

# ====== DANH SÁCH API KEY ======
API_KEYS = [
    "AIzaSyAz-qhdAKYVEQWfbPi-T_SV02hjtPoh1BM",
    "AIzaSyDl6lN_pZsH27kta_th6yB9j6BswmxjIWw",
    "AIzaSyD0ZPhkVVVUJ2wWsTtRfkWQ617w2aaIMFE"
]
current_key_index = 0

def set_api_key(index):
    global current_key_index, model
    current_key_index = index % len(API_KEYS)
    genai.configure(api_key=API_KEYS[current_key_index])
    model = genai.GenerativeModel("gemini-1.5-flash")
    print(f"[INFO] Đang dùng API key {current_key_index+1}/{len(API_KEYS)}")

# Khởi tạo key ban đầu
set_api_key(0)

app = Flask(__name__)

# --- Trang HTML chính ---
@app.get("/")
def index():
    return render_template("index.html")  # file HTML nằm trong thư mục templates/

@app.post("/ask")
def ask():
    global current_key_index
    data = request.get_json(silent=True) or {}
    question = (data.get("message") or "").strip()
    if not question:
        return jsonify({"reply": "Bạn chưa nhập câu hỏi."})

    if question.lower() == "tạm biệt":
        return jsonify({"reply": "Tạm biệt! Hẹn gặp lại bạn 👋"})

    tries = 0
    while tries < len(API_KEYS):
        try:
            resp = model.generate_content(f"Trả lời bằng tiếng Việt, ngắn gọn, mạch lạc: {question}")
            return jsonify({"reply": resp.text})
        except Exception as e:
            err_str = str(e).lower()
            if "quota" in err_str or "429" in err_str or "403" in err_str:
                print(f"[CẢNH BÁO] API key {API_KEYS[current_key_index]} hết quota. Đổi sang key khác...")
                tries += 1
                set_api_key(current_key_index + 1)
            else:
                return jsonify({"reply": f"Đã xảy ra lỗi: {e}"})
    return jsonify({"reply": "Tất cả API key đã hết quota hoặc gặp lỗi."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)