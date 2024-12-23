import tkinter as tk
from tkinter import filedialog, messagebox
from moviepy.editor import VideoFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.editor import VideoFileClip, vfx
import os

class MP4toGIFConverter:
    def __init__(self, master):
        self.master = master
        master.title("MP4 to GIF Converter")

        # ファイル選択ボタン
        self.select_button = tk.Button(master, text="MP4ファイルを選択", command=self.select_file)
        self.select_button.grid(row=0, column=0, padx=10, pady=10)

        # 選択されたファイルの表示
        self.file_label = tk.Label(master, text="選択されたファイル: なし")
        self.file_label.grid(row=0, column=1, padx=10, pady=10)

        # 横幅の入力
        self.width_label = tk.Label(master, text="横幅:")
        self.width_label.grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.width_entry = tk.Entry(master)
        self.width_entry.grid(row=1, column=1, padx=10, pady=5, sticky='w')
        self.width_entry.insert(0, "480")  # デフォルト値

        # 縦幅の入力
        self.height_label = tk.Label(master, text="縦幅:")
        self.height_label.grid(row=2, column=0, padx=10, pady=5, sticky='e')
        self.height_entry = tk.Entry(master)
        self.height_entry.grid(row=2, column=1, padx=10, pady=5, sticky='w')
        self.height_entry.insert(0, "270")  # デフォルト値

        # 再生速度の入力（スピード倍率）
        self.speed_label = tk.Label(master, text="再生速度倍率 (例: 1.0 は通常速度):")
        self.speed_label.grid(row=3, column=0, padx=10, pady=5, sticky='e')
        self.speed_entry = tk.Entry(master)
        self.speed_entry.grid(row=3, column=1, padx=10, pady=5, sticky='w')
        self.speed_entry.insert(0, "1.0")  # デフォルト値

        # 変換ボタン
        self.convert_button = tk.Button(master, text="GIFに変換", command=self.convert_to_gif)
        self.convert_button.grid(row=4, column=0, columnspan=2, padx=10, pady=20)

    def select_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("MP4ファイル", "*.mp4"), ("すべてのファイル", "*.*")]
        )
        if file_path:
            self.file_path = file_path
            self.file_label.config(text=f"選択されたファイル: {os.path.basename(file_path)}")
            print(f"選択されたファイルパス: {self.file_path}")  # デバッグ出力
        else:
            self.file_label.config(text="選択されたファイル: なし")
            self.file_path = None
            print("ファイルが選択されていません。")  # デバッグ出力

    def convert_to_gif(self):
        if not hasattr(self, 'file_path') or not self.file_path:
            messagebox.showerror("エラー", "MP4ファイルを選択してください。")
            print("エラー: MP4ファイルが選択されていません。")  # デバッグ出力
            return

        # ファイルの存在確認
        if not os.path.exists(self.file_path):
            messagebox.showerror("エラー", f"指定されたファイルが見つかりません:\n{self.file_path}")
            print(f"エラー: ファイルが存在しません - {self.file_path}")  # デバッグ出力
            return

        try:
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())
            speed = float(self.speed_entry.get())
            if speed <= 0:
                raise ValueError
            print(f"入力パラメータ - 横幅: {width}, 縦幅: {height}, 再生速度倍率: {speed}")  # デバッグ出力
        except ValueError:
            messagebox.showerror("エラー", "横幅、縦幅は整数、再生速度倍率は正の数値を入力してください。")
            print("エラー: パラメータの入力が無効です。")  # デバッグ出力
            return

        # 保存先ファイルの選択
        save_path = filedialog.asksaveasfilename(
            defaultextension=".gif",
            filetypes=[("GIFファイル", "*.gif")],
            initialfile=os.path.splitext(os.path.basename(self.file_path))[0] + ".gif"
        )
        if not save_path:
            print("保存がキャンセルされました。")  # デバッグ出力
            return  # 保存がキャンセルされた場合

        print(f"保存先パス: {save_path}")  # デバッグ出力

        # 保存先のディレクトリの存在確認
        save_dir = os.path.dirname(save_path)
        if not os.path.exists(save_dir):
            messagebox.showerror("エラー", f"保存先のディレクトリが存在しません:\n{save_dir}")
            print(f"エラー: 保存先ディレクトリが存在しません - {save_dir}")  # デバッグ出力
            return

        try:
            clip = VideoFileClip(self.file_path)
            print("VideoFileClip オブジェクトを作成しました。")  # デバッグ出力

            # 再生速度の調整
            if speed != 1.0:
                clip = clip.fx(vfx.speedx, speed)
                print("再生速度を調整しました。")  # デバッグ出力

            # サイズの調整
            clip = clip.resize(newsize=(width, height))
            print("動画サイズを調整しました。")  # デバッグ出力

            # GIFに書き出し
            clip.write_gif(save_path, program='ImageMagick')
            print("GIFを書き出しました。")  # デバッグ出力

            messagebox.showinfo("成功", f"GIFが正常に保存されました:\n{save_path}")
            print(f"成功: GIFが保存されました - {save_path}")  # デバッグ出力
        except Exception as e:
            messagebox.showerror("エラー", f"変換中にエラーが発生しました:\n{str(e)}")
            print(f"エラー: 変換中に例外が発生しました - {str(e)}")  # デバッグ出力

if __name__ == "__main__":
    root = tk.Tk()
    converter = MP4toGIFConverter(root)
    root.mainloop()
