import time
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .english_dictionary_scraping import EnglishDictionaryScraping

URL ="https://www.oxfordlearnersdictionaries.com/definition/english/{word}_{seq}"

class OxfordScraping(EnglishDictionaryScraping):

    OPP_TEXT = "opposite"
    SYN_TEXT = "synonym"
    RESET_PERIOD= 30

    def search(self, words):
        """
        処理の流れ
        ① 引数の単語リストごとに以下の処理を行う。
        ② 同一の単語でも品詞によってURLが異なるため、以下の処理を行う。
        　 各単語の検索結果のURLを開き、該当する品詞かどうかチェックする。品詞が引数と異なる場合、URL末尾の連番をインクリメントする。
        　 該当の単語・品詞に該当するURLが存在しない場合は、クラス定数を返却値に格納する。
        　 例）doubt
            名詞：https://www.oxfordlearnersdictionaries.com/definition/english/doubt_1
            動詞：https://www.oxfordlearnersdictionaries.com/definition/english/doubt_2
        ③ ②のURLから反意語・類義語・発音（英）・発音（米）を取得する
        　 ※ Oxford辞書では派生語は取得しない。
        """

        driver = self._set_driver()

        result = []

        max_cnt = len(words)
        try:
            
            """① 引数の単語リストごとに以下の処理を行う。
            """
            for index, word in enumerate(words):
                # UIのメッセージを変更
                self._set_ui_message(max_cnt)

                # 定期的にdriverを再起動して、履歴やクッキー、cacheイメージなどを削除する
                if not ((index+1) % OxfordScraping.RESET_PERIOD):
                    driver.quit()
                    driver = self._set_driver()

                seq = 0 # URLの末尾に付ける連番
                part_of_speech = "" # 品詞

                """② 各単語の検索結果のURLを開き、該当する品詞かどうかチェックする。品詞が引数と異なる場合、URL末尾の連番をインクリメントする。
                """
                while True:
                    # URLを開く
                    seq += 1
                    driver.get(URL.format(word=word["単語"], seq=seq))
                    WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located)
                    time.sleep(1)

                    # htmlを取得する
                    html = driver.page_source.encode('utf-8_sig')
                    soup = BeautifulSoup(html, 'lxml')

                    # 品詞を取得する
                    part_of_speech = self._get_html_or_default(lambda: soup.body.select_one("div.webtop > span.pos").text.strip(), "")

                    # 指定の品詞が存在しない(単語の検索結果が存在しない)または、指定の品詞のURLを取得した場合はループ処理を抜ける
                    if part_of_speech == "" or word["品詞"] in part_of_speech:
                        break

                """③ ②のURLから反意語・類義語・発音（英）・発音（米）を取得する
                """
                # 指定の単語・品詞の組み合わせが存在しない場合
                if part_of_speech == "":
                    data = {"単語": word["単語"], "反意語": EnglishDictionaryScraping.NOT_FOUND_ROW, "類義語": EnglishDictionaryScraping.NOT_FOUND_ROW, "派生語": EnglishDictionaryScraping.NOT_FOUND_ROW, "発音（英）": EnglishDictionaryScraping.NOT_FOUND_ROW, "発音（米）": EnglishDictionaryScraping.NOT_FOUND_ROW}
                    self._write_log(data, derivative=False)
                    result.append(data)
                    continue
                
                # 発音（英）を取得する
                phons_br = self._get_html_or_default(lambda: soup.body.select_one("div.phons_br > div").attrs["data-src-mp3"], EnglishDictionaryScraping.NOT_FOUND_COL)
                # 発音（米国）を取得する
                phons_n_am = self._get_html_or_default(lambda: soup.body.select_one("div.phons_n_am > div").attrs["data-src-mp3"], EnglishDictionaryScraping.NOT_FOUND_COL)
                # 反意語を取得する
                opposite = self._get_opp_or_syn(soup, OxfordScraping.OPP_TEXT)
                # 類義語を取得する
                synonym = self._get_opp_or_syn(soup, OxfordScraping.SYN_TEXT)

                # 結果を格納する
                data = {"単語": word["単語"], "反意語": opposite, "類義語": synonym, "派生語": EnglishDictionaryScraping.NOT_FOUND_COL, "発音（英）": phons_br, "発音（米）": phons_n_am}
                self._write_log(data, derivative=False)
                result.append(data)

        finally:
            driver.quit()

        return result
        

    def _get_opp_or_syn(self, soup, opp_or_syn):
        """反意語・類義語を取得する

            Args:
                soup: 検索対象となるhtml
                opp_or_syn: 反意語または類義語。クラス定数として定義した値を使用する。

            Returns:
                反意語または類義語を区切り文字で連結した文字列。存在しない場合は、クラス定数とする。        
        """
        result_list = []

        # 反意語(oppsite)または類義語(synonym)と記載のhtmltextを取得する
        text_list = self._get_html_or_default(lambda: soup.body.select_one("#entryContent > div > ol.senses_multiple").find_all(text=opp_or_syn), [])

        # 上記で取得した全html textの親の親要素を取得し、その中にある反意語・類義語を取得する
        for text in text_list:
            parent_html = text.parent.parent
            target_text = self._get_html_or_default(lambda: parent_html.select_one("a > span > span").text.strip(), "")

            # 反意語・類義語を取得でき、かつ返却値のリストに存在しない場合は該当の値を追加する
            if target_text and not target_text in result_list:
                result_list.append(target_text)
            
        # 反意語・類義語の文字列を作成する
        # 反意語・類義語が存在する場合は、セパレータで区切った文字列を作成。存在しない場合はクラス定数を設定する。
        return EnglishDictionaryScraping.WORD_SEPARATOR.join(result_list) if result_list else EnglishDictionaryScraping.NOT_FOUND_COL

    def _get_html_or_default(self, func, default):
        """htmlから指定のセレクタに関するhtmlを取得する。
        　　指定のhtmlが存在しせずにAttributeErrorが発生する場合はデフォルトの値を設定する

            Args:
                func: 実行する関数
                default: デフォルト値

            Returns:
                実行結果
        """
        try:
            return func()
        except AttributeError as e:
            return default

