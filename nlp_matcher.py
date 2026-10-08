import json
import spacy

# 載入 spaCy 的輕量級英文模型
nlp = spacy.load("en_core_web_sm")

# ==========================================
# [新增] 自訂太簡單的基礎單字黑名單
# 雖然 spaCy 會自動過濾 the, is, at 這種文法字
# 但像是 boy, apple, book 這種實體字，你可以手動加在這裡
# ==========================================
CUSTOM_EASY_WORDS = {"boy", "girl", "apple", "book", "dog", "cat", "car", "good", "bad"}

# 將我們的自訂名單也加入到 spaCy 的停用詞庫中
for word in CUSTOM_EASY_WORDS:
    nlp.vocab[word].is_stop = True

def load_vocab_db(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
        
    vocab_db = {}
    for item in raw_data:
        words = item['word'].split('/')
        for w in words:
            clean_word = w.strip().lower()
            if clean_word:
                vocab_db[clean_word] = item
                
    return vocab_db

def extract_key_vocabulary(text, vocab_db):
    doc = nlp(text)
    found_words = {}
    
    for token in doc:
        # [修改] 加入 token.is_stop 判斷
        # 如果是標點、空白、數字、專有名詞，或是「停用詞 (包含自訂黑名單)」，就直接略過
        if token.is_punct or token.is_space or token.is_digit or token.pos_ == "PROPN" or token.is_stop:
            continue
            
        lemma = token.lemma_.lower()
        
        # 再次確保還原後的字根不在黑名單內，且存在於我們的 7000 單字典中
        if not nlp.vocab[lemma].is_stop and lemma in vocab_db:
            if lemma not in found_words:
                found_words[lemma] = vocab_db[lemma]
                found_words[lemma]['original_text'] = token.text
                
    return list(found_words.values())

if __name__ == "__main__":
    DB_PATH = "7000_words.json"
    
    try:
        my_vocab_db = load_vocab_db(DB_PATH)
        print(f"成功載入單字庫，共 {len(my_vocab_db)} 筆。\n")
        
        # 測試字串：包含基礎字 (The, were, by, they, and, an) 與自訂黑名單字 (dogs, sleep)
        sample_exam_text = """
        The abandoned dogs were rescued by local actors. 
        They provided medical care and an area for the animals to sleep.
        """
        
        print("考卷原文:")
        print(sample_exam_text)
        print("-" * 40)
        
        matched_results = extract_key_vocabulary(sample_exam_text, my_vocab_db)
        
        print("擷取出的重點單字:")
        for result in matched_results:
            print(f"[{result['word']}] ({result['part_of_speech']}) {result['meaning']}")
            
    except FileNotFoundError:
        print(f"找不到 {DB_PATH}，請確認檔案位置。")