
import os
import cv2
import pytesseract
import numpy as np

# ファイルの指定
video_path = 'sample.mp4'# 動画を読み込む
video = cv2.VideoCapture(video_path)

# 動画のフレーム数を取得する
frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

# セリフ部分の抜き出し
ret, frame = video.read()
cv2.namedWindow("video")
x0, y0, w, h = cv2.selectROI("video", frame)
if x0 is None or y0 is None or w is None or h is None:
    print("トリミング領域の指定に失敗しました。")
    exit()

# 60フレームごとに処理を繰り返す
for i in range(0, frame_count):

    # フレームを取得する
    ret, frame = video.read(i)  # これを呼び出すことで動画が1フレーム進んでいそう？

    # 一定フレームのときのみ動作 TODO: 何秒おきに確認するかを考える
    if i % 120 != 0:
        continue

    if ret:
        # 画像表示(テスト用)
        # cv2.imshow("frame", frame)

        # 全体抜き出し
        # roi = frame[0:frame.shape[0], 0:frame.shape[1]]

        # トリミング
        roi = frame[y0:y0 + h, x0:x0 + w]

        # OCR を使用して、画像からテキストを取得する
        text = pytesseract.image_to_string(roi, lang="jpn")

        # テキスト処理
        text = text.replace(" ", "")

        print(text)

    else:
        print('読み込めませんでした。')

    # キーボード入力を待つ
    key = cv2.waitKey(100)

    # スペースキーが押されたら終了する
    if key == 32:
        break
