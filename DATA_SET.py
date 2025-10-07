__package__ = "DATA_SET"

import LICENSE_PLATE
import fiftyone as fo
import fiftyone.zoo as foz
import random
import json
from PIL import Image

class DATA_SET:
    LICENSE_PLATE_DIR = "./license_plate_images"
    DATA_SET_IMAGES_DIR = "./data_set/images"
    DATA_SET_LABELS_DIR = "./data_set/labels"
    MAX_LICENSE_PLATES_PER_IMAGE = 3

    def __init__(self, trainingNumber, typeOfVehicle):
        trainingNumber = int(trainingNumber)
        typeOfVehicle = int(typeOfVehicle)
        completedNumber = 0

        while trainingNumber > 0:
            completedNumber += 1
            self.backgroundImage = self.downloadBackgroundImage(completedNumber)
            self.licensePlatePaths = self.generateLicensePlates(typeOfVehicle)
            self.dataSet = self.createDataSet(self.backgroundImage, self.licensePlates)
            trainingNumber -= 1

    def downloadBackgroundImage(self, completedNumber):
        print("\n背景画像をダウンロード中...")
        backgroundImage = foz.load_zoo_dataset(
            "open-images-v7",
            split="train",
            label_types=[],
            classes = ["Building"],
            max_samples = 1,
            shuffle = True
        )

        backgroundImage.name = f"{completedNumber}"
        backgroundImage.export(DATA_SET.DATA_SET_IMAGES_DIR, dataset_type = fo.types.ImageDirectory)

        print("\n背景画像をダウンロード完了")

        return backgroundImage
    
    def generateLicensePlates(self, typeOfVehicle):
        licensePlatePaths = []

        with open(DATA_SET.LICENSE_PLATE_DIR + f"/{LICENSE_PLATE.LICENSE_PLATE.typeOfVehicleString[typeOfVehicle]}/metaData.json", "r", encoding="utf-8") as f:
            metaData = json.load(f)

        print("\nナンバープレートを作成中...")

        licensePlateNumber = random.randint(1, self.MAX_LICENSE_PLATES_PER_IMAGE + 1)

        while licensePlateNumber > 0:
            licensePlatePaths += random.choice(metaData["imagePath"]).split(",")
            licensePlateNumber -= 1

        print("\nナンバープレートを選択完了")

        return licensePlatePaths
        
    def createDataSet(self, backgroundImage, licensePlates):
        print("\nデータセットを作成中...")
        # TODO : ナンバープレートの位置決め、背景画像とナンバープレートを合成する