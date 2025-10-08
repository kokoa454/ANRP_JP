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
    DATA_SET_NAME = "data_set"
    MAX_LICENSE_PLATES_PER_IMAGE = 3
    MAX_CELLS_PER_IMAGE = 3

    def __init__(self, trainingNumber, typeOfVehicle):
        trainingNumber = int(trainingNumber)
        typeOfVehicle = int(typeOfVehicle)
        
        if os.path.exists(self.BACKGROUND_IMAGE_DIR):
            print("\n前回の背景画像を削除します。")
            shutil.rmtree(self.BACKGROUND_IMAGE_DIR)
            print("前回の背景画像を削除しました。")
        os.makedirs(self.BACKGROUND_IMAGE_DIR)

        if os.path.exists(self.DATA_SET_IMAGES_DIR):
            print("\n前回のデータセット(画像)を削除します。")
            shutil.rmtree(self.DATA_SET_IMAGES_DIR)
            fo.delete_datasets(self.DATA_SET_NAME)
            print("前回のデータセット(画像)を削除しました。")
        os.makedirs(self.DATA_SET_IMAGES_DIR)

        if os.path.exists(self.DATA_SET_LABELS_DIR):
            print("\n前回のデータセット(ラベル)を削除します。")
            shutil.rmtree(self.DATA_SET_LABELS_DIR)
            fo.delete_datasets(self.DATA_SET_NAME)
            print("前回のデータセット(ラベル)を削除しました。")
        os.makedirs(self.DATA_SET_LABELS_DIR)

        self.downloadBackgroundImage(trainingNumber)

        print("\nデータセットを生成中...")
        while trainingNumber > 0:
            self.backgroundImagePath = self.pickBackgroundImage()
            self.licensePlatePaths = self.pickLicensePlates(typeOfVehicle)
            self.dataSet = self.createDataSet(self.backgroundImagePath, self.licensePlatePaths)
            self.dataSet.save(self.DATA_SET_IMAGES_DIR + f"/{trainingNumber}.jpg")
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

        backgroundImages.name = self.DATA_SET_NAME
        backgroundImages.export(self.BACKGROUND_IMAGE_DIR, dataset_type = fo.types.ImageDirectory)

        for sample in backgroundImages:
            if sample.filepath.endswith(".jpg"):
                dst_path = os.path.join(self.BACKGROUND_IMAGE_DIR, os.path.basename(sample.filepath))
                shutil.copy(sample.filepath, dst_path)
                metaData["imagePath"].append(dst_path.replace("\\", "/"))
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

            licensePlateNumber = random.randint(1, self.MAX_LICENSE_PLATES_PER_IMAGE)

            while licensePlateNumber > 0:
                licensePlatePaths += random.choice(metaData["imagePath"]).split(",")
                licensePlateNumber -= 1

            print("\nナンバープレートの選択完了")
            
        except FileNotFoundError:
            print("ERROR: ナンバープレートを生成してください。")
            sys.exit()

        return licensePlatePaths
        
    def createDataSet(self, backgroundImagePath, licensePlatePaths):
        background = Image.open(backgroundImagePath)

        BACKGROUND_WIDTH = background.size[0]
        BACKGROUND_HEIGHT = background.size[1]
        isHorizontal = BACKGROUND_HEIGHT < BACKGROUND_WIDTH
        isVertical = BACKGROUND_WIDTH > BACKGROUND_HEIGHT or BACKGROUND_WIDTH == BACKGROUND_HEIGHT
        LICENSE_PLATE_WIDTH = LICENSE_PLATE.LICENSE_PLATE.LICENSE_PLATE_WIDTH
        LICENSE_PLATE_HEIGHT = LICENSE_PLATE.LICENSE_PLATE.LICENSE_PLATE_HEIGHT
        MARGIN_BETWEEN_LICENSE_PLATES = 10
        startCellCoordinateForEachLicensePlate = []
        startWidthCoordinateForEachLicensePlate = 0
        startHeightCoordinateForEachLicensePlate = 0
        # LEVEL_OF_NOISE = random.randint(1, 3)
        isUsed = False

        if isHorizontal:
            cellWidth = BACKGROUND_WIDTH // self.MAX_CELLS_PER_IMAGE - (MARGIN_BETWEEN_LICENSE_PLATES * 2)
            cellHeight = BACKGROUND_HEIGHT - (MARGIN_BETWEEN_LICENSE_PLATES * 2)
        elif isVertical:
            cellWidth = BACKGROUND_WIDTH - (MARGIN_BETWEEN_LICENSE_PLATES * 2)
            cellHeight = BACKGROUND_HEIGHT // self.MAX_CELLS_PER_IMAGE - (MARGIN_BETWEEN_LICENSE_PLATES * 2)
        else:
            cellWidth = BACKGROUND_WIDTH // self.MAX_CELLS_PER_IMAGE - (MARGIN_BETWEEN_LICENSE_PLATES * 2)
            cellHeight = BACKGROUND_HEIGHT // self.MAX_CELLS_PER_IMAGE - (MARGIN_BETWEEN_LICENSE_PLATES * 2)

        for licensePlatePath in licensePlatePaths:
            licensePlate = Image.open(licensePlatePath)
            # makeNoise(licensePlatePath, LEVEL_OF_NOISE)
            # xRotationAngle = random.randint(-10, 10)
            # yRotationAngle = random.randint(-10, 10)
            # zRotationAngle = random.randint(-10, 10)
            # rotateLicensePlate(licensePlatePath, xRotationAngle, yRotationAngle, zRotationAngle)

            if LICENSE_PLATE_WIDTH > cellWidth:
                licensePlate = licensePlate.resize(
                    (
                        cellWidth, 
                        int(licensePlate.size[1] * (cellWidth / licensePlate.size[0]))
                    )
                )
            elif LICENSE_PLATE_HEIGHT > cellHeight:
                licensePlate = licensePlate.resize(
                    (
                        int(licensePlate.size[0] * (cellHeight / licensePlate.size[1])),
                        cellHeight
                    )
                )

            startCellCoordinateForEachLicensePlate.append([startWidthCoordinateForEachLicensePlate, startHeightCoordinateForEachLicensePlate, isUsed])
            
            if isHorizontal:
                startWidthCoordinateForEachLicensePlate += cellWidth
            elif isVertical:
                startHeightCoordinateForEachLicensePlate += cellHeight
            
            while True:
                position = random.randint(0, len(startCellCoordinateForEachLicensePlate) -1)
                if startCellCoordinateForEachLicensePlate[position][2] == False:
                    background.paste(
                        licensePlate, 
                        (
                            startCellCoordinateForEachLicensePlate[position][0] + MARGIN_BETWEEN_LICENSE_PLATES, 
                            startCellCoordinateForEachLicensePlate[position][1] + MARGIN_BETWEEN_LICENSE_PLATES
                            )
                        )
                    startCellCoordinateForEachLicensePlate[position][2] = True
                    break

        return background

    # def makeNoise(licensePlatePath, levelOfNoise):

    # def rotateLicensePlate(licensePlatePath, x, y, z):