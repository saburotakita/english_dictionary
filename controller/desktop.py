import eel
import sys
import socket

# eel.exposeのインポート用
from . import bridge


class Desktop:
    CHROME_ARGS = [
        '--incognit',  # シークレットモード
        '--disable-http-cache',  # キャッシュ無効
        '--disable-plugins',  # プラグイン無効
        '--disable-extensions',  # 拡張機能無効
        '--disable-dev-tools',  # デベロッパーツールを無効にする
    ]

    ALLOW_EXTENSIONS = ['.html', '.css', '.js', '.ico']

    def __init__(self, root, endpoint, size):
        """
        Args:
            root (str): [description]
            endpoint (str): [description]
            size (tuple(int, int)): [description]
        """
        self._root = root
        self._endpoint = endpoint
        self._size = size

    def start(self):
        """ 開始処理 """
        eel.init(self._root, allowed_extensions=Desktop.ALLOW_EXTENSIONS)

        # 未使用ポート取得
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', 0))
        port = s.getsockname()[1]
        s.close()

        options = {
            'mode': "chrome",
            'close_callback': self.exit,
            'port': port,
            'cmdline_args': Desktop.CHROME_ARGS
        }

        eel.start(self._endpoint, options=options,
                    size=self._size, suppress_error=True)

    def exit(self, arg1, arg2):
        """ 終了処理 """
        sys.exit(0)
