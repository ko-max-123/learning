import tkinter as tk
from tkinter import messagebox
import random
import time
import os
import sys
import socket
import threading

# ネットワーク設定
HOST = socket.gethostbyname(socket.gethostname())
PORT = 5000
BUFFER_SIZE = 1024

# サーバーとクライアントのフラグ
is_server = False
conn = None
addr = None
client_socket = None

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
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

data = load_kanji_data(resource_path("kannji.txt"))
used_data = []
remaining_data = data[:]

# タイマーの設定
time_left = 60
running = True
player_finished = False
opponent_finished = False

# メニュー画面再表示関数
def create_main_menu():
    global root
    for widget in root.winfo_children():
        widget.destroy()

    root.title("漢字クイズアプリ")
    root.geometry("900x600")

    single_player_button = tk.Button(root, text="一人プレイ", command=start_single_player, font=("Arial", 14))
    single_player_button.place(relx=0.5, rely=0.4, anchor="center")

    multi_player_button = tk.Button(root, text="二人でプレイ", command=start_two_player, font=("Arial", 14))
    multi_player_button.place(relx=0.5, rely=0.6, anchor="center")

# サーバー起動関数
def start_server(port):
    global conn, addr, is_server
    is_server = True
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, port))
        server_socket.listen(1)
        messagebox.showinfo("サーバー起動", f"サーバーが起動しました。IP: {HOST}, ポート: {port}")
        conn, addr = server_socket.accept()
        messagebox.showinfo("接続", f"クライアント接続: {addr}")
        start_quiz()
    except Exception as e:
        messagebox.showerror("エラー", f"サーバーエラー: {str(e)}")

# クライアント接続関数
def start_client(ip, port):
    global client_socket
    try:
        if not ip:
            messagebox.showerror("エラー", "IPアドレスが入力されていません。")
            return
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))
        messagebox.showinfo("接続", "サーバーに接続しました。")
        start_quiz()
    except ConnectionRefusedError:
        messagebox.showerror("エラー", "サーバーに接続できません。サーバーが起動していることを確認してください。")
    except Exception as e:
        messagebox.showerror("エラー", f"接続エラー: {str(e)}")

# 一人プレイ開始
def start_single_player():
    for widget in root.winfo_children():
        widget.destroy()
    start_quiz(root)

# 二人プレイメニュー
def start_two_player():
    for widget in root.winfo_children():
        widget.destroy()

    server_button = tk.Button(root, text="サーバを立てる", command=lambda: threading.Thread(target=start_server, args=(5000,)).start(), font=("Arial", 14))
    server_button.place(relx=0.3, rely=0.5, anchor="center")

    ip_entry = tk.Entry(root, font=("Arial", 14))
    ip_entry.place(relx=0.5, rely=0.5, anchor="center")

    connect_button = tk.Button(root, text="サーバに接続する", command=lambda: threading.Thread(target=start_client, args=(ip_entry.get(), 5000)).start(), font=("Arial", 14))
    connect_button.place(relx=0.7, rely=0.5, anchor="center")

    # 戻るボタン追加
    back_button = tk.Button(root, text="戻る", command=create_main_menu, font=("Arial", 14))
    back_button.place(relx=0.1, rely=0.1, anchor="center")

# クイズスタート
def start_quiz(parent):
    global timer_label, kanji_label, yomi_label, input_entry, result_label, submit_button, time_left, running

    # 回答チェック関数
    def check_answer():
        global running
        user_input = input_entry.get()
        if user_input == current_yomi:
            result_label.config(text="正解◯", fg="green")
            running = False
            parent.after(2000, reset_quiz)
        else:
            result_label.config(text="間違い☓", fg="red")

    # 戻るボタン処理
    def go_back():
        global running, time_left
        running = False
        time_left = 60
        for widget in parent.winfo_children():
            widget.destroy()
        create_main_menu()

    # クイズリセット関数
    def reset_quiz():
        global time_left, running, current_kanji, current_yomi
        if remaining_data:
            item = random.choice(remaining_data)
            remaining_data.remove(item)
            current_kanji, current_yomi = item[0], item[1]
            kanji_label.config(text=current_kanji)
            yomi_label.config(text=current_yomi)
            input_entry.delete(0, tk.END)
            result_label.config(text="")
            time_left = 60
            running = True
            update_timer()
        else:
            result_label.config(text="クリア！", fg="blue")

    # タイマー更新関数
    def update_timer():
        global time_left, running
        if running and time_left > 0:
            time_left -= 1
            timer_label.config(text=f"残り時間: {time_left}秒")
            parent.after(1000, update_timer)
        elif time_left == 0:
            result_label.config(text="タイムアウト☓", fg="red")

    # GUI初期化
    parent.title("漢字クイズアプリ")
    parent.geometry("900x600")

    # タイマー表示
    timer_label = tk.Label(parent, text=f"残り時間: {time_left}秒", font=("Arial", 14))
    timer_label.place(x=500, y=10)

    # 漢字表示エリア
    kanji_label = tk.Label(parent, text="", font=("Arial", 48))
    kanji_label.place(relx=0.5, rely=0.4, anchor="center")

    # 読み仮名表示
    yomi_label = tk.Label(parent, text="", font=("Arial", 24))
    yomi_label.place(relx=0.5, rely=0.25, anchor="center")

    # 入力欄とボタン
    input_entry = tk.Entry(parent, font=("Arial", 18))
    input_entry.place(relx=0.4, rely=0.6, width=200, anchor="center")

    result_label = tk.Label(parent, text="", font=("Arial", 20))
    result_label.place(relx=0.5, rely=0.15, anchor="center")

    submit_button = tk.Button(parent, text="決定", command=check_answer, font=("Arial", 14))
    submit_button.place(relx=0.65, rely=0.6, anchor="center")

    # 戻るボタン追加
    back_button = tk.Button(parent, text="戻る", command=go_back, font=("Arial", 14))
    back_button.place(relx=0.1, rely=0.1, anchor="center")

    reset_quiz()

# メニュー画面を表示
root = tk.Tk()
create_main_menu()
root.mainloop()
