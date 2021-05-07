import time

from .english_dictionary_scraping import EnglishDictionaryScraping

#beautifulsoupでの処理に変更をお願いいたします。
#書き方の問題になってしまいますが、main関数が一番下にくるようにするのが一般的かと思います。main関数で使用している関数を上に書きます。
class LongmanScraping(EnglishDictionaryScraping):
    def search(self, words):
        """
        処理の流れ
        ① 引数の単語リストごとに以下の処理を行う。
        ② 同一の単語でも品詞によって反意語、類義語が異なるため以下の処理をおこなう。
          各単語のdictentry要素から品詞名を取得し、該当する品詞かどうか調べる。品詞が引数と異なる場合返り値をNOT_FOUND_ROWにし、処理を終了する。
        ③ 品詞が一致した場合、該当のdictentry要素から必要項目を取得する
        """
        driver = self._set_driver()

        word_list = []
        for word in words:
            word_list.append(self.main(word, driver))
        driver.quit()
        return word_list
        
    def main(self,word, driver):
        results = {}
        #longman_URL
        URL = 'https://www.ldoceonline.com/jp/dictionary/'
        # URLと単語名から検索
        URL = URL + word['単語']
        # # サイトを開く
        driver.get(URL)
        # timeで対応するのではなく、waitを用いてページの読み込みが完了するまで待機するのように変更をお願いいたします。
        time.sleep(4)

        cur_url = driver.current_url
        # URLと開いたURLが一致すれば処理を開始
        if cur_url == URL:
            # dirverからdictentry要素を取得
            # while文を利用している意味がよく分かりません。for文のみではいけないのでしょうか？
            while True:
                dic = driver.find_elements_by_class_name('dictentry')
                # 取得した要素から品詞名を取得しword['品詞']と比較
                for dic_driver in dic:
                    try:
                        pos = dic_driver.find_element_by_class_name('POS').text
                        # 品詞名が一致すれば必要項目を取得
                        if pos.lstrip('OPP ') == word['品詞']:
                            results = self.get_search(word['単語'], dic_driver, driver)
                            break
                        else:
                        # 品詞名が一致しなければresultsにNOT_FOUND_ROWを返す
                            results['単語'], results['反意語'], results['類義語'], results['派生語'], results['発音（英）'], results['発音（米）'] = word['単語'], self.NOT_FOUND_ROW, self.NOT_FOUND_ROW, self.NOT_FOUND_ROW, self.NOT_FOUND_ROW, self.NOT_FOUND_ROW
                            break 
                    except:
                        pass
                break
        # URLから検索できなければresultsにNOT_FOUND_ROWを返す
        else:
            results['単語'], results['反意語'], results['類義語'], results['派生語'], results['発音（英）'], results['発音（米）'] = word['単語'], self.NOT_FOUND_ROW, self.NOT_FOUND_ROW, self.NOT_FOUND_ROW, self.NOT_FOUND_ROW, self.NOT_FOUND_ROW
        return results
    
    # 一度listに格納した後に不要な文字列を削除している理由はなにかあるのでしょうか？
    # 二度listに格納する行為をおこなうと、プログラムが格納しているlistを記憶するために無駄な容量を使用してしまいます。
    # 取得したデータから不要な文字列の削除
    def delite(self, ele_list, delite_word):
        word_list = []
        for value in ele_list:
            value = value.text
            value = value.replace(',',"")
            word_list.append(value.lstrip(delite_word))
        return word_list
    
    # joinを用いるともっときれいに書けるかと思います。
    # 取得したデータをWORD_SEPARATORで区切る
    def return_value(self, value_list):
        i = 0
        returns = ''
        while i < len(value_list):
            returns += value_list[i]
            returns += self.WORD_SEPARATOR
            i += 1
        return returns.rstrip(self.WORD_SEPARATOR)

    # 取得メイン処理
    def get_search(self, word, dic_driver, driver):
        results = {}
        # 反意語、類義語が複数あるためリストを作成
        opp_list = []
        syn_list = []
        bre_list = []

        # while文を利用している理由をお伺いしたいです。コードを見る限り、while文を使用する理由はないかと思います。
        # 反意語取得
        while True:
            opp = dic_driver.find_elements_by_class_name('OPP')
            # 反意語を取得できなければoppにNOT_FOUND_COLを代入して処理を終了
            if not opp:
                opp = self.NOT_FOUND_COL
                break
            # 取得した要素から不要な文字を削除しリストに格納
            opp_list = self.delite(opp, 'OPP ')
            # リストの中から重複を削除
            opp_list = list(set(opp_list))
            # 取得したデータをWORD_SEPARATORで区切りoppに代入
            opp = self.return_value(opp_list)
            break
        
        # こちらも同様にwhile文を使用しなくても書けるかと思います
        # 類義語取得
        while True:
            syn = dic_driver.find_elements_by_class_name('SYN')
            bre = dic_driver.find_elements_by_class_name('BREQUIV')

            # 類義語を取得できなければsynにNOT_FOUND_COLを代入して処理を終了
            if len(syn) == 0 and len(bre) == 0:
                syn = self.NOT_FOUND_COL
                break

            # 取得した要素から不要な文字を削除しリストに格納
            syn_list = self.delite(syn, '類義語 ')
            bre_list = self.delite(bre, '類義語 ')
            for value in bre_list:
                syn_list.append(value.replace('British English',''))

            # リストの中から重複を削除
            syn_list = list(set(syn_list))
            # 取得したデータをWORD_SEPARATORで区切りsynに代入
            syn = self.return_value(syn_list)
            break
        
        # exceptですべての例外を除くようにしないでください
        # 派生語取得
        try:
            wordfams = driver.find_element_by_class_name('wordfams').text
            # 不要な文字列の削除
            wordfams = wordfams.lstrip('語群 ')
            wordfams = wordfams.replace(' ', '/')
            wordfams = wordfams.replace('/≠/', ' ≠ ')
        except:
            wordfams = self.NOT_FOUND_COL

        # 発音（英）取得
        try:
            uk = dic_driver.find_element_by_class_name('speaker.brefile.fas.fa-volume-up.hideOnAmp')
            uk = uk.get_attribute("data-src-mp3")
        except:
            uk = self.NOT_FOUND_COL

        # 発音（米）取得
        try:
            us = dic_driver.find_element_by_class_name('speaker.amefile.fas.fa-volume-up.hideOnAmp')
            us = us.get_attribute("data-src-mp3")
        except:
            us = self.NOT_FOUND_COL
        
        results['単語'], results['反意語'], results['類義語'], results['派生語'], results['発音（英）'], results['発音（米）'] = word, opp, syn, wordfams, uk, us
        return results
