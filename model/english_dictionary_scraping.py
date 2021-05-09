import eel
from selenium import webdriver
from webdriver_manager import chrome

from .log_file import LogFile


class EnglishDictionaryScraping:
    """
    英単語スクレイピングの基底クラス
    Ver.3
    使い方：
        ・各サイトごとにこのクラスを継承する
        class OxfordScraping(EnglishDictionaryScraping):
        class LongmanScraping(EnglishDictionaryScraping):

        ・作成するクラスは、このファイルと同じ階層の別ファイルに作成してください
        oxford_scraping.py
        longman_scraping.py

        ・webドライバーはこのクラスの_set_driverを利用する
        driver = self._set_driver(False)

        ・外部から呼び出すメソッドはsearchのみ
        サブクラスでオーバーライドして実装する
        同じ名前と引数で実装すればOK

        ・例外処理
        selenumで発生する例外はこのクラスを使用する側で処理をする
    """

    # クラス定数
    # 単語と品詞の組み合わせが見つからなかった場合
    NOT_FOUND_ROW = ''

    # 類義語などが見つからなかった場合
    NOT_FOUND_COL = ''

    # 複数の類義語などの区切り
    WORD_SEPARATOR = '/'
    
    def __init__(self, driver_path=None):
        """
        Args:
            driver_path (str, optional): webドライバーのパス
                未設定の場合は、自動ダウンロード
        """
        self._cnt = 0
        self._log_file = LogFile()
        self._driver_path = driver_path

    def search(self, words):
        """
        検索処理
        このメソッドをオーバーライドして実装してください

        Args:
            words (list[dict]): 検索する単語の辞書のリスト
            {
                '単語': value,
                '品詞': value,
            }

        Returns:
            (list[dict]): 1つの単語の辞書を集めたリスト
            {
                '単語': value,
                '反意語': value,
                '類義語': value,
                '派生語': value,
                '発音（英）': value,
                '発音（米）'： value,
            }
        """
        pass

    def _set_driver(self, is_headless=True):
        # Chromeドライバーの読み込み
        options = webdriver.ChromeOptions()

        # ドライバー未ダウンロードなら、読み込み
        if self._driver_path is None:
            self._driver_path = chrome.ChromeDriverManager().install()

        # ヘッドレスモード（画面非表示モード）の設定
        if is_headless:
            options.add_argument('--headless')

        # 起動オプションの設定
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('log-level=3')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--incognito')
        options.add_argument('--user-agent=Chrome/87.0.42.88')
        options.add_argument('--single-process')
        options.add_argument('--start-maximized')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-desktop-notifications')
        options.add_argument('--disable-application-cache')
        options.add_argument("--disable-extensions")
        options.add_argument('--lang=ja')

        # ChromeのWebDriverオブジェクトを作成する。
        return webdriver.Chrome(self._driver_path, options=options)

    def _set_ui_message(self, max_cnt):
        """
        UIに表示されるメッセージの更新
        ----
        実行中です・・・(5/20単語目)
        ----
        """
        self._cnt += 1
        eel.change_message('running', f'実行中です・・・({self._cnt}/{max_cnt}単語目)')

    def _write_log(self, data, opposite=True, synonym=True, derivative=True,
                   pronunciation_uk=True, pronunciation_us=True):
        """ログ書き出し

        Args:
            data (dict): 単語の検索結果
            opposite (bool, optional): 反意語を検索する設定か
            synonym (bool, optional): 類義語を検索する設定か
            derivative (bool, optional): 派生語を検索する設定か
            pronunciation_uk (bool, optional): 発音（英）を検索する設定か
            pronunciation_us (bool, optional): 発音（米）を検索する設定か

        書き出すログの形式:
            単語：run
            反意語：organize/smuggle/ladder
            類義語：見つかりませんでした
            派生語：取得しない設定です
            発音（英）：https://www...
            発音（米）：https://www...
            ------------------------------
            単語：wrong
            反意語：mistaken
            類義語：right
            派生語：取得しない設定です
            発音（英）：https://www...
            発音（米）：https://www...
            ------------------------------
        """
        messages = []

        messages.append(f"単語：{data['単語']}\n")
        messages.append(self._get_log_message(data['反意語'], '反意語', opposite))
        messages.append(self._get_log_message(data['類義語'], '類義語', synonym))
        messages.append(self._get_log_message(data['派生語'], '派生語', derivative))
        messages.append(self._get_log_message(data['発音（英）'], '発音（英）', pronunciation_uk))
        messages.append(self._get_log_message(data['発音（米）'], '発音（米）', pronunciation_us))

        self._log_file.write_lines(messages)
        self._log_file.write_separater()

    def _get_log_message(self, word, head, has_searched):
        """書き出すログを取得

        Args:
            word (str): 検索結果の単語
            head (str): どの種類を検索したか（類義語、派生語など）
            has_searched (bool): 検索する設定か

        Returns:
            [str]: 1行分のログ
                反意語：mistaken
        """
        if has_searched:
            if word == self.NOT_FOUND_COL:
                return f"{head}：見つかりませんでした\n"
            else:
                return f"{head}：{word}\n"
        else:
            return f"{head}：取得しない設定です\n"
