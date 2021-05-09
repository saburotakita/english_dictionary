import datetime
import pathlib


class LogFile:
    """
    ログファイルの管理
    """
    def __init__(self, file_name=None, dir_name=None):
        if file_name is None:
            now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            file_name = f'{now}.log'

        if dir_name is None:
            dir_name = 'log'
            

        dir_path = pathlib.Path(dir_name)
        dir_path.mkdir(exist_ok=True, parents=True)

        self._path = pathlib.Path(dir_path / file_name)

    def write_line(self, message):
        """1行書き込み"""
        with self._path.open('a', encoding='utf-8_sig', newline='') as f:
            f.write(message)

    def write_lines(self, messages):
        """リストで複数行書き込み"""
        with self._path.open('a', encoding='utf-8_sig', newline='') as f:
            f.writelines(messages)

    def write_separater(self, mark='-', repeat=30):
        """区切り文字を書き込み"""
        with self._path.open('a', encoding='utf-8_sig', newline='') as f:
            f.write(f"{mark*repeat}\n")
