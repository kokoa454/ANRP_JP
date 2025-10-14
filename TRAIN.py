__package__ = "TRAIN"

from DATA_SET import DATA_SET
from ultralytics import YOLO
import os
import torch

class TRAIN:
    try:
        MODEL = YOLO("yolov12n.pt")
    except OSError:
        raise RuntimeError("ERROR: モデルの読み込みに失敗しました。")
    except FileNotFoundError:
        raise RuntimeError("ERROR: モデルが見つかりません。")
    
    MODEL_NAME = "yolov12n.pt"
    DATA_PATH = f"{DATA_SET.DATA_SET_DIR}/data.yaml"
    EPOCHS = 100
    BATCH_SIZE = 16
    IMGSZ = 640
    NAME = "license_plate_12n"
    PROJECT_PATH = "yolo_output"

    def __init__(self):
        print(f"{self.MODEL_NAME}による学習を開始します。(Epochs: {self.EPOCHS}, Batch Size: {self.BATCH_SIZE}, Image Size: {self.IMGSZ}, Name: {self.NAME})")

        if not os.path.exists(self.PROJECT_PATH):
            os.makedirs(self.PROJECT_PATH)

        try:
            results = self.MODEL.train(
            data = self.DATA_PATH,
            epochs = self.EPOCHS,
            batch = self.BATCH_SIZE,
            imgsz = self.IMGSZ,
            name = self.NAME,
            project = self.PROJECT_PATH,
        )
        except RuntimeError:
            raise RuntimeError("ERROR: 学習に失敗しました。")

        print("学習を終了しました。")
