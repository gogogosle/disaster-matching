import os
import json
import re
from flask import Flask, render_template, request
import pandas as pd
import google.generativeai as genai

app = Flask(__name__)

# --- 設定 ---
# Renderの環境変数からAPIキーを取得
API_KEY = os.environ.get("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

def identify_and_process_files(files):
    """
    アップロードされたファイルを読み込み、
    SNSデータ(Spectee)と業務データ(Chrono)を判別してテキスト化する
    """
    data_text_chrono = ""
    data_text_sns = ""
    
    for file in files:
        if file.filename == '':
            continue
        try:
            # CSV読み込み (エラー回避のためエンジン指定・不正行スキップ)
            try:
                df = pd.read_csv(file, on_bad_lines='skip', engine='python', encoding='utf-8_sig')
            except:
                # UTF-8でダメならShift-JISでトライ
                file.seek(0)
                df = pd.read_csv(file, on_bad_lines='skip', engine='python', encoding='shift_jis')

            cols = df.columns.tolist()
            
            # --- 判別ロジック ---
            
            # パターンA: 防災システム（Chrono）
            if '受信日時' in cols and '情報内容' in cols:
                target_cols = ['Id', '受信日時', '区域', '住所', '区分', '情報内容', '緯度', '経度']
                valid_cols = [c for c in target_cols if c in cols]
                csv_str = df[valid_cols].head(50).to_csv(index=False)
                data_text_chrono += f"\n{csv_str}"
                
            # パターンB: SNSデータ (Spectee)
            elif 'テキスト' in cols or 'SNS_URL' in cols:
                target_cols = ['日時', 'テキスト', '市区町村', '大字町丁目', '事象', '緯度', '経度']
                valid_cols = [c for c in target_cols if c in cols]
                csv_str = df[valid_cols].head(50).to_csv(index=False)
                data_text_sns += f"\n{csv_str}"
                
        except Exception as e:
            print(f"File read error ({file.filename}): {e}")
            continue

    return data_text_chrono, data_text_sns

def clean_json_string(json_str):
    """AIがMarkdown記法を含めて返した場合に除去する"""
    cleaned = re.sub(r'^```json\s*', '', json_str)
    cleaned = re.sub(r'^```\s*', '', cleaned)
    cleaned = re.sub(r'\s*```$', '', cleaned)
    return cleaned.strip()

@app.route('/', methods=['GET', 'POST'])
def index():
    matches = []
    error_message = None

    if request.method == 'POST':
        uploaded_files = request.files.getlist('files')

        if not API_KEY:
            error_message = "サーバー設定エラー: APIキーが設定されていません。"
        elif not uploaded_files or uploaded_files[0].filename == '':
            error_message = "CSVファイルを選択してください。"
        else:
            txt_chrono, txt_sns = identify_and_process_files(uploaded_files)
            
            if not txt_chrono or not txt_sns:
                error_message = "エラー: SNSデータと防災システムデータの両方が必要です。（カラム名で自動判別します）"
            else:
                try:
                    # ★ここを最新のGemini 3.0 Flashに変更
                    model = genai.GenerativeModel('gemini-3-flash')

                    prompt = f"""
                    あなたは熟練した災害情報分析官です。
                    以下の「A: 防災システム登録データ」と「B: SNS投稿データ」を照合し、同一の災害事象について言及していると思われるペアを特定してください。
                    
                    【照合ルール（重要）】
                    1. 時間軸のズレ: 前後12時間の幅で許容する。
                    2. 場所の特定: 「町名」や「ランドマーク」の一致を最重視する。
                    3. 事象の類似: 表現が異なっても意味が通じる場合は一致とみなす。
                    4. 確信度のスコアリング: 0%〜100%で評価。

                    【入力データ】
                    [A: 防災システム登録データ]
                    {txt_chrono}

                    [B: SNS投稿データ]
                    {txt_sns}

                    【出力形式 (JSON)】
                    必ず以下のJSON配列形式のみを出力してください。Markdown装飾は不要です。
                    [
                        {{
                            "match_id": 1,
                            "score": 95,
                            "reason": "理由を記述",
                            "location_label": "地名",
                            "lat": 33.590, 
                            "lng": 130.412,
                            "event_type": "事象種別",
                            "chrono_info": "システム側の要約",
                            "sns_info": "SNS側の要約"
                        }}
                    ]
                    """

                    response = model.generate_content(prompt)
                    cleaned_text = clean_json_string(response.text)
                    matches = json.loads(cleaned_text)

                except Exception as e:
                    error_message = f"AI処理中にエラーが発生しました: {e}"
                    matches = []

    return render_template('index.html', matches=matches, error=error_message)

if __name__ == '__main__':
    app.run(debug=True)
