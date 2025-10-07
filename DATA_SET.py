__package__ = "DATA_SET"

import LICENSE_PLATE
import fiftyone as fo
import fiftyone.zoo as foz
import random
import json
from PIL import Image
import sys
import shutil
import os

class DATA_SET:
    BACKGROUND_IMAGE_DIR = "./background_images"
    DATA_SET_IMAGES_DIR = "./data_set/images"
    DATA_SET_LABELS_DIR = "./data_set/labels"
    MAX_LICENSE_PLATES_PER_IMAGE = 3

    def __init__(self, trainingNumber, typeOfVehicle):
        trainingNumber = int(trainingNumber)
        typeOfVehicle = int(typeOfVehicle)
        
        if os.path.exists(self.BACKGROUND_IMAGE_DIR):
            print("\n前回の背景画像を削除します。")
            shutil.rmtree(self.BACKGROUND_IMAGE_DIR)
            print("前回の背景画像を削除しました。")
            os.makedirs(self.BACKGROUND_IMAGE_DIR)

        if os.path.exists(self.DATA_SET_IMAGES_DIR):
            print("\n前回のデータセットを削除します。")
            shutil.rmtree(self.DATA_SET_IMAGES_DIR)
            shutil.rmtree(self.DATA_SET_LABELS_DIR)
            print("前回のデータセットを削除しました。")
            os.makedirs(self.DATA_SET_IMAGES_DIR)
            os.makedirs(self.DATA_SET_LABELS_DIR)

        self.downloadBackgroundImage(trainingNumber)

        print("\nデータセットを生成中...")
        while trainingNumber > 0:
            self.backgroundImagePath = self.pickBackgroundImage()
            self.licensePlatePaths = self.pickLicensePlates(typeOfVehicle)
            self.dataSet = self.createDataSet(self.backgroundImagePath, self.licensePlatePaths)
            trainingNumber -= 1

        print("\nデータセットを生成完了")

    def downloadBackgroundImage(self, trainingNumber):
        metaData = {"imagePath": []}

        print("\n背景画像をダウンロード中...")
        backgroundImages = foz.load_zoo_dataset(
            "open-images-v7",
            split="train",
            label_types=[],
            classes = ["Building"],
            max_samples = trainingNumber,
            shuffle = True
        )

        backgroundImages.name = f"background_image"
        backgroundImages.export(self.BACKGROUND_IMAGE_DIR, dataset_type = fo.types.ImageDirectory)

        for sample in backgroundImages:
            relativePaths = os.path.relpath(sample.filepath, self.BACKGROUND_IMAGE_DIR)
            for relativePath in relativePaths.split("\\"):
                if relativePath.endswith(".jpg"):
                    relativePath = os.path.join(self.BACKGROUND_IMAGE_DIR, relativePath)
                    relativePath = relativePath.replace("\\", "/")
                    metaData["imagePath"].append(relativePath)

        with open (f"{self.BACKGROUND_IMAGE_DIR}/metaData.json", "w", encoding="utf-8") as f:
            json.dump(metaData, f, ensure_ascii=False)

        print("\n背景画像をダウンロード完了")

        return
    
    def pickBackgroundImage(self):
        try:
            f = open(self.BACKGROUND_IMAGE_DIR + "/metaData.json", "r", encoding="utf-8")
            metaData = json.load(f)

            print("\n背景画像の選択中...")
            backgroundImage = random.choice(metaData["imagePath"])
            print("\n背景画像の選択完了")

            return backgroundImage

        except FileNotFoundError:
            print("ERROR: 背景画像をダウンロードしてください。")
            sys.exit()

    def pickLicensePlates(self, typeOfVehicle):
        licensePlatePaths = []
        
        try:
            f = open(LICENSE_PLATE.LICENSE_PLATE.LICENSE_PLATE_DIR + f"/{LICENSE_PLATE.LICENSE_PLATE.typeOfVehicleString[typeOfVehicle]}/metaData.json", "r", encoding="utf-8")
            metaData = json.load(f)

            print("\nナンバープレートの選択中...")

            licensePlateNumber = random.randint(1, self.MAX_LICENSE_PLATES_PER_IMAGE + 1)

            while licensePlateNumber > 0:
                licensePlatePaths += random.choice(metaData["imagePath"]).split(",")
                licensePlateNumber -= 1

            print("\nナンバープレートの選択完了")
        
        except FileNotFoundError:
            print("ERROR: ナンバープレートを生成してください。")
            sys.exit()

        return licensePlatePaths
        
    def createDataSet(self, backgroundImagePath, licensePlatePaths):
        print("\nデータセットを作成中...")
        # TODO : ナンバープレートの位置決め、背景画像とナンバープレートを合成する

        print("\nデータセットを作成完了")