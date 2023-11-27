import os
import cv2
import pytesseract
import numpy as np
from difflib import SequenceMatcher


START_FRAME = 2 * 60    # 最初の数秒を飛ばす時間
FRAME_INTERVAL = 10  # 画像を読み取る間隔
TEST_FLAG = True    # テストフラグ
TESSERACT_PATH = "C:\Program Files\Tesseract-OCR" # 環境変数のパス


def SetPath() -> None:
    """環境変数にパスを通す"""

    if TESSERACT_PATH not in os.environ["PATH"].split(os.pathsep):
        os.environ["PATH"] += TESSERACT_PATH


def CaptureArea(frame: np.ndarray) -> (int, int, int, int):
    """指定した領域の座標と幅と高さを返す

    Args:
        video (_type_): _description_

    Returns:
        x0[int], y0[int], w[int], h[int]: _description_
    """

    x0, y0, w, h = cv2.selectROI(frame)
    if x0 is None or y0 is None or w is None or h is None:
        print("トリミング領域の指定に失敗しました。")
        exit()
    cv2.destroyAllWindows()
    return x0, y0, w, h


def OcrImage(img: np.ndarray, scale: int, mode: int, reverse_flag: bool = False) -> str:
    """画像から文字を読み取る

    Args:
        img (np.ndarray): 画像データ
        scale (int): 画像の拡大倍率
        mode (int): tesseractのpsmモードの選択
        reverse_flag (bool): ビット反転処理フラグ

    Returns:
        str: 読み取った文字列
    """

    # グレースケール変換
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    threshold = 200
    cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY, dst=img)

    # ビット反転処理
    if reverse_flag:
        img = cv2.bitwise_not(img)

    # 拡大処理
    h, w = img.shape[:2]
    img = cv2.resize(img, dsize=(w * scale, h * scale))

    # 画像認識
    text = pytesseract.image_to_string(img, lang="jpn", config=f"--psm {mode}, --oem 3, name_config")

    return text.replace(" ", "")


def main():

    # 変数宣言
    prev_name = ""
    prev_text = ""
    text = ""

    # 初期化
    SetPath()

    # 動画の取り込み
    video = cv2.VideoCapture('data\sample1.mp4')

    # 動画の総フレーム数を取得する
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    # トリミングのために2秒進める
    for i in range(START_FRAME):
        ret, frame = video.read(i)

    # 各ウィンドウの領域を選択
    name_x, name_y, name_w, name_h = CaptureArea(frame)
    text_x, text_y, text_w, text_h = CaptureArea(frame)

    # 動画の読み取り処理
    for i in range(START_FRAME, frame_count): # TODO:ここでFRAME_INTERVAL刻みにすればよくね？

        # フレームを取得する
        ret, frame = video.read(i)

        # 一定フレーム間隔で読み取りを行う
        if i % FRAME_INTERVAL != 0 and i != frame_count - 1:
            continue

        # 画像表示
        if TEST_FLAG:
            cv2.imshow("frame", frame)

        # 読み取りの可否
        if ret:

            # テキスト部分を画像認識
            text_img = frame[text_y:text_y + text_h, text_x:text_x + text_w]
            cur_text = OcrImage(text_img, 2, 6)

            # 前のセリフとの一致率が低くなったタイミングで書き出し処理
            if SequenceMatcher(None, cur_text, prev_text).ratio() < 0.3:
                text += f'{prev_name}{prev_text}\n'
                if TEST_FLAG:
                    print(f'{prev_name}{prev_text}\n')

            # 1フレーム前のテキストを保持
            prev_text = cur_text

            # キャラ名を画像認識
            name_img = frame[name_y:name_y + name_h, name_x:name_x + name_w]
            prev_name = OcrImage(name_img, 6, 8, True)
        else:
            print('読み込めませんでした。')

        # スペースキーが押されたら終了する
        key = cv2.waitKey(100)
        if key == 32:
            break

    with open("output.txt", "a", encoding="utf-8") as f:
        f.write(text)


if __name__ == "__main__":
    main()
