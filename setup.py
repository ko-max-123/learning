from cx_Freeze import setup, Executable
import sys

# GUIアプリケーションとして扱う設定
base = None
if sys.platform == "win32":
    base = "Win32GUI"

# 含めるデータファイル（kannji.txt）とパッケージ指定
options = {
    'build_exe': {
        'packages': ['tkinter', 'random', 'time', 'os', 'sys'],
        'include_files': ['kannji.txt'],  # 必要なファイルを含める
    }
}

# アプリケーションの設定
setup(
    name="漢字クイズアプリ",
    version="1.0",
    description="漢字クイズアプリケーション",
    options=options,
    executables=[Executable("kanji.py", base=base)]
)
