from flask import Flask, request, jsonify, render_template
from nlp_matcher import load_vocab_db, extract_key_vocabulary

app = Flask(__name__)

# 在伺服器啟動時，預先將 7000 單字庫載入記憶體
# 這樣就不用每次有人發送請求時都重新讀取 JSON，大幅提升效能
DB_PATH = "7000_words.json"
try:
    vocab_db = load_vocab_db(DB_PATH)
    print(f"✅ 成功載入單字庫，共 {len(vocab_db)} 筆資料。")
except FileNotFoundError:
    print(f"❌ 找不到 {DB_PATH}，請確認檔案是否有放在專案根目錄。")
    vocab_db = {}

@app.route('/')
def index():
    # 當使用者造訪首頁時，回傳 templates 資料夾內的 index.html
    return render_template('index.html')

@app.route('/api/extract', methods=['POST'])
def extract_api():
    # 接收前端傳來的 JSON 資料 (包含考卷文字)
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({"error": "沒有收到文章資料"}), 400
        
    text = data['text']
    
    # 呼叫我們的 NLP 腳本進行解析與過濾
    matched_results = extract_key_vocabulary(text, vocab_db)
    
    # 將擷取出來的單字陣列回傳給前端
    return jsonify({
        "status": "success",
        "word_count": len(matched_results),
        "results": matched_results
    })

if __name__ == '__main__':
    # 啟動 Flask 開發伺服器，開啟 debug 模式方便修改後自動重整
    app.run(debug=True, port=5000)