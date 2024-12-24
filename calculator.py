import tkinter as tk

class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("電卓")
        self.geometry("298x475")
        self.resizable(False, False)  # 幅と高さを固定
        self.result_var = tk.StringVar()
        self.create_widgets()

    def create_widgets(self):
        # 結果表示エリア
        result_entry = tk.Entry(self, textvariable=self.result_var, font=("Arial", 24), bd=10, insertwidth=2, width=14, borderwidth=4)
        result_entry.grid(row=0, column=0, columnspan=4)

        # ボタン配置
        buttons = [
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
            ('0', 4, 0), ('.', 4, 1), ('+', 4, 2), ('=', 4, 3),
            ('C', 5, 0)
        ]

        for (text, row, col) in buttons:
            self.create_button(text, row, col)

    def create_button(self, text, row, col):
        button = tk.Button(self, text=text, padx=20, pady=20, font=("Arial", 18), command=lambda: self.on_button_click(text))
        button.grid(row=row, column=col, sticky="nsew")

    def on_button_click(self, char):
        if char == "C":
            self.result_var.set("")
        elif char == "=":
            try:
                expression = self.result_var.get()
                result = eval(expression)
                self.result_var.set(result)
            except Exception as e:
                self.result_var.set("エラー")
        else:
            current_text = self.result_var.get()
            self.result_var.set(current_text + char)

if __name__ == "__main__":
    app = Calculator()
    app.mainloop()
