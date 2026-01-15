import os
import json
import re
from flask import Flask, render_template, request
import pandas as pd
import google.generativeai as genai

app = Flask(__name__)

# --- 設定 ---
# APIキー
API_KEY = os.environ.get("GOOGLE_API_KEY")
# モデル名（設定がない場合は安全な 'gemini-1.5-flash' をデフォルトにする）
# ※Renderの環境変数で 'gemini-3-flash-preview' などを指定可能にします
MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")

if API_KEY:
    genai.configure(api_key=API_KEY)

# --- (中略) identify_and_process_files 関数などはそのまま ---
def identify_and_process_files(files):
    # ... (前回のコードと同じ) ...
    data_text_chrono = ""
    data_text_sns = ""
    for file in files:
        if file.filename == '': continue
        try:
            try: df = pd.read_csv(file, on_bad_lines='skip', engine='python', encoding='utf-8_sig')
            except: file.seek(0); df = pd.read_csv(file, on_bad_lines='skip', engine='python', encoding='shift_jis')
            cols = df.columns.tolist()
            if '受信日時' in cols and '情報内容' in cols:
                csv_str = df[['受信日時','情報内容','住所']].head(50).to_csv(index=False); data_text_chrono += f"\n{csv_str}"
            elif 'テキスト' in cols or 'SNS_URL' in cols:
                csv_str = df[['日時','テキスト','市区町村']].head(50).to_csv(index=False); data_text_sns += f"\n{csv_str}"
        except: continue
    return data_text_chrono, data_text_sns

def clean_json_string(json_str):
    cleaned = re.sub(r'^```json\s*', '', json_str)
    cleaned = re.sub(r'^```\s*', '', cleaned)
    cleaned = re.sub(r'\s*```$', '', cleaned)
    return cleaned.strip()

# ★追加機能: 使えるモデル一覧を確認するページ
@app.route('/debug_models')
def debug_models():
    if not API_KEY: return "APIキーが設定されていません"
    try:
        # 今のアカウントで使えるモデル一覧を取得
        models = list(genai.list_models())
        # 'generateContent' に対応しているモデルだけ抽出して表示
        available = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
        return f"<h3>現在使用可能なモデル一覧 (APIから取得):</h3><ul>" + "".join([f"<li>{m}</li>" for m in available]) + "</ul>"
    except Exception as e:
        return f"エラー: {e}"

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
                error_message = "エラー: SNSデータと防災システムデータの両方が必要です。"
            else:
                try:
                    # 環境変数で指定されたモデルを使用
                    model = genai.GenerativeModel(MODEL_NAME)
                    
                    prompt = f"""
                    あなたは熟練した災害情報分析官です。
                    以下のA(防災システム)とB(SNS)を照合し、同一事象を特定してJSONで出力してください。
                    ... (中略: プロンプトは前回と同じ) ...
                    [A: 防災システム] {txt_chrono}
                    [B: SNSデータ] {txt_sns}
                    """
                    
                    response = model.generate_content(prompt)
                    matches = json.loads(clean_json_string(response.text))

                except Exception as e:
                    # エラー時に、現在使おうとしたモデル名を表示してあげる
                    error_message = f"モデル '{MODEL_NAME}' でエラーが発生: {e}. <br><a href='/debug_models' target='_blank'>使えるモデル一覧を確認する</a>"
                    matches = []

    return render_template('index.html', matches=matches, error=error_message)

if __name__ == '__main__':
    app.run(debug=True)
