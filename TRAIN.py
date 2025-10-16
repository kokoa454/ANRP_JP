__package__ = "TRAIN"

from DATA_SET import DATA_SET
from ultralytics import YOLO
import os
import re

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
        print(f"{self.MODEL_NAME}による学習を開始します。(Epochs: {self.EPOCHS}, Batch Size: {self.BATCH_SIZE}, Image Size: {self.IMGSZ}, Name: {self.NAME})")

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
                        "last.pt"
                    )
                    
                    if os.path.exists(self.LAST_PT_PATH):
                        self.MODEL_TO_LOAD = self.LAST_PT_PATH
                    
                
                if self.MODEL_TO_LOAD:
                    self.MODEL = YOLO(self.MODEL_TO_LOAD)
                    print(f"前回の学習結果（{self.MODEL_TO_LOAD}）を読み込みました。")

                elif os.path.exists(os.path.join(self.OUTPUT_DIR, "license_plate_11n", "weights", "last.pt")):
                    self.MODEL = YOLO(os.path.join(self.OUTPUT_DIR, "license_plate_11n", "weights", "last.pt"))
                    print(f"前回の学習結果(license_plate_11n/weights/last.pt)を読み込みました。")

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
            results = self.MODEL.train(
                data = self.DATA_PATH,
                epochs = trainingNumber,
                patience = self.PATIENCE,
                batch = self.BATCH_SIZE,
                imgsz = self.IMGSZ,
                name = self.NAME,
                project = self.PROJECT_PATH,
            )
        except RuntimeError:
            raise RuntimeError("ERROR: 学習に失敗しました。")

        print("学習を終了しました。")