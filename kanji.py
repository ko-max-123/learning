import tkinter as tk
from tkinter import messagebox
import random
import time

# 漢字データの読み込み
def load_kanji_data(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = [line.strip().split() for line in file.readlines()]
        return data
    except FileNotFoundError:
        messagebox.showerror("エラー", "ファイルが見つかりません。")
        exit()

# データ初期化
data = load_kanji_data("kannji.txt")
current_kanji, current_yomi = random.choice(data)

# タイマーの設定
def update_timer():
    global time_left
    if time_left > 0:
        time_left -= 1
        timer_label.config(text=f"残り時間: {time_left}秒")
        root.after(1000, update_timer)
    else:
        result_label.config(text="タイムアウト☓", fg="red")

# 回答チェック
def check_answer():
    user_input = input_entry.get()
    if user_input == current_yomi:
        result_label.config(text="正解◯", fg="green")
    else:
        result_label.config(text="間違い☓", fg="red")

# GUI初期化
root = tk.Tk()
root.title("漢字クイズアプリ")
root.geometry("800x400")

# タイマー表示
time_left = 60
timer_label = tk.Label(root, text=f"残り時間: {time_left}秒", font=("Arial", 14))
timer_label.place(x=500, y=10)

# 漢字表示エリア
kanji_label = tk.Label(root, text=current_kanji, font=("Arial", 48))
kanji_label.place(relx=0.5, rely=0.4, anchor="center")

# 読み仮名表示
yomi_label = tk.Label(root, text=current_yomi, font=("Arial", 24))
yomi_label.place(relx=0.5, rely=0.25, anchor="center")

# 入力欄とボタン
input_entry = tk.Entry(root, font=("Arial", 18))
input_entry.place(relx=0.4, rely=0.6, width=200, anchor="center")

result_label = tk.Label(root, text="", font=("Arial", 20))
result_label.place(relx=0.5, rely=0.15, anchor="center")

submit_button = tk.Button(root, text="決定", command=check_answer, font=("Arial", 14))
submit_button.place(relx=0.65, rely=0.6, anchor="center")

# タイマー開始
update_timer()

root.mainloop()
