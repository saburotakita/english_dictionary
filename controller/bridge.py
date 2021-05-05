import eel
from selenium.common import exceptions

from model import csv_file
from model import exception_log
from model import longman_scraping
from model import oxford_scraping


@eel.expose
def scraping(site, import_file_name, export_file_name):
    """
    処理の流れ
    １．入力内容のチェック
    ２．ボタンを無効化
    ３．CSVファイルの読み込み
    ４．読み込み内容のチェック
    ５．スクレイピング
    ６．結果の書き出し
    ７．ボタンの有効化

    Args:
        site (str): 検索先の辞書サイト
        import_file_name (str): 入力ファイル名
        export_file_name (str): 出力ファイル名
    """

    # １．入力内容のチェック
    # ファイル名が入力されている（空文字でない）ことをチェック
    # 片方でも入力されていない場合は、ここで終了する
    if not (import_file_name and export_file_name):
        eel.change_message('error', 'ファイル名を入力してください。')
        return None

    # ２．ボタンを無効化
    eel.disable_search_button()
    eel.change_message('running', '実行中です・・・')

    # ３．CSVファイルの読み込み
    import_file = csv_file.CsvFile(import_file_name)
    # ファイルが存在するかチェック
    # 存在しなければ、ボタンを有効化して終了
    if not import_file.exist():
        eel.change_message('error', 'そのCSVファイルは存在しません。')
        eel.enable_search_button()
        return None
    # 読み込み
    # ファイルがShift-JISで読み込めるか
    try:
        words = import_file.read('shift_jis')
    except UnicodeDecodeError as e:
        eel.change_message('error', '単語ファイルはShift-JISで入力してください。')
        eel.enable_search_button()
        return None

    # ４．読み込み内容のチェック
    # 各チェックを通らなければ、ボタンを有効化して終了
    # 1つ以上の行があるかチェック
    if len(words) < 1:
        eel.change_message('error', '単語ファイルに単語が入力されていません。')
        eel.enable_search_button()
        return None

    # 単語と品詞の列があるかチェック
    if not({'単語', '品詞'} <= set(words[0].keys())):
        eel.change_message('error', '"単語"と"品詞"がファイルに含まれていません。')
        eel.enable_search_button()
        return None

    # ５．スクレイピング
    # エラーログを書き込むためのインスタンスを用意
    err_log_file = exception_log.ExceptionLog()

    try:
        # siteの値によって、検索先に使用するクラスを変更
        if site == 'oxford':
            print('oxfordの処理開始')
            result = oxford_scraping.OxfordScraping().search(words)
            print('oxfordの処理終了')
        else:
            print('longmanの処理開始')
            # 完成後、入れ替え
            # result = longman_scraping.LongmanScraping().search(words)
            result = []
            print('oxfordの処理終了')

    # よく発生するseleniumの例外をキャッチ
    # サイトへの接続時間切れ
    except exceptions.TimeoutException as e:
        eel.change_message('error', 'サイトに接続できませんでした。')
        eel.enable_search_button()
        err_log_file.write(e)
        return None
    # Webドライバー関連の例外
    except  exceptions.WebDriverException as e:
        eel.change_message('error', 'ブラウザとの接続に失敗しました。')
        eel.enable_search_button()
        err_log_file.write(e)
        return None
    # そのほか、想定外の例外をまとめて処理
    except Exception as e:
        eel.change_message('error', '英単語の取得に失敗しました。')
        eel.enable_search_button()
        err_log_file.write(e)
        return None

    # ６．結果の書き出し
    if result:
        export_file = csv_file.CsvFile(export_file_name)
        export_file.write(result, 'utf-8_sig')

    # ７．ボタンの有効化
    eel.enable_search_button()
    eel.change_message('success', '完了しました。')
