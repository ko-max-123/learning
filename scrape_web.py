import requests
from bs4 import BeautifulSoup

# 指定されたURL
url = ''

# ページの内容を取得
response = requests.get(url)
response.encoding = response.apparent_encoding  # 文字コードを自動検出して設定

if response.status_code == 200:
    # BeautifulSoupでHTMLを解析
    soup = BeautifulSoup(response.text, 'html.parser')

    # ページの本文を抽出
    # 例: ページ内のすべてのテキストを取得
    content = soup.get_text(separator='\n')

    # ファイルに書き出す
    with open('output.txt', 'w', encoding='utf-8') as file:
        file.write(content)

    print("ページの内容をoutput.txtに保存しました。")
else:
    print(f"エラーが発生しました。ステータスコード: {response.status_code}")
