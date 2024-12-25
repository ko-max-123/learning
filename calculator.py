import tkinter as tk

class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("電卓")
        self.resizable(True, True)  # 幅と高さを自動調整
        self.result_var = tk.StringVar()
        self.create_widgets()
        self.bind_keys()  # キーボードバインド追加

    def create_widgets(self):
        # 結果表示エリア
        self.result_entry = tk.Entry(self, textvariable=self.result_var, font=("Arial", 24), bd=10, insertwidth=2, width=14, borderwidth=4)
        self.result_entry.grid(row=0, column=0, columnspan=4, pady=(10, 20))  # 上下に余白を追加
        self.result_entry.bind("<KeyPress>", self.validate_key)  # 入力検証
        self.result_entry.bind("<BackSpace>", self.backspace)  # バックスペース対応

        # ボタン配置
        buttons = [
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
            ('0', 4, 0), ('.', 4, 1), ('+', 4, 2), ('=', 4, 3),
            ('C', 5, 0), ('←', 5, 1)
        ]

        for (text, row, col) in buttons:
            self.create_button(text, row, col)

        # 各列のサイズ自動調整
        for i in range(4):
            self.grid_columnconfigure(i, weight=1)
        for i in range(6):
            self.grid_rowconfigure(i, weight=1)

    def create_button(self, text, row, col):
        button = tk.Button(self, text=text, font=("Arial", 18), command=lambda: self.on_button_click(text))
        button.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)  # ボタンにパディングを追加

    def bind_keys(self):
        # キーバインド設定
        self.bind("<KeyPress>", self.validate_key)
        self.bind("<Return>", lambda e: self.on_button_click("="))  # Enterキーで計算
        self.bind("<BackSpace>", self.backspace)  # バックスペース
        self.bind("<Escape>", lambda e: self.on_button_click("C"))  # Escキーでクリア
        self.bind("<Left>", self.backspace)  # ←キーでバックスペース動作

    def validate_key(self, event):
        allowed_keys = '0123456789./*-+'
        # フォーカスがエントリにある場合も検証
        if self.focus_get() == self.result_entry and event.char not in allowed_keys:
            return "break"  # 不許可のキーは無効
        if event.char in allowed_keys:
            self.on_button_click(event.char)  # 許可されたキーのみ処理
        return "break"  # 入力は完全にブロック

    def backspace(self, event=None):
        current_text = self.result_var.get()
        self.result_var.set(current_text[:-1])  # 最後の文字を削除
        return "break"

    def on_button_click(self, char):
        if char == "C":
            self.result_var.set("")
        elif char == "=":
            try:
                expression = self.result_var.get()
                result = eval(expression)
                self.result_var.set(str(result)[:13])  # 最大13桁表示
            except Exception as e:
                self.result_var.set("エラー")
        elif char == "←":
            self.backspace()  # バックスペースと同様の動作
        else:
            current_text = self.result_var.get()
            if len(current_text) < 13:  # 最大13桁制限
                self.result_var.set(current_text + char)

if __name__ == "__main__":
    app = Calculator()
    app.mainloop()
