import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import requests
from bs4 import BeautifulSoup
import os
import webbrowser

class ScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("定期スクレイピングアプリ")
        self.root.geometry("900x700")
        
        # スクレイピング設定
        self.scraping = False
        self.keyword = ""
        self.interval = 60  # デフォルト60秒
        self.collected_titles = set()
        self.results = []
        self.scraper_thread = None
        self.lock = threading.Lock()
        
        # テキストファイルのパス
        self.TEXT_FILE = 'collected_titles.txt'
        
        # テキストファイルから既存のタイトルを読み込む
        if os.path.exists(self.TEXT_FILE):
            with open(self.TEXT_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    self.collected_titles.add(line.strip())
        
        self.create_widgets()
        self.update_results_periodically()
    
    def create_widgets(self):
        # フレームの作成
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=10, padx=10, fill='x')
        
        # キーワード入力
        ttk.Label(control_frame, text="キーワード:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.keyword_entry = ttk.Entry(control_frame, width=30)
        self.keyword_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        # 間隔入力
        ttk.Label(control_frame, text="間隔（秒）:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.interval_entry = ttk.Entry(control_frame, width=10)
        self.interval_entry.insert(0, "60")
        self.interval_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        # スタートボタン
        self.start_button = ttk.Button(control_frame, text="スクレイピング開始", command=self.start_scraping)
        self.start_button.grid(row=0, column=2, padx=10, pady=5)
        
        # ストップボタン
        self.stop_button = ttk.Button(control_frame, text="スクレイピング停止", command=self.stop_scraping, state='disabled')
        self.stop_button.grid(row=1, column=2, padx=10, pady=5)
        
        # 結果表示用ツリービュー
        columns = ("Title", "Link", "Source")
        self.tree = ttk.Treeview(self.root, columns=columns, show='headings')
        self.tree.heading("Title", text="タイトル")
        self.tree.heading("Link", text="リンク")
        self.tree.heading("Source", text="ソース")
        self.tree.column("Title", width=500)
        self.tree.column("Link", width=250)
        self.tree.column("Source", width=100)
        self.tree.pack(pady=10, padx=10, fill='both', expand=True)
        
        # スクロールバー
        scrollbar = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        
        # ダブルクリックで元ページへ
        self.tree.bind("<Double-1>", self.open_link)
    
    def start_scraping(self):
        self.keyword = self.keyword_entry.get().strip()
        interval_str = self.interval_entry.get().strip()
        
        if not self.keyword:
            messagebox.showwarning("入力エラー", "キーワードを入力してください。")
            return
        
        try:
            self.interval = int(interval_str)
            if self.interval < 10:
                raise ValueError
        except ValueError:
            messagebox.showwarning("入力エラー", "間隔は10秒以上の整数で入力してください。")
            return
        
        if not self.scraping:
            self.scraping = True
            self.scraper_thread = threading.Thread(target=self.scrape, daemon=True)
            self.scraper_thread.start()
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            messagebox.showinfo("スクレイピング開始", f"キーワード「{self.keyword}」でスクレイピングを開始します。")
    
    def stop_scraping(self):
        if self.scraping:
            self.scraping = False
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            messagebox.showinfo("スクレイピング停止", "スクレイピングを停止しました。")
    
    def scrape(self):
        while self.scraping:
            try:
                # Yahooニュース ビジネス版
                yahoo_url = "https://finance.yahoo.co.jp/"
                yahoo_headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                }
                yahoo_response = requests.get(yahoo_url, headers=yahoo_headers)
                yahoo_soup = BeautifulSoup(yahoo_response.text, 'html.parser')
                
                # Yahooニュースの記事を抽出
                for item in yahoo_soup.select('.newsFeed_item'):
                    title_elem = item.select_one('.newsFeed_item_title')
                    link_elem = item.select_one('a')
                    if title_elem and link_elem:
                        title = title_elem.get_text().strip()
                        link = link_elem['href']
                        if self.keyword.lower() in title.lower():
                            with self.lock:
                                if title not in self.collected_titles:
                                    self.collected_titles.add(title)
                                    self.results.insert(0, {'title': title, 'link': link, 'source': 'Yahoo'})
                                    # 最新10件に制限
                                    self.results = self.results[:10]
                                    # テキストファイルに記録
                                    with open(self.TEXT_FILE, 'a', encoding='utf-8') as f:
                                        f.write(title + '\n')
                
                # Bloomberg日本版
                bloomberg_url = "https://www.bloomberg.co.jp/"
                bloomberg_headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                }
                bloomberg_response = requests.get(bloomberg_url, headers=bloomberg_headers)
                bloomberg_soup = BeautifulSoup(bloomberg_response.text, 'html.parser')
                
                # Bloombergの記事を抽出
                for item in bloomberg_soup.select('.index-module__post___3vhgV'):
                    title_elem = item.select_one('h3')
                    link_elem = item.select_one('a')
                    if title_elem and link_elem:
                        title = title_elem.get_text().strip()
                        link = link_elem['href']
                        if not link.startswith('http'):
                            link = 'https://www.bloomberg.co.jp' + link
                        if self.keyword.lower() in title.lower():
                            with self.lock:
                                if title not in self.collected_titles:
                                    self.collected_titles.add(title)
                                    self.results.insert(0, {'title': title, 'link': link, 'source': 'Bloomberg'})
                                    # 最新10件に制限
                                    self.results = self.results[:10]
                                    # テキストファイルに記録
                                    with open(self.TEXT_FILE, 'a', encoding='utf-8') as f:
                                        f.write(title + '\n')
                
                # GUIを更新
                self.root.after(0, self.update_treeview)
                # 次のスクレイピングまで待機
                time.sleep(self.interval)
            except Exception as e:
                print(f"スクレイピング中にエラーが発生しました: {e}")
                time.sleep(self.interval)
    
    def update_treeview(self):
        # ツリービューをクリア
        for item in self.tree.get_children():
            self.tree.delete(item)
        # 最新の結果を挿入
        for item in self.results:
            self.tree.insert('', 'end', values=(item['title'], item['link'], item['source']))
    
    def update_results_periodically(self):
        # 定期的にツリービューを更新
        if self.scraping:
            self.update_treeview()
        self.root.after(5000, self.update_results_periodically)  # 5秒ごとに更新
    
    def open_link(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item)
            link = item['values'][1]
            if link:
                webbrowser.open(link)

if __name__ == "__main__":
    root = tk.Tk()
    app = ScraperApp(root)
    root.mainloop()
