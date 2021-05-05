from controller.desktop import Desktop


def main():
    """
    デスクトップアプリを設定してスタート
    """
    # HTMLのルートディレクトリ
    root = 'view'
    # 最初に読み込むHTMLファイルのルートディレクトリからのパス
    endpoint = 'index.html'
    # ウィンドウサイズ
    size_x = 600
    size_y = 500
    size = (size_x, size_y)

    # パラメータを設定して起動
    desktop = Desktop(root, endpoint, size)
    desktop.start()


if __name__ == '__main__':
    main()
