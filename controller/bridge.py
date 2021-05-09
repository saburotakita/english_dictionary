import sys

import eel
from selenium.common import exceptions

from model import csv_file
from model import excel_file
from model import log_file
from model import longman_scraping
from model import oxford_scraping


CLOSE = 0


@eel.expose
def run(site, import_file_name, export_file_name):
    # ボタンを無効化
    eel.disable_search_button()

    # スクレイピング
    result = scraping(site, import_file_name, export_file_name)

    # None以外は例外をログへ書き出し
    if result is not None:
        f = log_file.LogFile()
        f.write_line(str(result))

    # ボタンの有効化
    eel.enable_search_button()

    sys.exit(0)


def scraping(site, import_file_name, export_file_name):
    """
    処理の流れ
    １．入力内容のチェック
    ２．CSVファイルの読み込み
    ３．読み込み内容のチェック
    ４．スクレイピング
    ５．結果の書き出し

    Args:
        site (str): 検索先の辞書サイト
        import_file_name (str): 入力ファイル名
        export_file_name (str): 出力ファイル名
    """

    eel.change_message('running', '実行の準備をしています')

    # １．入力内容のチェック
    # ファイル名が入力されている（空文字でない）ことをチェック
    # 片方でも入力されていない場合は、ここで終了する
    if not (import_file_name and export_file_name):
        eel.change_message('error', 'ファイル名を入力してください。')
        return None

    # ２．CSVファイルの読み込み
    # 拡張子が.csvで入力されていなければ追記
    if import_file_name[3:] != '.csv':
        import_file_name += '.csv'

    import_file = csv_file.CsvFile(import_file_name)
    # ファイルが存在するかチェック
    # 存在しなければ、ボタンを有効化して終了
    if not import_file.exist():
        eel.change_message('error', 'そのCSVファイルは存在しません。')
        return None
    # 読み込み
    # ファイルがShift-JISで読み込めるか
    try:
        words = import_file.read('shift_jis')
    except UnicodeDecodeError as e:
        eel.change_message('error', '単語ファイルはShift-JISで入力してください。')
        return None

    # ３．読み込み内容のチェック
    # 各チェックを通らなければ、ボタンを有効化して終了
    # 1つ以上の行があるかチェック
    if len(words) < 1:
        eel.change_message('error', '単語ファイルに単語が入力されていません。')
        return None

    # 単語と品詞の列があるかチェック
    if not({'単語', '品詞'} <= set(words[0].keys())):
        eel.change_message('error', '"単語"と"品詞"がファイルに含まれていません。')
        return None

    # ４．スクレイピング
    # エラーログを書き込むためのインスタンスを用意
    try:
        # siteの値によって、検索先に使用するクラスを変更
        if site == 'oxford':
            result = oxford_scraping.OxfordScraping().search(words)
        else:
            result = longman_scraping.LongmanScraping().search(words)

    # よく発生するseleniumの例外をキャッチ
    # サイトへの接続時間切れ
    except exceptions.TimeoutException as e:
        eel.change_message('error', 'サイトに接続できませんでした。<br>時間をおいてからツールを再度実行してください。')
        return e
    # Webドライバー関連の例外
    except  exceptions.WebDriverException as e:
        eel.change_message('error', 'driver1ファイルとjsonファイルを削除して<br>再度ツールを実行してください。')
        return e
    # そのほか、想定外の例外をまとめて処理
    except Exception as e:
        eel.change_message('error', 'ツールの実行に失敗しました。<br>時間をおいても改善されない場合は、<br>作成されたログファイルを送ってください。')
        return e

    # ５．結果の書き出し
    # 拡張子が.xlsxで入力されていなければ追記
    if export_file_name[4:] != '.xlsx':
        export_file_name += '.xlsx'

    if result:
        export_file = excel_file.ExcelDictionaryFile(export_file_name)
        export_file.write(result)

    eel.change_message('success', '完了しました。')

    return None
