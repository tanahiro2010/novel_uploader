import time
import json
import requests
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

class NarouData:
    def __init__(self):
        self.url = 'https://ncode.syosetu.com/{}/{}'
        self.api_url = 'https://api.syosetu.com/novelapi/api/'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0"
        })

        return

    def get_work_info(self, ncode: str):
        endpoint = self.api_url + "?ncode={}&out=json".format(ncode.lower())
        response = self.session.get(endpoint)
        body = response.json()
        if len(body) == 1:
            return None

        return body[1]

    def get_episodes(self, api_response: dict):
        ncode: str = api_response['ncode'].lower()
        all_count = api_response['general_all_no']
        episodes_data = []

        for i in range(int(all_count)):
            endpoint = self.url.format(ncode, i + 1)
            logger.info(f"📥 エピソード {i+1}/{all_count} をダウンロード中: {endpoint}")

            response = self.session.get(endpoint)
            if not response.ok:
                logger.warning(f"⚠️ エピソードの取得に失敗しました (HTTP {response.status_code})")
                break

            html = BeautifulSoup(response.text, 'html.parser')
            episode_title = html.select_one(".p-novel__title").text
            episode_content = html.select_one(".p-novel__text").text
            episodes_data.append({
                "title": episode_title,
                "content": episode_content
            })
            logger.info(f"  ✅ タイトル: {episode_title}")
            time.sleep(1)
            pass

        logger.info(f"🎉 全 {len(episodes_data)} エピソードのダウンロード完了")
        return episodes_data


class NarouDriver:
    def __init__(self, conf):
        # Seleniumのログを完全に抑制
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--log-level=3')
        options.add_argument('--disable-logging')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()
        self.driver.implicitly_wait(10)
        with open(conf, 'r', encoding='utf-8') as f:
            self.login_data = json.load(f)

        return

    def login(self):
        narou_conf = self.login_data['narou']
        logger.info("🔐 小説家になろうにログイン中...")
        self.driver.get('https://syosetu.com/login/input/')
        time.sleep(0.5)
        
        wait = WebDriverWait(self.driver, 15)
        narouid = wait.until(EC.presence_of_element_located((By.NAME, "narouid")))
        password = self.driver.find_element(By.NAME, "pass")
        
        narouid.send_keys(narou_conf['email'])
        password.send_keys(narou_conf['password'])
        time.sleep(0.5)
        self.driver.find_element(By.ID, "mainsubmit").click()
        time.sleep(1)

        if "https://syosetu.com/user2stepauth/input/authtoken/" in self.driver.current_url:
            logger.warning("🔑 二段階認証が必要です")
            input("二段階認証後、Enterキーを押してください: ")

        self.driver.get("https://syosetu.com/user/top/")
        logger.info("✅ ログイン完了")
        return

    def episode_auto_input(self, work_url: str, episode_data: list):
        # ドメインチェック
        if 'syosetu.com' not in work_url:
            logger.error(f"❌ 提供されたURLは小説家になろうのURLではありません: {work_url}")
            logger.error("💡 ヒント: カクヨムのURLを使用していませんか？")
            return

        # URL正規化
        work_url = work_url.rstrip('/')
        logger.info(f"📝 エピソード投稿URL: {work_url}")

        wait = WebDriverWait(self.driver, 15)
        total = len(episode_data)

        for idx, episode in enumerate(episode_data, 1):
            try:
                logger.info(f"📤 エピソード {idx}/{total} を投稿中: {episode.get('title', '(タイトルなし)')}")
                self.driver.get(work_url)
                time.sleep(0.5)

                # subtitle と novel の入力欄が表示されるまで待機
                subtitle = wait.until(EC.presence_of_element_located((By.NAME, "subtitle")))
                novel = wait.until(EC.presence_of_element_located((By.NAME, "novel")))

                # 入力欄をクリアして新しい内容を入力
                subtitle.clear()
                subtitle.send_keys(episode.get('title', ''))

                novel.clear()
                novel.send_keys(episode.get('content', ''))
                time.sleep(0.5)

                # 送信ボタンを探してクリック
                try:
                    btn = self.driver.find_element(By.CSS_SELECTOR, 'button[form="usernoveldatainputForm"]')
                except NoSuchElementException:
                    logger.debug("usernoveldatainputForm が見つからないため、代替セレクタを試行")
                    btn = self.driver.find_element(By.CSS_SELECTOR, 'button[type=submit]')

                btn.click()
                logger.info(f"  ✅ エピソード {idx}/{total} の投稿完了")
                time.sleep(1)
                
            except TimeoutException:
                logger.error(f"❌ タイムアウト: subtitle または novel の入力欄が見つかりませんでした")
                logger.error(f"現在のURL: {self.driver.current_url}")
                logger.debug("--- ページソースの一部 ---")
                logger.debug(self.driver.page_source[:1500])
                logger.debug("--- 終了 ---")
                return
            except Exception as e:
                logger.error(f"❌ 予期しないエラーが発生しました: {e}", exc_info=True)
                return

        logger.info(f"🎉 全 {total} エピソードの投稿が完了しました！")




if __name__ == '__main__':
    narou = NarouData()
    work = narou.get_work_info("N0417KQ")
    episodes = narou.get_episodes(work)
    print(episodes)