import csv
import pathlib


class CsvFile:
    """
    CSVファイル
    """
    def __init__(self, file_path):
        self._path = pathlib.Path(file_path)

    def exist(self):
        """ファイルの存在を確認

        Returns:
            bool: 存在する:True/存在しない:False
        """
        return self._path.is_file()
    
    def read(self, encoding):
        """読み込み

        Args:
            encoding (str): 読み込みのエンコード方式

        Returns:
            list[DictReader]: 列をキーとするDictReaderのリスト
        """
        if self.exist():
            with self._path.open('r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                return [row for row in reader]
            
    def write(self, data, encoding):
        """書き込み

        Args:
            data (list[dict]): 列をキーとする辞書のリスト
            encoding (str): 書き込みのエンコード方式
        """
        header = data[0].keys()
        with self._path.open('w', newline='', encoding=encoding) as f:
            writer = csv.DictWriter(f, header)
            writer.writeheader()
            writer.writerows(data)
