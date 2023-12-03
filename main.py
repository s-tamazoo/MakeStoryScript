import os
import cv2
import pytesseract
import numpy as np
from typing import Union
from difflib import SequenceMatcher


TESSERACT_PATH = "C:\Program Files\Tesseract-OCR"  # 環境変数のパス
VIDEO_PATH = 'data\sample1.mp4'  # 動画のパス
START_FRAME = 2 * 60    # 最初の数秒を飛ばす時間
FRAME_INTERVAL = 10  # 画像を読み取る間隔
TEST_FLAG = True    # テストフラグ
NAME_SCALE = 10     # 名前ウィンドウを拡大する倍率
TEXT_SCALE = 2     # テキストウィンドウを拡大する倍率


def SetPath() -> None:
    """環境変数にパスを通す"""

    if TESSERACT_PATH not in os.environ["PATH"].split(os.pathsep):
        os.environ["PATH"] += TESSERACT_PATH


def CaptureArea(img: np.ndarray) -> Union[int, int, int, int]:
    """指定した領域の座標と幅と高さを返す

    Args:
        img (np.ndarray): 画像データ

    Returns:
        Union[int, int, int, int]: 選択した領域のx座標, y座標, 横幅, 縦幅
    """

    x0, y0, w, h = cv2.selectROI(img)
    if x0 is None or y0 is None or w is None or h is None:
        print("トリミング領域の指定に失敗しました。")
        exit()
    cv2.destroyAllWindows()
    return x0, y0, w, h


def PreprocessImage(img: np.ndarray, scale: int, reverse_flag: bool = False) -> np.ndarray:
    """画像認識しやすい画像に加工する

    Args:
        img (np.ndarray): 画像データ
        scale (int): 画像の拡大倍率
        reverse_flag (bool): ビット反転処理フラグ

    Returns:
        np.ndarray: 加工した画像データ
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
    return cv2.resize(img, dsize=(w * scale, h * scale))


def main():

    name = ""
    prev_text = ""
    text = ""

    SetPath()
    video = cv2.VideoCapture(VIDEO_PATH)
    for i in range(START_FRAME):
        _, frame = video.read()
    name_x, name_y, name_w, name_h = CaptureArea(frame)
    text_x, text_y, text_w, text_h = CaptureArea(frame)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    for i in range(START_FRAME, frame_count):

        is_recognized, frame = video.read()

        # 一定フレーム間隔で読み取りを行う
        if i % FRAME_INTERVAL != 0 and i != frame_count - 1:
            continue

        if TEST_FLAG:
            cv2.imshow("frame", frame)

        if is_recognized:

            # テキストウィンドウの画像認識
            text_img = PreprocessImage(frame[text_y:text_y + text_h, text_x:text_x + text_w], TEXT_SCALE)
            text_config = "--psm 6, --oem 3"
            cur_text = pytesseract.image_to_string(text_img, lang="jpn", config=text_config).replace(" ", "")

            # 前のセリフとの一致率が低くなったタイミングで書き出し処理
            if SequenceMatcher(None, cur_text, prev_text).ratio() < 0.3 and prev_text != "":
                text += f'{name}{prev_text}\n'
                if TEST_FLAG:
                    print(f'{name}{prev_text}\n')

            prev_text = cur_text
            # キャラウィンドウの画像認識
            name_img = PreprocessImage(frame[name_y:name_y + name_h, name_x:name_x + name_w], NAME_SCALE, True)
            name_config = "--psm 8, --oem 3, name_whitelist.txt"
            name = pytesseract.image_to_string(name_img, lang="jpn", config=name_config).replace(" ", "")
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
