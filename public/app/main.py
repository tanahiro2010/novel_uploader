import json

from lib.kakuyomu import KakuyomuData, KakuyomuDriver
from lib.narou import NarouDriver, NarouData
from utils.choose import choose
import time
import os
import logging
from logging.handlers import RotatingFileHandler
from colorama import Fore, Back, Style, init

# Coloramaの初期化（Windows対応）
init(autoreset=True)

# カスタムカラーフォーマッタ
class ColoredFormatter(logging.Formatter):
    """ログレベルに応じて色を付けるフォーマッタ"""
    
    # ログレベルごとの色設定
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Back.WHITE + Style.BRIGHT,
    }
    
    # 絵文字とアイコン
    ICONS = {
        'DEBUG': '🔍',
        'INFO': '✨',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🚨',
    }
    
    def format(self, record):
        # ログレベルに応じた色を取得
        log_color = self.COLORS.get(record.levelname, '')
        icon = self.ICONS.get(record.levelname, '')
        
        # レベル名を色付き＋アイコン付きに
        colored_levelname = f"{log_color}{icon} {record.levelname}{Style.RESET_ALL}"
        
        # タイムスタンプを青色に
        timestamp = f"{Fore.BLUE}{self.formatTime(record, self.datefmt)}{Style.RESET_ALL}"
        
        # モジュール名をシアンに
        module_name = f"{Fore.CYAN}{record.name}{Style.RESET_ALL}"
        
        # メッセージ部分（既に絵文字が含まれている場合はそのまま）
        message = record.getMessage()
        
        # フォーマット組み立て
        formatted = f"{timestamp} | {colored_levelname:20s} | {module_name:20s} | {message}"
        
        # 例外情報があれば追加
        if record.exc_info:
            formatted += '\n' + self.formatException(record.exc_info)
        
        return formatted

# ログ設定
def setup_logging():
    # ルートロガーの設定
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # コンソール用：カラーフォーマッタ（絵文字＋色付き）
    console_formatter = ColoredFormatter(
        datefmt='%H:%M:%S'
    )
    
    # ファイル用：通常のフォーマッタ（色なし）
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # コンソールハンドラ（カラー）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # ファイルハンドラ（ログファイルに保存）
    file_handler = RotatingFileHandler(
        'syosetu_converter.log',
        maxBytes=1024*1024,  # 1MB
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Seleniumのログを抑制
    logging.getLogger('selenium').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

logger = setup_logging()


def main():
    conf_path = "../config.json"
    if not os.path.exists(conf_path):
        logger.error("設定ファイルが見つかりません")
        exit(1)

    with open("../config.json", 'r', encoding='utf-8') as f:
        conf = json.load(f)
        pass



    narou = NarouData()
    kakuyomu = KakuyomuData()

    all_options = [
        "カクヨム",
        "小説家になろう",
        "【未実装】アルファポリス",
        "【未実装】ネオページ",
        "ソフトを終了"
    ]
    allow_options = [
        "kakuyomu",
        "narou"
    ]


    print("既に掲載しているプラットフォームを選択してください >>")
    _input = choose(all_options)
    if _input == 4:
        exit()

    print("次に掲載したいプラットフォームを選択してください >>")
    _output = choose(all_options)
    if _output == 4:
        exit()

    if _input > (len(allow_options) - 1) or _output > (len(all_options) - 1):
        logger.error("選択肢が無効です")
        return

    input_mode = allow_options[_input]
    output_mode = allow_options[_output]

    logger.info(f"入力元プラットフォーム: {input_mode}")
    logger.info(f"出力先プラットフォーム: {output_mode}")

    if input_mode == output_mode:
        logger.error("同じプラットフォームを選択することはできません")
        return

    episodes = []

    if input_mode == "kakuyomu":
        print("掲載したい作品のURLを入力してください (例: https://kakuyomu.jp/works/16818622177542595290)")
        url = input(">> ")
        try:
            logger.info(f"カクヨム作品情報を取得中: {url}")
            work = kakuyomu.get_work_info(url)
            logger.info(f"作品タイトル: {work['title']}")
            episodes = kakuyomu.get_episodes(work['first_url'])
            logger.info(f"エピソード数: {len(episodes)}")
        except Exception as e:
            logger.error(f"作品が見つからない、またはURLが無効な可能性があります: {e}")
            return

        pass
    elif input_mode == "narou":
        print("掲載したい作品のncodeを入力してください (例: n5922lb)")
        ncode = input(">> ")
        try:
            logger.info(f"小説家になろう作品情報を取得中: {ncode}")
            work = narou.get_work_info(ncode)
            if work is None:
                raise ValueError("作品情報を取得できませんでした")

            logger.info(f"作品タイトル: {work['title']}")
            episodes = narou.get_episodes(work)
            logger.info(f"エピソード数: {len(episodes)}")
        except Exception as e:
            logger.error(f"作品が見つからない、またはncodeが無効な可能性があります: {e}")
            return

    print("作品管理用URLを入力してください (例: {})".format("https://kakuyomu.jp/my/works/16818622177542595290" if output_mode == "kakuyomu" else "https://syosetu.com/draftepisode/input/ncode/2875635/"))
    input_value = input(">> ")

    try:
        if output_mode == "kakuyomu":
            kakuyomu_conf = conf["kakuyomu"]
            if kakuyomu_conf["email"] == "" or kakuyomu_conf["password"] == "":
                raise ValueError("設定が入力されていません")

            logger.info("カクヨムドライバを初期化中...")
            kakuyomu_driver = KakuyomuDriver(conf_path)
            logger.info("ログイン中...")
            kakuyomu_driver.login()
            logger.info("エピソードの自動入力を開始します")
            kakuyomu_driver.episode_auto_input(input_value, episodes)
            logger.info("✨ すべてのエピソード入力が完了しました！")

        else:
            narou_conf = conf["narou"]
            if narou_conf["email"] == "" or narou_conf["password"] == "":
                raise ValueError("設定が入力されていません")

            logger.info("小説家になろうドライバを初期化中...")
            narou_driver = NarouDriver(conf_path)
            logger.info("ログイン中...")
            narou_driver.login()
            logger.info("エピソードの自動入力を開始します")
            narou_driver.episode_auto_input(input_value, episodes)
            logger.info("✨ すべてのエピソード入力が完了しました！")
    except Exception as e:
        logger.error(f"データの読み込みまたは処理に失敗しました: {e}", exc_info=True)
        exit(1)

if __name__ == '__main__':
    while True:
        main()