import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# リンク一覧ファイル名
links_file = 'links.txt'

# 出力ファイル名
output_excel = 'stock_info.xlsx'
pdf_folder = 'pdf_files'
log_file = 'error_log.txt'

# 保存フォルダ作成
os.makedirs(pdf_folder, exist_ok=True)

# ログ記録関数
def log_error(message):
    with open(log_file, 'a', encoding='utf-8') as log:
        log.write(message + '\n')

# データ保存リスト
data = []

# ブラウザ設定
options = webdriver.ChromeOptions()
options.add_argument('--log-level=3')  # ログレベル抑制
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')  # GPU無効化
options.add_argument('--disable-software-rasterizer')
options.add_experimental_option('excludeSwitches', ['enable-logging'])  # USBエラー抑制

# ダウンロードディレクトリ設定
current_dir = os.path.abspath(os.path.dirname(__file__))
download_dir = os.path.join(current_dir, pdf_folder)
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True
}
options.add_experimental_option("prefs", prefs)

# ダウンロード完了待機処理
def wait_for_downloads(download_path, timeout=30):
    end_time = time.time() + timeout
    while time.time() < end_time:
        if any([filename.endswith('.pdf') for filename in os.listdir(download_path)]):
            return True
        time.sleep(1)
    return False

# データ取得処理
def fetch_stock_info(url):
    try:
        service = Service()
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(url)
        # ページ読み込み待機
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#stockinfo_i1')))
        time.sleep(3)  # JS処理の待機

        # 銘柄コード取得
        stock_code = driver.find_element(By.CSS_SELECTOR, '#stockinfo_i1 > div.si_i1_1 > h2 > span.inline-block').text.strip()
        stock_price = driver.find_element(By.CSS_SELECTOR, '#stockinfo_i1 > div.si_i1_2 > span.kabuka').text.strip()

        # PDFリンク取得
        pdf_links = driver.find_elements(By.CSS_SELECTOR, 'div.fin_quarter_t0_d.fin_quarter_result_d > table > tbody > tr > td.fb_pdf1 > a')
        if pdf_links:
            last_link = pdf_links[-1]
            last_link.click()  # 最後のリンクをクリック
            time.sleep(5)  # PDF画面への遷移待機

            # 新しいウィンドウに切り替え
            driver.switch_to.window(driver.window_handles[-1])

            # PDFリンククリック
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#pdflink > p > a')))
            pdf_final_link = driver.find_element(By.CSS_SELECTOR, '#pdflink > p > a')
            pdf_final_link.click()
            time.sleep(10)  # PDFダウンロード待機

            # ダウンロード確認
            if wait_for_downloads(download_dir):
                latest_file = max([os.path.join(download_dir, f) for f in os.listdir(download_dir) if f.endswith('.pdf')], key=os.path.getmtime)
                dest_path = os.path.join(download_dir, f'{stock_code}.pdf')
                os.rename(latest_file, dest_path)
            else:
                log_error(f'Failed to download PDF for URL: {url}')

        else:
            log_error(f'PDF link not found for URL: {url}')

        # データ追加
        data.append({'Stock Code': stock_code, 'Price': stock_price, 'PDF': f'{stock_code}.pdf'})

    except Exception as e:
        log_error(f'Error processing URL {url}: {str(e)}')

    finally:
        # ブラウザ終了
        driver.quit()

# リンク一覧読み込み
with open(links_file, 'r') as file:
    links = [line.strip() for line in file.readlines() if line.strip()]

# 各リンクにアクセスしてデータ取得
for link in links:
    fetch_stock_info(link)

# Excelファイルに出力
if data:
    df = pd.DataFrame(data)
    df.to_excel(output_excel, index=False)

print(f'Data saved to {output_excel} and PDFs saved to {pdf_folder}.')
