import pdfplumber
import json
import re

def parse_vocabulary_pdf(pdf_path, output_json):
    results = []
    
    # 匹配詞性與中文解釋的邊界
    # 邏輯：開頭由小寫字母、小數點、斜線、空白組成(如 n. 或 adv. / prep.)，後面接著其他內容
    pos_pattern = re.compile(r'^([a-z\.\/\s]+)\s+(.+)')

    print("開始解析 PDF...")
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            width = page.width
            height = page.height
            
            # 建立左右兩半的裁切框 (x0, top, x1, bottom)
            left_bbox = (0, 0, width * 0.5, height)
            right_bbox = (width * 0.5, 0, width, height)
            
            # 依序處理左欄與右欄
            for bbox in [left_bbox, right_bbox]:
                column_page = page.crop(bbox)
                text = column_page.extract_text()
                
                if not text:
                    continue
                
                lines = text.split('\n')
                current_word = None  # 用來暫存當前處理中的單字，方便處理跨行
                
                for line in lines:
                    line = line.strip()
                    # 過濾掉頁首或空白行
                    if not line or "大考中心" in line or "LEVEL" in line:
                        continue
                        
                    # 判斷是否為一個新單字的開頭（特徵：行內包含音標的起始括號 '['）
                    if '[' in line:
                        try:
                            # 1. 抓取單字 (第一組 '[' 前面的所有字元)
                            first_bracket_idx = line.index('[')
                            word_part = line[:first_bracket_idx].strip()
                            
                            rest = line[first_bracket_idx:]
                            
                            # 2. 抓取音標 (第一組 '[' 到最後一組 ']' 之間的所有字元)
                            # 使用 rindex 避免像 [`æktɚ]/ [`æktrɪs] 被提前截斷
                            last_bracket_idx = rest.rindex(']')
                            phonetic_part = rest[:last_bracket_idx+1].strip()
                            
                            # 3. 抓取剩下的詞性與解釋
                            meaning_part = rest[last_bracket_idx+1:].strip()
                            
                            pos = ""
                            meaning = meaning_part
                            
                            # 如果這行還有剩下的文字，嘗試分離詞性與解釋
                            if meaning_part:
                                pos_match = pos_pattern.match(meaning_part)
                                if pos_match:
                                    pos = pos_match.group(1).strip()
                                    meaning = pos_match.group(2).strip()
                            
                            # 建立字典並加入總列表 (這裡的字典是 Reference，後續跨行可以直接修改它)
                            current_word = {
                                "word": word_part,
                                "phonetic": phonetic_part,
                                "part_of_speech": pos,
                                "meaning": meaning
                            }
                            results.append(current_word)
                            
                        except ValueError:
                            # 處理預期外格式的錯誤
                            print(f"解析異常行: {line}")
                            
                    else:
                        # 如果這行沒有 '['，代表它是上一個單字的跨行延續 (例如: "n. 男演員/女演員")
                        if current_word:
                            pos_match = pos_pattern.match(line)
                            
                            # 如果上一行沒有抓到詞性，且這一行符合詞性特徵，就補回去
                            if pos_match and not current_word["part_of_speech"]:
                                current_word["part_of_speech"] = pos_match.group(1).strip()
                                current_word["meaning"] = pos_match.group(2).strip()
                            else:
                                # 否則，這行單純是中文解釋的延續 (如編號 "(2) 河堤")
                                if current_word["meaning"]:
                                    current_word["meaning"] += " " + line
                                else:
                                    current_word["meaning"] = line
                                    
            print(f"已完成第 {page_num} 頁處理...")

    # 寫入 JSON
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
        
    print(f"\n轉換成功！共提取了 {len(results)} 個單字，已存為 {output_json}")

# 執行腳本
if __name__ == "__main__":
    parse_vocabulary_pdf(r"C:\workspace\ENGLISH\pdfcut\7000_words.pdf", "7000_words.json")