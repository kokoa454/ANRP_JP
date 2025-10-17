__package__ = "TRAIN"

from DATA_SET import DATA_SET
from ultralytics import YOLO
import os
import re
import torch

class TRAIN:
    OUTPUT_DIR = "./yolo_output"
    MODEL_TO_LOAD = None
    LAST_PT_PATH = None
    MODEL_NAME = "yolo11n"
    DATA_PATH = f"{DATA_SET.DATA_SET_DIR}/data.yaml"
    PATIENCE = 10
    BATCH_SIZE = 16
    IMGSZ = 640
    NAME = "license_plate_11n"
    PROJECT_PATH = "yolo_output"

    def __init__(self, trainingNumber):
        trainingNumber = int(trainingNumber)
        print(f"{self.MODEL_NAME}による学習を開始します。(Epochs: {trainingNumber}, Batch Size: {self.BATCH_SIZE}, Image Size: {self.IMGSZ}, Name: {self.NAME})")

        if not os.path.exists(self.PROJECT_PATH):
            os.makedirs(self.PROJECT_PATH)

        try:
            if os.path.exists(self.OUTPUT_DIR):
                folderNames = os.listdir(self.OUTPUT_DIR)
                
                pattern = re.compile(r'^(license_plate_11n)(\d+)$') 
                
                numbered_folders = []
                for name in folderNames:
                    match = pattern.match(name)
                    if match:
                        number = int(match.group(2))
                        numbered_folders.append((number, name))

                if numbered_folders:
                    latest_folder_name = max(numbered_folders)[1] 
                    
                    self.LAST_PT_PATH = os.path.join(
                        self.OUTPUT_DIR,
                        latest_folder_name,
                        "weights",
                        "best.pt"
                    )
                    
                    if os.path.exists(self.LAST_PT_PATH):
                        self.MODEL_TO_LOAD = self.LAST_PT_PATH
                    
                
                if self.MODEL_TO_LOAD:
                    self.MODEL = YOLO(self.MODEL_TO_LOAD)
                    print(f"前回の学習結果（{self.MODEL_TO_LOAD}）を読み込みました。")

                elif os.path.exists(os.path.join(self.OUTPUT_DIR, "license_plate_11n", "weights", "best.pt")):
                    self.MODEL = YOLO(os.path.join(self.OUTPUT_DIR, "license_plate_11n", "weights", "best.pt"))
                    print(f"前回の学習結果(license_plate_11n/weights/best.pt)を読み込みました。")

                else:
                    self.MODEL = YOLO("yolo11n.pt")
                    print(f"既存の重みが見つからなかったため、yolo11n.pt で新規に学習します。")

            else:
                self.MODEL = YOLO("yolo11n.pt")
                print(f"新規に学習します。")
                
        except OSError:
            raise RuntimeError("ERROR: モデルの読み込みに失敗しました。")
        except FileNotFoundError:
            raise RuntimeError("ERROR: モデルが見つかりません。")

        try:
            if(torch.cuda.is_available()): # ultralyticsをインストール後、pytorchがcpu版の場合、pytorchだけを一度消し、pytorchだけを新たに再インストール(cuda13.0だったらcu130)を行う必要がある
                device = 0
                print("GPUで学習を始めます。")
            else:
                device = "cpu"
                print("CPUで学習を始めます。")
            results = self.MODEL.train(
                    data = self.DATA_PATH,
                    epochs = trainingNumber,
                    patience = self.PATIENCE,
                    batch = self.BATCH_SIZE,
                    imgsz = self.IMGSZ,
                    name = self.NAME,
                    project = self.PROJECT_PATH,
                    workers = 0,
                    device = device,
                    cache = True
                )
        except RuntimeError:
            raise RuntimeError("ERROR: 学習に失敗しました。")

        print("学習を終了しました。")