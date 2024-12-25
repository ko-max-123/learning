import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
import pandas as pd
import numpy as np
import datetime

import matplotlib
matplotlib.use("Agg")  # GUI上でmatplotlibを埋め込むためのバックエンド設定
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplfinance as mpf  # ローソク足描画ライブラリ

# ======================
# 売買戦略の関数群
# ======================

def breakout_strategy(df, n=20):
    """
    ブレイクアウト戦略
    過去n期間の高値を上抜け → Breakout_Buy=1
    過去n期間の安値を下抜け → Breakout_Sell=1
    """
    df = df.copy()
    df['Highest'] = df['High'].rolling(n).max().shift(1)
    df['Lowest'] = df['Low'].rolling(n).min().shift(1)

    # インデックスずれを回避するため、alignを行う（ただし同一DataFrame内なら通常不要）
    close_aligned, high_aligned = df['Close'].align(df['Highest'], axis=0, copy=False)
    df['Breakout_Buy'] = np.where(close_aligned > high_aligned, 1, 0)

    close_aligned2, low_aligned = df['Close'].align(df['Lowest'], axis=0, copy=False)
    df['Breakout_Sell'] = np.where(close_aligned2 < low_aligned, 1, 0)

    return df

def moving_average_crossover_strategy(df, short_window=5, long_window=25):
    """
    移動平均線のゴールデンクロス/デッドクロス戦略
    短期MAが長期MAを上抜け → MA_Buy=1
    短期MAが長期MAを下抜け → MA_Sell=1
    """
    df = df.copy()
    df['MA_short'] = df['Close'].rolling(short_window).mean()
    df['MA_long']  = df['Close'].rolling(long_window).mean()

    # 前日値と当日値でクロス判定
    df['prev_short'] = df['MA_short'].shift(1)
    df['prev_long']  = df['MA_long'].shift(1)

    df['MA_Buy'] = 0
    df['MA_Sell'] = 0

    buy_cond = (df['prev_short'] <= df['prev_long']) & (df['MA_short'] > df['MA_long'])
    sell_cond = (df['prev_short'] >= df['prev_long']) & (df['MA_short'] < df['MA_long'])

    df.loc[buy_cond, 'MA_Buy'] = 1
    df.loc[sell_cond, 'MA_Sell'] = 1

    df.drop(['prev_short','prev_long'], axis=1, inplace=True)
    return df

def opening_range_break_strategy(df, opening_minutes=30):
    """
    オープニングレンジ・ブレイク戦略 (intraday用)
    日ごとに、最初の X分間の高値/安値を超えたら OR_Buy/OR_Sell
    ※日足の場合は1日1本なので意味が薄い。分足データ向けの簡易実装。

    'Operands are not aligned' 回避のため、alignを使ってインデックスを揃えてから np.where を実行。
    """
    df = df.copy()
    # Datetime列が無い場合は作る（yfinance日足などはindexがDatetime）
    if 'Datetime' not in df.columns:
        df['Datetime'] = df.index

    df['Date'] = df['Datetime'].dt.date
    df['Time'] = df['Datetime'].dt.time

    # 日ごとに最初の X 分間を取り、その High/Low を OR_High, OR_Low として集計
    def calc_or(sub_df):
        times = sub_df['Datetime'].sort_values()
        if len(times) == 0:
            return pd.Series([np.nan, np.nan], index=['OR_High','OR_Low'])
        start_dt = times.iloc[0]
        end_dt = start_dt + pd.Timedelta(minutes=opening_minutes)
        mask = (sub_df['Datetime'] >= start_dt) & (sub_df['Datetime'] < end_dt)
        sub_open = sub_df[mask]
        if len(sub_open) == 0:
            return pd.Series([np.nan, np.nan], index=['OR_High','OR_Low'])
        return pd.Series([
            sub_open['High'].max(),
            sub_open['Low'].min()
        ], index=['OR_High','OR_Low'])

    # 日ごとに apply
    or_df = df.groupby('Date').apply(calc_or).reset_index()
    # -> or_df: [Date, OR_High, OR_Low]

    # マージ
    df_reset = df.reset_index(drop=False)
    df_merged = pd.merge(df_reset, or_df, on='Date', how='left')

    # インデックスを Datetime に戻す
    df_merged.set_index('Datetime', inplace=True)
    df_merged.sort_index(inplace=True)

    # OR_Buy, OR_Sell を計算
    # alignで行インデックスを統一
    close_aligned, high_aligned = df_merged['Close'].align(df_merged['OR_High'], axis=0, copy=False)
    df_merged['OR_Buy'] = np.where(close_aligned > high_aligned, 1, 0)

    close_aligned2, low_aligned = df_merged['Close'].align(df_merged['OR_Low'], axis=0, copy=False)
    df_merged['OR_Sell'] = np.where(close_aligned2 < low_aligned, 1, 0)

    return df_merged

def combine_signals(df):
    """
    3つの戦略（ブレイクアウト, オープニングレンジ, MAクロス）シグナルを融合
    OR条件で Synergy_Buy, Synergy_Sell を出す
    """
    df = df.copy()
    buy_cols = ['Breakout_Buy','MA_Buy','OR_Buy']
    sell_cols = ['Breakout_Sell','MA_Sell','OR_Sell']

    for col in buy_cols + sell_cols:
        if col not in df.columns:
            df[col] = 0

    df['Synergy_Buy'] = np.where(df[buy_cols].sum(axis=1) > 0, 1, 0)
    df['Synergy_Sell'] = np.where(df[sell_cols].sum(axis=1) > 0, 1, 0)
    return df

