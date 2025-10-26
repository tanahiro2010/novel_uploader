import os
import sys

# --- Windows用 ---
if os.name == 'nt':
    import msvcrt
    def get_key():
        ch1 = msvcrt.getch()
        if ch1 == b'\xe0':  # 矢印キー
            ch2 = msvcrt.getch()
            if ch2 == b'H': return 'UP'
            if ch2 == b'P': return 'DOWN'
        elif ch1 == b'\r':  # Enter
            return 'ENTER'
        return None

# --- Unix系 (Mac/Linux) 用 ---
else:
    import tty, termios
    def get_key():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch1 = sys.stdin.read(1)
            if ch1 == '\x1b':
                ch2 = sys.stdin.read(1)
                ch3 = sys.stdin.read(1)
                if ch2 == '[':
                    if ch3 == 'A': return 'UP'
                    if ch3 == 'B': return 'DOWN'
            elif ch1 == '\n':
                return 'ENTER'
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return None


def choose(options):
    """矢印キーで選んでEnterで決定。返り値は選んだインデックス。"""
    idx = 0
    # 最初に選択肢を描画
    for i, option in enumerate(options):
        prefix = "> " if i == idx else "  "
        print(f"{prefix}{option}")

    while True:
        # カーソルを選択肢の行数分だけ戻す
        sys.stdout.write(f"\033[{len(options)}A")
        sys.stdout.flush()

        # 選択肢を再描画
        for i, option in enumerate(options):
            prefix = "> " if i == idx else "  "
            print(f"{prefix}{option}")

        key = get_key()
        if key == 'UP':
            idx = (idx - 1) % len(options)
        elif key == 'DOWN':
            idx = (idx + 1) % len(options)
        elif key == 'ENTER':
            return idx


if __name__ == "__main__":
    print("フルーツを選んでください:")
    fruits = ["りんご", "バナナ", "みかん", "ぶどう"]
    choice = choose(fruits)
    print("選ばれたインデックス:", choice)
    print("選ばれたフルーツ:", fruits[choice])
