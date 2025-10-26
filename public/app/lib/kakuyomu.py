import json
import requests
import time
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)



class KakuyomuData:
    def __init__(self):
        self.url = 'https://kakuyomu.jp'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0"
        })

        return

    def get_absolute_url(self, link):
        return self.url + link

    def get_work_info(self, link: str) -> dict | None:
        response = self.session.get(link)
        data = {}
        if response.ok:
            html = BeautifulSoup(response.text, 'html.parser')
            data['id'] = link.split('/')[-1]
            data['title'] = html.select_one('h1.Heading_heading__lQ85n.Heading_left__RVp4h.Heading_size-2l__rAFn3').text
            author = html.select_one('.partialGiftWidgetActivityName a')
            data['author_name'] = author.text
            data['author_url'] = self.get_absolute_url(author['href'])
            data['first_url'] = self.get_absolute_url(html.select_one(
                '.Layout_layout__5aFuw.Layout_items-normal__4mOqD.Layout_justify-normal__zqNe7.Layout_direction-row__boh0Z.Layout_wrap-wrap__yY3zM.Layout_gap-2s__xUCm0 a')[
                                                          'href'])

            return data
        return None

    def get_episodes(self, first_url: str) -> list | None:
        episode_url = first_url
        episodes_data = []

        while True:
            logger.info(f"📥 エピソードをダウンロード中: {episode_url}")
            response = self.session.get(episode_url)
            if not response.ok:
                logger.warning(f"⚠️ エピソードの取得に失敗しました (HTTP {response.status_code})")
                break

            html = BeautifulSoup(response.text, 'html.parser')
            episode_title = html.select_one(".widget-episodeTitle").text
            episode_content = html.select_one(".widget-episodeBody").text
            episode_data = {
                "url": episode_url,
                "title": episode_title,
                "content": episode_content
            }
            episodes_data.append(episode_data)

            logger.info(f"  ✅ タイトル: {episode_title}")

            next_url = html.select_one("#contentMain-readNextEpisode")
            if not next_url:
                logger.info(f"🎉 全 {len(episodes_data)} エピソードのダウンロード完了")
                return episodes_data

            episode_url = self.get_absolute_url(next_url['href'])

            time.sleep(1)
            pass

        return episodes_data




class KakuyomuDriver:
    def __init__(self, conf: str):
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
        kakuyomu_conf = self.login_data['kakuyomu']
        if kakuyomu_conf['email'] == "" or kakuyomu_conf['password'] == "":
            logger.error("❌ メールアドレスまたはパスワードが設定されていません")
            return

        logger.info("🔐 カクヨムにログイン中...")
        self.driver.get("https://kakuyomu.jp/auth/login/email?location=%2F&auth_platform=web")
        
        wait = WebDriverWait(self.driver, 15)
        email = wait.until(EC.presence_of_element_located((By.NAME, "email")))
        password = self.driver.find_element(By.NAME, "password")

        email.send_keys(kakuyomu_conf['email'])
        password.send_keys(kakuyomu_conf['password'])

        self.driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
        time.sleep(1)
        self.driver.get("https://kakuyomu.jp/my")
        logger.info("✅ ログイン完了")
        return


    def episode_auto_input(self, work_url: str, episodes_data: list):
        # ドメインチェック
        if 'kakuyomu.jp' not in work_url:
            logger.error(f"❌ 提供されたURLはカクヨムのURLではありません: {work_url}")
            logger.error("💡 ヒント: 小説家になろうのURLを使用していませんか？")
            return

        # URL正規化（末尾スラッシュを除去して重複を防ぐ）
        work_url = work_url.rstrip('/')
        new_url = work_url + "/episodes/new"
        logger.info(f"📝 エピソード投稿URL: {new_url}")

        wait = WebDriverWait(self.driver, 15)
        total = len(episodes_data)

        for idx, episode in enumerate(episodes_data, 1):
            try:
                logger.info(f"📤 エピソード {idx}/{total} を投稿中: {episode.get('title', '(タイトルなし)')}")
                self.driver.get(new_url)
                
                # タイトルと本文の入力欄が表示されるまで待機
                logger.debug(f"現在のURL: {self.driver.current_url}")
                title_el = wait.until(EC.presence_of_element_located((By.NAME, "title")))
                body_el = wait.until(EC.presence_of_element_located((By.NAME, "body")))

                # 入力欄をクリアして新しい内容を入力
                title_el.clear()
                title_el.send_keys(episode.get('title', ''))

                body_el.clear()
                body_el.send_keys(episode.get('content', ''))

                time.sleep(0.5)
                
                # 更新/公開ボタンを探してクリック
                try:
                    update_btn = self.driver.find_element(By.ID, "updateButton")
                except NoSuchElementException:
                    logger.debug("updateButton が見つからないため、代替セレクタを試行")
                    update_btn = self.driver.find_element(By.CSS_SELECTOR, 'button[type=submit]')

                update_btn.click()
                logger.info(f"  ✅ エピソード {idx}/{total} の投稿完了")
                time.sleep(0.5)
                
            except TimeoutException:
                logger.error(f"❌ タイムアウト: タイトルまたは本文の入力欄が見つかりませんでした")
                logger.error(f"現在のURL: {self.driver.current_url}")
                logger.debug("--- ページソースの一部 ---")
                logger.debug(self.driver.page_source[:1500])
                logger.debug("--- 終了 ---")
                return
            except Exception as e:
                logger.error(f"❌ 予期しないエラーが発生しました: {e}", exc_info=True)
                return

        logger.info(f"🎉 全 {total} エピソードの投稿が完了しました！")