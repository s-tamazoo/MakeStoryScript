import os
import cv2
import pytesseract
import numpy as np


def Init() -> None:
    """インストール済みのTesseractのパスを通す
    """
    
    TESSERACT_PATH = "C:\Program Files\Tesseract-OCR"
    if TESSERACT_PATH not in os.environ["PATH"].split(os.pathsep):
        os.environ["PATH"] += TESSERACT_PATH


def CaptureArea(frame):
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


def main():

    # 定数宣言
    START_FRAME = 2 * 60    # 最初の数秒を飛ばす時間
    FRAME_INTERVAL = 10 # 画像を読み取る間隔
    TEST_FLAG = True    # テスト用の定数

    # 変数宣言
    prev_name = ""
    prev_text = ""
    text = ""

    # 初期化
    Init()

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
    for i in range(START_FRAME, frame_count):

        # フレームを取得する
        ret, frame = video.read(i)

        # 一定フレーム間隔で読み取りを行う
        if i % FRAME_INTERVAL != 0 and i != frame_count - 1:
            continue

        # 画像表示(テスト用)
        if TEST_FLAG:
            cv2.imshow("frame", frame)

        # 読み取りの可否
        if ret:

            # テキスト部分を画像認識
            text_roi = frame[text_y:text_y + text_h, text_x:text_x + text_w] # TODO:関数化
            text_roi = cv2.cvtColor(text_roi, cv2.COLOR_BGR2GRAY)
            cv2.threshold(text_roi, 200, 255, cv2.THRESH_BINARY, dst=text_roi)
            h, w = text_roi.shape[:2]
            text_roi = cv2.resize(text_roi, dsize=(w*2, h*2))
            if TEST_FLAG:
                cv2.imshow("text_roi", text_roi)
            cur_text = pytesseract.image_to_string(text_roi, lang="jpn", config="--psm 6, --oem 3")
            cur_text = cur_text.replace(" ", "")

            # 前のセリフより短くなったタイミングで書き出し処理
            if len(cur_text) < len(prev_text) - 2:  # 画像認識の揺れでテキストが短くなる場合を考慮して-2

                text += f'{prev_name}{prev_text}\n'
                if TEST_FLAG:
                    print(text)

            # 1フレーム前のテキストを保持
            prev_text = cur_text

            # キャラ名部分を画像認識
            name = frame[name_y:name_y + name_h, name_x:name_x + name_w]    # TODO:関数化
            name = cv2.cvtColor(name, cv2.COLOR_BGR2GRAY)
            cv2.threshold(name, 200, 255, cv2.THRESH_BINARY, dst=name)
            name = cv2.bitwise_not(name)

            # nameのサイズを6倍
            h, w = name.shape[:2]
            name = cv2.resize(name, dsize=(w*6, h*6))
            if TEST_FLAG:
                cv2.imshow("name", name)
            prev_name = pytesseract.image_to_string(name, lang="jpn", config="--psm 8, --oem 3, name_config")
            prev_name = prev_name.replace(" ", "")
        else:
            print('読み込めませんでした。')

        # スペースキーが押されたら終了する
        key = cv2.waitKey(100)
        if key == 32:
            with open("output.txt", "a", encoding="utf-8") as f:
                f.write(text)
            break

    with open("output.txt", "a", encoding="utf-8") as f:
        f.write(text)


if __name__ == "__main__":
    main()
