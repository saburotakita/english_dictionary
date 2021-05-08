import datetime
import pathlib


class LogFile:
    def __init__(self):
        now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        self._path = pathlib.Path(f'{now}.log')

    def write_line(self, message):
        with self._path.open('a', encoding='utf-8_sig', newline='') as f:
            f.write(message)

    def write_lines(self, messages):
        with self._path.open('a', encoding='utf-8_sig', newline='') as f:
            f.writelines(messages)

    def write_separater(self, mark='-'):
        with self._path.open('a', encoding='utf-8_sig', newline='') as f:
            f.write(f"{mark*30}\n")