# ======================
# GUIクラス
# ======================
class StrategyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("株式シグナル（順張り3戦略＋グラフ表示）")

        # --- 入力欄 ---
        ttk.Label(root, text="銘柄コード (例: AAPL, 7203.T)").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.ticker_entry = ttk.Entry(root)
        self.ticker_entry.insert(0, "AAPL")  # デフォルト例
        self.ticker_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(root, text="開始日 (YYYY-MM-DD)").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.start_entry = ttk.Entry(root)
        self.start_entry.insert(0, "2023-01-01")
        self.start_entry.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(root, text="終了日 (YYYY-MM-DD)").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.end_entry = ttk.Entry(root)
        self.end_entry.insert(0, "2023-12-31")
        self.end_entry.grid(row=2, column=1, padx=5, pady=2)

        ttk.Label(root, text="取得間隔 interval (1d,1h,5m,etc)").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.interval_combo = ttk.Combobox(root, values=["1d","1h","30m","15m","5m","1m"])
        self.interval_combo.current(0)
        self.interval_combo.grid(row=3, column=1, padx=5, pady=2)

        # 実行ボタン
        self.run_button = ttk.Button(root, text="データ取得＆検証", command=self.run_strategy)
        self.run_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # 結果のテキスト表示
        self.result_text = tk.Text(root, height=15, width=80)
        self.result_text.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        # グラフ表示用のキャンバス (mplfinance)
        self.fig = None
        self.canvas = None

        root.rowconfigure(5, weight=1)
        root.columnconfigure(1, weight=1)

    def run_strategy(self):
        ticker = self.ticker_entry.get().strip()
        start_date = self.start_entry.get().strip()
        end_date = self.end_entry.get().strip()
        interval = self.interval_combo.get()

        if not ticker:
            messagebox.showerror("エラー", "銘柄コードを入力してください。")
            return

        try:
            # 1) データ取得
            df = yf.download(ticker, start=start_date, end=end_date, interval=interval, progress=False, auto_adjust=True)
            if df.empty:
                self.result_text.insert("end", "データが取得できませんでした。\n")
                return

            df = df[['Open','High','Low','Close','Volume']].copy()
            df.sort_index(inplace=True)

            # 2) 各戦略適用
            df = breakout_strategy(df, n=20)
            df = moving_average_crossover_strategy(df, short_window=5, long_window=25)
            # 75日線も表示したいので別途計算
            df['MA_75'] = df['Close'].rolling(75).mean()

            # オープニングレンジ
            df = opening_range_break_strategy(df, opening_minutes=30)

            # シグナル融合
            df = combine_signals(df)

            # 3) テキスト出力
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert("end", f"取得行数: {len(df)}\n")
            self.result_text.insert("end", "直近10行のシグナル状況:\n")
            show_cols = ['Close','Breakout_Buy','Breakout_Sell','MA_Buy','MA_Sell','OR_Buy','OR_Sell','Synergy_Buy','Synergy_Sell']
            self.result_text.insert("end", str(df[show_cols].tail(10)))
            self.result_text.insert("end", "\n")

            # 4) グラフ描画
            self.plot_candlestick_with_signals(df)

        except Exception as e:
            messagebox.showerror("エラー", f"処理中にエラーが発生しました。\n{str(e)}")

    def plot_candlestick_with_signals(self, df):
        """mplfinance を用いてローソク足 + MA(5/25/75) + シグナルを可視化"""
        # 既存キャンバス破棄
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        if self.fig:
            plt.close(self.fig)

        mpf_df = df.copy()
        mpf_df.index.name = "Date"

        # シグナル
        buy_signal = mpf_df[mpf_df['Synergy_Buy'] == 1]
        sell_signal = mpf_df[mpf_df['Synergy_Sell'] == 1]

        # 移動平均線
        mpf_df['MA_5']  = mpf_df['Close'].rolling(5).mean()
        mpf_df['MA_25'] = mpf_df['Close'].rolling(25).mean()
        # すでに df['MA_75'] は計算済み

        # additional plots
        apds = [
            mpf.make_addplot(mpf_df['MA_5'],  color='green', width=0.7),
            mpf.make_addplot(mpf_df['MA_25'], color='blue',  width=0.7),
            mpf.make_addplot(mpf_df['MA_75'], color='red',   width=0.7),
        ]

        # シグナルを散布図として描画
        if not buy_signal.empty:
            apds.append(
                mpf.make_addplot(buy_signal['Close'], type='scatter', marker='^', color='lime', markersize=100)
            )
        if not sell_signal.empty:
            apds.append(
                mpf.make_addplot(sell_signal['Close'], type='scatter', marker='v', color='fuchsia', markersize=100)
            )

        # 描画
        self.fig, _ = mpf.plot(
            mpf_df,
            type='candle',  # ローソク足
            style='yahoo',
            addplot=apds,
            volume=True,
            returnfig=True,
            figsize=(10,6),
            title='Candlestick with 5/25/75MA & Buy/Sell Signals'
        )

        # Tkinterキャンバスへ
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

def main():
    root = tk.Tk()
    ttk.Style().theme_use('clam')
    app = StrategyGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
