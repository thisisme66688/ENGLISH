from flask import Flask, request, jsonify, render_template
from nlp_matcher import load_vocab_db, extract_key_vocabulary
import pdfplumber  # 新增：引入處理 PDF 的套件

app = Flask(__name__)

DB_PATH = "7000_words.json"
try:
    vocab_db = load_vocab_db(DB_PATH)
    print(f"✅ 成功載入單字庫，共 {len(vocab_db)} 筆資料。")
except FileNotFoundError:
    print(f"❌ 找不到 {DB_PATH}，請確認檔案是否有放在專案根目錄。")
    vocab_db = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/extract', methods=['POST'])
def extract_api():
    # (原本的分析文字程式碼保持不變...)
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "沒有收到文章資料"}), 400
    text = data['text']
    matched_results = extract_key_vocabulary(text, vocab_db)
    return jsonify({
        "status": "success",
        "word_count": len(matched_results),
        "results": matched_results
    })

# ==========================================
# [新增] 處理 PDF 上傳與文字讀取的 API
# ==========================================
@app.route('/api/upload_pdf', methods=['POST'])
def upload_pdf():
    # 檢查請求中是否包含檔案
    if 'file' not in request.files:
        return jsonify({"error": "沒有找到上傳的檔案"}), 400
        
    file = request.files['file']
    
    # 檢查檔名確保使用者有選擇檔案，且是 PDF 格式
    if file.filename == '' or not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "請上傳有效的 PDF 檔案"}), 400

    try:
        extracted_text = ""
        # 直接從記憶體讀取上傳的檔案，不存進硬碟以節省空間
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n\n"
                    
        return jsonify({"status": "success", "text": extracted_text})
        
    except Exception as e:
        print(f"PDF 讀取錯誤: {e}")
        return jsonify({"error": "PDF 檔案讀取失敗，可能是檔案損毀或加密"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)