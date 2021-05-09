import time
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .english_dictionary_scraping import EnglishDictionaryScraping

URL = 'https://www.ldoceonline.com/jp/dictionary/{word}'

class LongmanScraping(EnglishDictionaryScraping):
    def search(self, words):
        REST_PERIOD = 30
        """
        処理の流れ
        ① 引数の単語リストごとに以下の処理を行う。
        ② 同一の単語でも品詞によって反意語、類義語が異なるため以下の処理をおこなう。
          各単語のdictentry要素から品詞名を取得し、該当する品詞かどうか調べる。品詞が引数と異なる場合返り値をNOT_FOUND_ROWにし、処理を終了する。
        ③ 品詞が一致した場合、該当のdictentry要素から必要項目を取得する
        """
        driver = self._set_driver()

        word_list = []
        max_cnt = len(words)

        for index, word in enumerate(words):
            self._set_ui_message(max_cnt)

            # 定期的にドライバーを再起動
            if(index+1) % REST_PERIOD == 0:
                driver.quit()
                driver = self._set_driver()

            data = self.main(word, driver)
            word_list.append(data)

            self._write_log(data)

        driver.quit()
        return word_list

    # 必要項目取得処理
    def get_search(self, word, dic_driver, wordfams):
        results = {}
        # 反意語、類義語が複数あるためリストを作成
        opp_list = []
        syn_list = []

        # 反意語取得
        opp = dic_driver.find_all('span', class_='OPP')
        # 反意語を取得できなければoppにNOT_FOUND_COLを代入
        if not opp:
            opp = self.NOT_FOUND_COL
        else:
            for value in opp:
                opp_list.append(self.delete(value, 'OPP '))
            opp_list = list(set(opp_list))
            # 取得したデータをWORD_SEPARATORで区切りoppに代入
            opp = (self.WORD_SEPARATOR).join(opp_list)

        # 類義語取得
        syn = dic_driver.find_all('span', class_='SYN')
        bre = dic_driver.find_all('span', class_='BREQUIV')

        # 類義語を取得できなければsynにNOT_FOUND_COLを代入
        if len(syn) == 0 and len(bre) == 0:
            syn = self.NOT_FOUND_COL
        else:
            # 取得した要素から不要な文字を削除しリストに格納
            if len(syn) != 0:
                for value in syn:
                    syn_list.append(self.delete(value, '類義語 '))

            if len(bre) != 0:
                for value in bre:
                    syn_list.append(self.delete(value, '類義語 '))
            
            # リストの中から重複を削除
            syn_list = list(set(syn_list))
            # 取得したデータをWORD_SEPARATORで区切りsynに代入
            syn = (self.WORD_SEPARATOR).join(syn_list)
            
        # 派生語を取得できなければwordfamsにNOT_FOUND_COLを代入
        if not wordfams:
            wordfams = self.NOT_FOUND_COL
        else:
            wordfams = wordfams.text
            # 不要な文字の削除
            wordfams = wordfams.lstrip('語群\n')
            wordfams = wordfams.replace('  ', '')
            wordfams = wordfams.replace('\n', '')
            wordfams = wordfams.replace(' ', '/')
            wordfams = wordfams.replace('/≠/', ' ≠ ')

        # 発音（英）取得
        uk = dic_driver.find('span', class_='speaker brefile fas fa-volume-up hideOnAmp').attrs["data-src-mp3"]
        if not uk:
            uk = self.NOT_FOUND_COL

        # 発音（米）取得
        us = dic_driver.find('span', class_='speaker amefile fas fa-volume-up hideOnAmp').attrs["data-src-mp3"]
        if not us:
            us = self.NOT_FOUND_COL

        results['単語'] = word
        results['反意語'] = opp
        results['類義語'] = syn
        results['派生語'] = wordfams
        results['発音（英）'] = uk
        results['発音（米）'] = us
        return results

    # 取得したデータから不要な文字の削除
    def delete(self, value, delete_word):
        value = value.text
        value = value.lstrip(delete_word)
        value = value.replace(',',"")
        value = value.replace('British English','')
        return value
    
    def main(self, word, driver):
        pos = ''
        results = {}

        # URLを開く
        driver.get(URL.format(word=word["単語"]))
        WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located)
        time.sleep(1)

        # htmlを取得する
        html = driver.page_source.encode('utf-8_sig')
        soup = BeautifulSoup(html, 'lxml')

        # dictentry要素を取得
        dic = soup.find_all('span', class_='dictentry')

        # 取得した要素から品詞名を取得しword['品詞']と比較
        for dic_driver in dic:
            try:
                pos = dic_driver.find('span', class_='POS').text
            except:
                pass
                # 品詞名が一致すれば必要項目を取得
            if pos == ' ' + word['品詞']:
                results = self.get_search(word['単語'], dic_driver, soup.find('div', class_='wordfams'))
                break
            else:
                # 品詞名が一致しなければresultsにNOT_FOUND_ROWを返す
                results['単語'] = word['単語']
                results['反意語'] = self.NOT_FOUND_ROW
                results['類義語'] = self.NOT_FOUND_ROW
                results['派生語'] = self.NOT_FOUND_ROW
                results['発音（英）'] = self.NOT_FOUND_ROW
                results['発音（米）'] = self.NOT_FOUND_ROW
        return results