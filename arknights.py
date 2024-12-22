import pyautogui
import time
import sys
import os
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler("arknights_automation.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def click_base_button(button_image, wait_time_before_start=5, max_attempts=5, attempt_interval=2, confidence=0.8):
    """
    指定した画像を画面上で検索し、見つかった場合はクリックします。
    見つからない場合は、再試行を行います。

    :param button_image: 「基地」ボタンの画像ファイルパス
    :param wait_time_before_start: スクリプト開始前の待機時間（秒）
    :param max_attempts: ボタン検出の最大試行回数
    :param attempt_interval: 各試行間の待機時間（秒）
    :param confidence: 画像認識の信頼度
    """
    logging.info(f"{wait_time_before_start}秒後に自動操作を開始します。ゲーム画面を確認してください。")
    time.sleep(wait_time_before_start)

    if not os.path.exists(button_image):
        logging.error(f"画像が見つかりません: {button_image}")
        sys.exit(1)

    for attempt in range(1, max_attempts + 1):
        logging.info(f"試行 {attempt} / {max_attempts}: 「基地」ボタンを検索しています...")
        try:
            location = pyautogui.locateOnScreen(button_image, confidence=confidence)
            if location is not None:
                button_point = pyautogui.center(location)
                pyautogui.click(button_point.x, button_point.y)
                logging.info(f"「基地」ボタンをクリックしました: ({button_point.x}, {button_point.y})")
                return True
            else:
                logging.warning(f"試行 {attempt}: 「基地」ボタンが見つかりませんでした。信頼度={confidence}")
        except Exception as e:
            logging.error(f"エラーが発生しました: {e}")

        if attempt < max_attempts:
            logging.info(f"{attempt_interval}秒後に再試行します...")
            time.sleep(attempt_interval)

    logging.error("「基地」ボタンが指定した試行回数内で見つかりませんでした。")
    return False

def main():
    setup_logging()

    # 「基地」ボタンの画像パスを設定
    button_image = r'.\base_button.png'  # ここを実際のパスに変更してください

    # 設定
    wait_time_before_start = 5  # スクリプト開始前の待機時間（秒）
    max_attempts = 5            # 最大試行回数
    attempt_interval = 2        # 試行間の待機時間（秒）
    confidence = 0.8            # 画像認識の信頼度

    success = click_base_button(
        button_image=button_image,
        wait_time_before_start=wait_time_before_start,
        max_attempts=max_attempts,
        attempt_interval=attempt_interval,
        confidence=confidence
    )

    if not success:
        logging.error("スクリプトを終了します。設定や画像を確認してください。")
        sys.exit(1)
    else:
        logging.info("スクリプトを正常に終了しました。")

if __name__ == "__main__":
    main()
