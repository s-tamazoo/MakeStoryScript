
import os
import cv2
import pytesseract
import numpy as np

# インストール済みのTesseractのパスを通す
TESSERACT_PATH = "C:\Program Files\Tesseract-OCR"
if TESSERACT_PATH not in os.environ["PATH"].split(os.pathsep):
    os.environ["PATH"] += TESSERACT_PATH

# ファイルの指定
video_path = 'sample.mp4'# 動画を読み込む
video = cv2.VideoCapture(video_path)

# 動画のフレーム数を取得する
frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

# 60フレームごとに処理を繰り返す
for i in range(0, frame_count):

    # フレームを取得する
    ret, frame = video.read(i)  # これを呼び出すことで動画が1フレーム進んでいそう？

    # 一定フレームのときのみ動作 TODO: 何秒おきに確認するかを考える
    if i % 60 != 0 and i != frame_count - 1:
        continue

    if ret:
        # 画像表示(テスト用)
        cv2.imshow("frame", frame)

        # 全体抜き出し
        roi = frame[0:frame.shape[0], 0:frame.shape[1]]

        # OCR を使用して、画像からテキストを取得する
        text = pytesseract.image_to_string(roi, lang="jpn")

        # テキスト処理
        text = text.replace(" ", "")

        print(i, text)

    else:
        print('読み込めませんでした。')

    # キーボード入力を待つ
    key = cv2.waitKey(100)

    # スペースキーが押されたら終了する
    if key == 32:
        break
