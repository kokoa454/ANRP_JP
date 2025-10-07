__package__ = "DATA_SET"

import LICENSE_PLATE
import fiftyone as fo
import fiftyone.zoo as foz
import random
import json
from PIL import Image
import sys
import os

class DATA_SET:
    BACKGROUND_IMAGE_DIR = "./background_images"
    DATA_SET_IMAGES_DIR = "./data_set/images"
    DATA_SET_LABELS_DIR = "./data_set/labels"
    MAX_LICENSE_PLATES_PER_IMAGE = 3

    def __init__(self, trainingNumber, typeOfVehicle):
        trainingNumber = int(trainingNumber)
        typeOfVehicle = int(typeOfVehicle)

        self.downloadBackgroundImage(trainingNumber)

        while trainingNumber > 0:
            # self.backgroundImagePath = self.pickBackgroundImage()
            self.licensePlatePaths = self.pickLicensePlates(typeOfVehicle)
            self.dataSet = self.createDataSet(self.backgroundImagePath, self.licensePlatePaths)
            trainingNumber -= 1

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
    
    def pickLicensePlates(self, typeOfVehicle):
        licensePlatePaths = []
        
        try:
            f = open(LICENSE_PLATE.LICENSE_PLATE.LICENSE_PLATE_DIR + f"/{LICENSE_PLATE.LICENSE_PLATE.typeOfVehicleString[typeOfVehicle]}/metaData.json", "r", encoding="utf-8")
            metaData = json.load(f)

            print("\nナンバープレートを選択中...")

            licensePlateNumber = random.randint(1, self.MAX_LICENSE_PLATES_PER_IMAGE + 1)

            while licensePlateNumber > 0:
                licensePlatePaths += random.choice(metaData["imagePath"]).split(",")
                licensePlateNumber -= 1

            print("\nナンバープレートを選択完了")
        
        except FileNotFoundError:
            print("ナンバープレートの作成に失敗しました。")
            print("ナンバープレートを生成してください。")
            sys.exit()

        return licensePlatePaths
        
    def createDataSet(self, backgroundImagePath, licensePlatePaths):
        print("\nデータセットを作成中...")
        # TODO : ナンバープレートの位置決め、背景画像とナンバープレートを合成する

        print("\nデータセットを作成完了")