
import os
import cv2
import pytesseract
import numpy as np


def CaptureArea(video):

    # トリミングのために2秒進める
    for i in range(120):

        # フレームを取得する
        ret, frame = video.read(i)  # これを呼び出すことで動画が1フレーム進んでいそう？

    x0, y0, w, h = cv2.selectROI(frame)
    if x0 is None or y0 is None or w is None or h is None:
        print("トリミング領域の指定に失敗しました。")
        exit()

    return x0, y0, w, h


# インストール済みのTesseractのパスを通す
TESSERACT_PATH = "C:\Program Files\Tesseract-OCR"
if TESSERACT_PATH not in os.environ["PATH"].split(os.pathsep):
    os.environ["PATH"] += TESSERACT_PATH

# ファイルの指定
video_path = 'data\sample2.mp4'
video = cv2.VideoCapture(video_path)

# 動画のフレーム数を取得する
frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

# 1フレーム前のテキストを格納する変数の宣言
prev_text = ""
prev_name = ""

x0, y0, w, h = CaptureArea(video)

# 定数指定
TEXT_X = x0     # 245
TEXT_Y = y0     # 497
TEXT_W = w      # 787
TEXT_H = h      # 114
NAME_X = 252
NAME_Y = 454
NAME_W = 125
NAME_H = 34
TEST_FLAG = True


# 60フレームごとに処理を繰り返す
for i in range(0, frame_count):

    # フレームを取得する
    ret, frame = video.read(i)

    # 一定フレームのときのみ動作
    if i % 10 != 0 and i != frame_count - 1:
        continue

    if ret:
        # 画像表示(テスト用)
        if TEST_FLAG:
            cv2.imshow("frame", frame)

        # トリミング
        text_roi = frame[TEXT_Y:TEXT_Y + TEXT_H, TEXT_X:TEXT_X + TEXT_W]

        # OCR を使用して、画像からテキストを取得する
        cur_text = pytesseract.image_to_string(text_roi, lang="jpn")

        # テキスト処理
        cur_text = cur_text.replace(" ", "")

        # 前のセリフより短くなったタイミングで書き出し処理
        if len(cur_text) < len(prev_text) - 1:  # 画像認識の揺れでテキストが短くなる場合を考慮して-1

            # テキスト
            prev_name = prev_name.strip("\n")
            text = prev_text
            # text = f'{prev_name}:{prev_text}\n'

            # テキスト出力(テスト用)
            if TEST_FLAG:
                print(i, text)

            # テキスト保存
            with open("output.txt", "a", encoding="utf-8") as f:
                f.write(text)

        prev_text = cur_text
        name_roi = frame[NAME_Y:NAME_Y + NAME_H, NAME_X:NAME_X + NAME_W]
        prev_name = pytesseract.image_to_string(name_roi, lang="jpn")

    else:
        print('読み込めませんでした。')

    # キーボード入力を待つ
    key = cv2.waitKey(100)

    # スペースキーが押されたら終了する
    if key == 32:
        break



