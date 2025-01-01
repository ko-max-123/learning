import os
import fitz  # PyMuPDF
import re
import openai

# OpenAI APIキーを設定
openai.api_key = 'your-api-key'

# フォルダパスを設定
folder_path = '/pdf_files'
output_file = 'summary_report.txt'

# PDFからテキストを抽出する関数
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
    return text

# ChatGPTにテキストを渡して分析結果を取得する関数
def analyze_financial_report_with_gpt(text):
    prompt = f"""
    あなたはアナリストで投資家です。以下の決算情報を分析し、以下の項目についてまとめてください。
    ・懸念点
    ・赤字か、黒字か
    ・赤字の場合はさらに赤字拡大するのか、または改善の余地があるのか
    ・黒字の場合は成長可能か、または鈍化か
    ・その他で投資家としての補足事項
    また、100点満点でこの銘柄に対して点数をつけなさい。

    決算情報:
    {text}
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {e}"

# メイン処理
def main():
    with open(output_file, 'w', encoding='utf-8') as f:
        for filename in os.listdir(folder_path):
            if filename.endswith('.pdf'):
                pdf_path = os.path.join(folder_path, filename)
                text = extract_text_from_pdf(pdf_path)
                analysis = analyze_financial_report_with_gpt(text)

                # レポート出力
                f.write(f"File: {filename}\n")
                f.write(f"{analysis}\n")
                f.write("\n==============================\n\n")
                print(f"Processed: {filename}")

if __name__ == '__main__':
    main()
