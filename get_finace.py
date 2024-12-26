import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import yfinance as yf
import matplotlib.dates as mdates

# 株価データを取得し、プロットする関数
def plot_stock():
    symbol = symbol_entry.get()
    if not symbol:
        return

    try:
        # データ取得
        data = yf.download(symbol, period="6mo")
        data.index = pd.to_datetime(data.index)  # ★日付をdatetime型に変換
        data['5MA'] = data['Close'].rolling(window=5).mean()
        data['25MA'] = data['Close'].rolling(window=25).mean()
        data['50MA'] = data['Close'].rolling(window=50).mean()
        data['100MA'] = data['Close'].rolling(window=100).mean()

        # プロット
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(data.index, data['Close'], label='Close Price', color='black')  # ★ x軸にdata.indexを明示
        ax.plot(data.index, data['5MA'], label='5-day MA', color='blue')
        ax.plot(data.index, data['25MA'], label='25-day MA', color='green')
        ax.plot(data.index, data['50MA'], label='50-day MA', color='red')
        ax.plot(data.index, data['100MA'], label='100-day MA', color='purple')

        # ローソク足
        colors = ['red' if close < open else 'green' for open, close in zip(data['Open'], data['Close'])]
        ax.bar(data.index, data['Close'] - data['Open'], bottom=data['Open'], width=0.8, color=colors)  # ★ 幅を0.8に調整

        # X軸のフォーマットを修正
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        fig.autofmt_xdate()  # ★ 日付を自動で調整

        ax.set_title(f'{symbol} Stock Price')
        ax.legend()
        ax.grid(True)

        # グラフを表示
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=2, column=0, columnspan=2)
        canvas.draw()

    except Exception as e:
        error_label.config(text=f"エラー: {str(e)}")

# GUIの設定
root = tk.Tk()
root.title("株価表示ツール")
root.geometry("800x600")

# 銘柄入力
tk.Label(root, text="銘柄コード (例: AAPL, TSLA, 7203.T):").grid(row=0, column=0, padx=10, pady=10)
symbol_entry = ttk.Entry(root)
symbol_entry.grid(row=0, column=1, padx=10, pady=10)

# 実行ボタン
plot_button = ttk.Button(root, text="表示", command=plot_stock)
plot_button.grid(row=1, column=0, columnspan=2, pady=10)

# エラーメッセージ用ラベル
error_label = tk.Label(root, text="", fg="red")
error_label.grid(row=3, column=0, columnspan=2)

# GUIの実行
root.mainloop()
