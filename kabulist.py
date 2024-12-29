import yfinance as yf
import pandas as pd

# 銘柄コードの読み込み
with open('kabulist.txt', 'r') as file:
    symbols = file.read().splitlines()

# データ取得
data = []
for symbol in symbols:
    try:
        # コードに接尾辞を追加（東証用）
        if symbol.isdigit():
            ticker = f"{symbol}.T"
        else:
            ticker = symbol
        
        # Yahoo Financeから情報取得
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # 銘柄名と株価を取得
        name = info.get('longName', 'N/A')  # 銘柄名
        price = info.get('previousClose', 'N/A')  # 前日終値

        data.append({'Code': symbol, 'Name': name, 'Price': price})

    except Exception as e:
        data.append({'Code': symbol, 'Name': 'Error', 'Price': 'Error'})

# データフレーム化とエクセル出力
df = pd.DataFrame(data)
output_path = "stock_prices_with_names.xlsx"
df.to_excel(output_path, index=False)

print(f"データは {output_path} に保存されました。")
