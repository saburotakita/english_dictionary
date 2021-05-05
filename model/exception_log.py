import datetime
import pathlib

class ExceptionLog:
    """
    例外のログファイル
    """

    def __init__(self):
        now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        self._path = pathlib.Path(f'error_{now}.log')

    def write(self, exception):
        """
        書き込み
        すでにあるファイルには追記をする
        ファイル名は現在時刻

        Args:
            exception (Exception): 発生した例外
        """
        with self._path.open('a', newline='') as f:
            f.write(str(exception))
            f.write('-'*20)
