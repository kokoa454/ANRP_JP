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
import numpy as np
import cv2

class DATA_SET:
    BACKGROUND_IMAGE_DIR = "./background_images"
    DATA_SET_IMAGES_DIR = "./data_set/images"
    DATA_SET_LABELS_DIR = "./data_set/labels"
    DATA_SET_NAME = "data_set"
    MAX_LICENSE_PLATES_PER_IMAGE = 3
    MAX_CELLS_PER_IMAGE = 3

    def __init__(self, trainingNumber):
        trainingNumber = int(trainingNumber)
        
        if os.path.exists(self.BACKGROUND_IMAGE_DIR):
            print("\n前回の背景画像を削除します。")
            shutil.rmtree(self.BACKGROUND_IMAGE_DIR)
            print("前回の背景画像を削除しました。")
        os.makedirs(self.BACKGROUND_IMAGE_DIR)

        if os.path.exists(self.DATA_SET_IMAGES_DIR):
            print("\n前回のデータセット(画像)を削除します。")
            fo.delete_datasets(self.DATA_SET_NAME)
            shutil.rmtree(self.DATA_SET_IMAGES_DIR)
            print("前回のデータセット(画像)を削除しました。")
        os.makedirs(self.DATA_SET_IMAGES_DIR)

        if os.path.exists(self.DATA_SET_LABELS_DIR):
            print("\n前回のデータセット(ラベル)を削除します。")
            shutil.rmtree(self.DATA_SET_LABELS_DIR)
            print("前回のデータセット(ラベル)を削除しました。")
        os.makedirs(self.DATA_SET_LABELS_DIR)

        self.downloadBackgroundImage(trainingNumber)

        print("\nデータセットの生成中...")
        for imageNumber in range(1, trainingNumber + 1):
            self.backgroundImagePath = self.pickBackgroundImage()
            self.licensePlatePaths = self.pickLicensePlates()
            self.dataSet = self.createDataSet(self.backgroundImagePath, self.licensePlatePaths, imageNumber)
            self.dataSet.save(self.DATA_SET_IMAGES_DIR + f"/{imageNumber:06}.jpg")

        print("\nデータセットの生成完了")

    def downloadBackgroundImage(self, trainingNumber):
        metaData = {"imagePath": []}

        print("\n背景画像のダウンロード中...")
        backgroundImages = foz.load_zoo_dataset(
            "open-images-v7",
            split="train",
            label_types=[],
            classes = [
                "Skyscraper",
                "Tower",
                "House",
                "Office building",
                "Convenience store"
            ],
            max_samples = trainingNumber,
            shuffle = True
        )

        backgroundImages.name = self.DATA_SET_NAME
        backgroundImages.export(self.BACKGROUND_IMAGE_DIR, dataset_type = fo.types.ImageDirectory)

        for sample in backgroundImages:
            if sample.filepath.lower().endswith((".jpg", ".jpeg", ".png")):
                uniqueName = f"{len(metaData['imagePath']):06}_{os.path.basename(sample.filepath)}"
                dst_path = os.path.join(self.BACKGROUND_IMAGE_DIR, uniqueName)
                shutil.copy(sample.filepath, dst_path)
                metaData["imagePath"].append(dst_path.replace("\\", "/"))

        try:
            with open (f"{self.BACKGROUND_IMAGE_DIR}/metaData.json", "w", encoding="utf-8") as f:
                json.dump(metaData, f, ensure_ascii=False)
        except Exception as e:
            raise RuntimeError("ERROR: メタデータの保存に失敗しました。")

        print("\n背景画像のダウンロード完了")

        return
    
    def pickBackgroundImage(self):
        try:
            with open(self.BACKGROUND_IMAGE_DIR + "/metaData.json", "r", encoding="utf-8") as f:
                metaData = json.load(f)

            print("\n背景画像の選択中...")
            backgroundImage = random.choice(metaData["imagePath"])
            print("\n背景画像の選択完了")

            return backgroundImage

        except FileNotFoundError:
            print("ERROR: 背景画像をダウンロードしてください。")
            raise RuntimeError("背景画像が見つかりません。")
        
        except json.JSONDecodeError:
            print("ERROR: 背景画像のメタデータが破損しています。")
            raise RuntimeError("再度生成してください。")

    def pickLicensePlates(self):
        licensePlatePaths = []
        
        try:
            with open(LICENSE_PLATE.LICENSE_PLATE.LICENSE_PLATE_DIR + "/metaData.json", "r", encoding="utf-8") as f:
                metaData = json.load(f)

            print("\nナンバープレートの選択中...")

            licensePlateNumber = random.randint(1, self.MAX_LICENSE_PLATES_PER_IMAGE)

            while licensePlateNumber > 0:
                typeOfVehicle = random.randint(0, len(LICENSE_PLATE.LICENSE_PLATE.TYPE_OF_VEHICLE_STRING) - 1)
                licensePlatePaths += random.choice(metaData["imagePath_" + LICENSE_PLATE.LICENSE_PLATE.TYPE_OF_VEHICLE_STRING[typeOfVehicle]]).split(",")
                licensePlateNumber -= 1

            print("\nナンバープレートの選択完了")
            
        except FileNotFoundError:
            print("ERROR: ナンバープレートを生成してください。")
            raise RuntimeError("ナンバープレートが見つかりません。")
        
        except json.JSONDecodeError:
            print("ERROR: ナンバープレートのメタデータが破損しています。")
            raise RuntimeError("再度生成してください。")

        return licensePlatePaths
        
    def createDataSet(self, backgroundImagePath, licensePlatePaths, imageNumber):
        background = Image.open(backgroundImagePath).convert("RGB")

        BACKGROUND_WIDTH = background.size[0]
        BACKGROUND_HEIGHT = background.size[1]
        isHorizontal = BACKGROUND_WIDTH > BACKGROUND_HEIGHT or BACKGROUND_WIDTH == BACKGROUND_HEIGHT
        isVertical = BACKGROUND_WIDTH < BACKGROUND_HEIGHT
        LICENSE_PLATE_WIDTH = LICENSE_PLATE.LICENSE_PLATE.LICENSE_PLATE_WIDTH
        LICENSE_PLATE_HEIGHT = LICENSE_PLATE.LICENSE_PLATE.LICENSE_PLATE_HEIGHT
        MARGIN = 10
        cellWidth = 0
        cellHeight = 0
        startCoordinateForEachLicensePlate = []
        startXCoordinate = 0
        startYCoordinate = 0
        isUsed = False

        if isHorizontal:
            cellWidth = BACKGROUND_WIDTH // self.MAX_CELLS_PER_IMAGE
            cellHeight = BACKGROUND_HEIGHT
        elif isVertical:
            cellWidth = BACKGROUND_WIDTH
            cellHeight = BACKGROUND_HEIGHT // self.MAX_CELLS_PER_IMAGE

        for cell in range(self.MAX_CELLS_PER_IMAGE):
            if isHorizontal:
                cellX = startXCoordinate + MARGIN
                cellY = random.randint(MARGIN, max(MARGIN, cellHeight - LICENSE_PLATE_HEIGHT - MARGIN))
                startXCoordinate += cellWidth
            else:
                cellX = random.randint(MARGIN, max(MARGIN, cellWidth - LICENSE_PLATE_WIDTH - MARGIN))
                cellY = startYCoordinate + random.randint(MARGIN, max(MARGIN, cellHeight - LICENSE_PLATE_HEIGHT - MARGIN))
                startYCoordinate += cellHeight
            
            startCoordinateForEachLicensePlate.append((cellX, cellY , isUsed))

        for i, licensePlatePath in enumerate(licensePlatePaths):
            licensePlate = Image.open(licensePlatePath).convert("RGBA")

            rotateOrNot = random.randint(0, 2)
            rotationXAngle = 0
            rotationYAngle = 0
            
            if rotateOrNot == 1:
                rotationXAngle = random.randint(-40, 40)
                if rotationXAngle != 0:
                    licensePlate = self.rotateLicensePlate(licensePlate, rotationXAngle, 0)
            elif rotateOrNot == 2:
                rotationYAngle = random.randint(-40, 40)
                if rotationYAngle != 0:
                    licensePlate = self.rotateLicensePlate(licensePlate, 0, rotationYAngle)

            levelOfNoise = random.randint(0, 5)
            if levelOfNoise > 0:
                licensePlate = self.makeNoise(licensePlate, levelOfNoise)

            currentLicensePlateWidth = licensePlate.size[0]
            currentLicensePlateHeight = licensePlate.size[1]
            
            maxLicensePlateWidth = max(1, cellWidth - (MARGIN * 2))
            maxLicensePlateHeight = max(1, cellHeight - (MARGIN * 2))

            if currentLicensePlateWidth > maxLicensePlateWidth or currentLicensePlateHeight > maxLicensePlateHeight:
                scale = min(maxLicensePlateWidth / currentLicensePlateWidth, maxLicensePlateHeight / currentLicensePlateHeight)
                newLicensePlateWidth = max(1, int(currentLicensePlateWidth * scale))
                newLicensePlateHeight = max(1, int(currentLicensePlateHeight * scale))
                licensePlate = licensePlate.resize((newLicensePlateWidth, newLicensePlateHeight))

            if i < len(startCoordinateForEachLicensePlate):
                licensePlateX = startCoordinateForEachLicensePlate[i][0]
                licensePlateY = startCoordinateForEachLicensePlate[i][1]
            else:
                licensePlateX = random.randint(MARGIN, max(MARGIN, BACKGROUND_WIDTH - licensePlate.size[0] - MARGIN))
                licensePlateY = random.randint(MARGIN, max(MARGIN, BACKGROUND_HEIGHT - licensePlate.size[1] - MARGIN))

            background.paste(licensePlate, (licensePlateX, licensePlateY), licensePlate)

            self.createLabels(
                classId = 0,
                imageNumber = imageNumber,
                xCenter = (licensePlateX + (licensePlate.size[0] / 2)) / BACKGROUND_WIDTH,
                yCenter = (licensePlateY + (licensePlate.size[1] / 2)) / BACKGROUND_HEIGHT,
                width = licensePlate.size[0] / BACKGROUND_WIDTH,
                height = licensePlate.size[1] / BACKGROUND_HEIGHT
            )

        return background

    def makeNoise(self, licensePlate, levelOfNoise):
        npLicensePlate = np.array(licensePlate)
        noise = np.random.randint(-levelOfNoise * 10, levelOfNoise * 10, npLicensePlate.shape, dtype='int16')
        noisyLicensePlate = np.clip(npLicensePlate.astype('int16') + noise, 0, 255).astype('uint8')
        return Image.fromarray(noisyLicensePlate)
    
    def rotateLicensePlate(self, licensePlate, rotationXAngle, rotationYAngle):
        npLicensePlate = np.array(licensePlate)
        licensePlateHeight, licensePlateWidth = npLicensePlate.shape[:2]
        focalLength = max(licensePlateWidth, licensePlateHeight) * 1.5 
        centerX = licensePlateWidth / 2
        centerY = licensePlateHeight / 2
        z = 0 

        srcPoints3D = np.float32([
            [-centerX, -centerY, z],
            [ centerX, -centerY, z],
            [ centerX,  centerY, z],
            [-centerX,  centerY, z]
        ])

        dstPoints = []
        radianX = np.deg2rad(rotationXAngle)
        radianY = np.deg2rad(rotationYAngle)

        rotationXMatrix = np.array([
            [1, 0, 0],
            [0, np.cos(radianX), -np.sin(radianX)],
            [0, np.sin(radianX), np.cos(radianX)]
        ])

        rotationYMatrix = np.array([
            [np.cos(radianY), 0, np.sin(radianY)],
            [0, 1, 0],
            [-np.sin(radianY), 0, np.cos(radianY)]
        ])

        finalRotationMatrix = np.identity(3)

        if rotationXAngle != 0:
            finalRotationMatrix = rotationXMatrix
        elif rotationYAngle != 0:
            finalRotationMatrix = rotationYMatrix

        for x, y, z_val in srcPoints3D:
            rotatedPoint = finalRotationMatrix @ np.array([x, y, z_val])
            Z_prime = rotatedPoint[2] + focalLength 
            if Z_prime == 0: Z_prime = 1e-6 
            
            x_proj = (focalLength * rotatedPoint[0] / Z_prime) + centerX
            y_proj = (focalLength * rotatedPoint[1] / Z_prime) + centerY
            
            dstPoints.append([x_proj, y_proj])
            
        dstPoint = np.float32(dstPoints)
        
        srcPoint = np.float32([
            [0, 0],
            [licensePlateWidth - 1, 0],
            [licensePlateWidth - 1, licensePlateHeight - 1],
            [0, licensePlateHeight - 1]
        ])

        try: 
            matrix = cv2.getPerspectiveTransform(srcPoint, dstPoint)
        except cv2.error as e:
            print("ERROR: ナンバープレートの回転に失敗しました。")
            raise RuntimeError("再度生成してください。")

        licensePlatePositionTransformed = cv2.perspectiveTransform(srcPoint.reshape(-1, 1, 2), matrix)
        
        licensePlateXCoordinate = licensePlatePositionTransformed[:, 0, 0]
        licensePlateYCoordinate = licensePlatePositionTransformed[:, 0, 1]
        
        minLicensePlateXCoordinate, maxLicensePlateXCoordinate = np.min(licensePlateXCoordinate), np.max(licensePlateXCoordinate)
        minLicensePlateYCoordinate, maxLicensePlateYCoordinate = np.min(licensePlateYCoordinate), np.max(licensePlateYCoordinate)

        newLicensePlateWidth = int(np.round(maxLicensePlateXCoordinate - minLicensePlateXCoordinate))
        newLicensePlateHeight = int(np.round(maxLicensePlateYCoordinate - minLicensePlateYCoordinate))
        
        matrixShift = np.array(
            [
                [1, 0, -minLicensePlateXCoordinate],
                [0, 1, -minLicensePlateYCoordinate],
                [0, 0, 1]
            ],
            dtype=np.float32
        )

        finalMatrix = matrixShift @ matrix

        if np.linalg.det(finalMatrix) == 0:
            return licensePlate
        
        affinedLicensePlate = cv2.warpPerspective(
            npLicensePlate, 
            finalMatrix, 
            (newLicensePlateWidth, newLicensePlateHeight), 
            flags=cv2.INTER_LINEAR, 
            borderMode=cv2.BORDER_CONSTANT, 
            borderValue=(0, 0, 0, 0)
        )

        return Image.fromarray(affinedLicensePlate, 'RGBA')
    
    def createLabels(self, classId, imageNumber, xCenter, yCenter, width, height):
        labelFilePath = f"{self.DATA_SET_LABELS_DIR}/{imageNumber:06}.txt"
        label = f"{classId} {xCenter:.6f} {yCenter:.6f} {width:.6f} {height:.6f}"
        
        try:
            with open(labelFilePath, "a") as f:
                f.write(label + "\n")
        except FileNotFoundError:
            raise RuntimeError("ERROR: ラベルファイルの作成に失敗しました。")
