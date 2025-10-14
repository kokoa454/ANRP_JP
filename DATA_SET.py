__package__ = "DATA_SET"

import LICENSE_PLATE
import fiftyone as fo
import fiftyone.zoo as foz
import random
import json
from PIL import Image, ImageDraw, ImageFont
import shutil
import os
import numpy as np
import cv2

class DATA_SET:
    BACKGROUND_IMAGE_DIR = "./background_images"
    DATA_SET_DIR = "./yolo_data"
    DATA_SET_IMAGES_DIR = f"{DATA_SET_DIR}/images"
    DATA_SET_LABELS_DIR = f"{DATA_SET_DIR}/labels"
    IMAGES_TRAIN_DIR = f"{DATA_SET_IMAGES_DIR}/train"
    IMAGES_VAL_DIR = f"{DATA_SET_IMAGES_DIR}/val"
    LABELS_TRAIN_DIR = f"{DATA_SET_LABELS_DIR}/train"
    LABELS_VAL_DIR = f"{DATA_SET_LABELS_DIR}/val"
    DATA_SET_NAME = "data_set"
    MAX_LICENSE_PLATES_PER_IMAGE = 3
    MAX_CELLS_PER_IMAGE = 3
    MAX_OVERLAP_RATE = 0.0

    def __init__(self, trainingNumber):
        trainingNumber = int(trainingNumber)
        
        if os.path.exists(self.BACKGROUND_IMAGE_DIR):
            print("\n前回の背景画像を削除します。")
            shutil.rmtree(self.BACKGROUND_IMAGE_DIR)
            print("前回の背景画像を削除しました。")
        os.makedirs(self.BACKGROUND_IMAGE_DIR)

        if os.path.exists(self.DATA_SET_IMAGES_DIR):
            print("\n前回のデータセットを削除します。")
            fo.delete_datasets(self.DATA_SET_NAME)
            shutil.rmtree(self.DATA_SET_IMAGES_DIR)
            print("前回のデータセットを削除しました。")
        os.makedirs(self.DATA_SET_IMAGES_DIR)

        if os.path.exists(self.DATA_SET_LABELS_DIR):
            print("\n前回のラベルを削除します。")
            shutil.rmtree(self.DATA_SET_LABELS_DIR)
            print("前回のラベルを削除しました。")
        os.makedirs(self.DATA_SET_LABELS_DIR)

        if not os.path.exists(self.IMAGES_TRAIN_DIR):
                    os.makedirs(self.IMAGES_TRAIN_DIR)
        if not os.path.exists(self.IMAGES_VAL_DIR):
                    os.makedirs(self.IMAGES_VAL_DIR)
        if not os.path.exists(self.LABELS_TRAIN_DIR):
                    os.makedirs(self.LABELS_TRAIN_DIR)
        if not os.path.exists(self.LABELS_VAL_DIR):
                    os.makedirs(self.LABELS_VAL_DIR)

        print("\n背景画像をダウンロードしています。")
        self.downloadBackgroundImage(trainingNumber)
        print("背景画像のダウンロードが完了しました。")

        splittedTrainingNumberCount = int(trainingNumber * 0.8)
        splittedTrainingNumber = 1
        splittedValidationNumber = 1

        print("\nデータセットを生成しています。")
        for imageNumber in range(1, trainingNumber + 1):
            backgroundImagePath = self.pickBackgroundImage()
            (licensePlatePaths, licensePlateClasses) = self.pickLicensePlates()
            self.dataSetImage, self.dataSetLabel = self.createDataSet(trainingNumber, backgroundImagePath, licensePlatePaths, licensePlateClasses, imageNumber)

            if imageNumber <= splittedTrainingNumberCount:
                self.saveDataSet(self.dataSetImage, self.dataSetLabel, trainingNumber, splittedTrainingNumber, isTrain=True)
                splittedTrainingNumber += 1
            else:
                self.saveDataSet(self.dataSetImage, self.dataSetLabel, trainingNumber, splittedValidationNumber , isTrain=False)
                splittedValidationNumber += 1
                
            print(f"データセット {imageNumber} / {trainingNumber} を生成しました。")
        
        print("YAMLファイルを作成しています。")
        self.createYaml()
        print("YAMLファイルを作成しました。")

        print("データセットの生成が完了しました。")

    def downloadBackgroundImage(self, trainingNumber):
        metaData = {"imagePath": []}

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
                dstPath = os.path.join(self.BACKGROUND_IMAGE_DIR, uniqueName)
                shutil.copy(sample.filepath, dstPath)
                metaData["imagePath"].append(dstPath.replace("\\", "/"))

        try:
            with open (f"{self.BACKGROUND_IMAGE_DIR}/metaData.json", "w", encoding="utf-8") as f:
                json.dump(metaData, f, ensure_ascii=False)
        except Exception as e:
            raise RuntimeError("ERROR: メタデータの保存に失敗しました。")

        return
    
    def pickBackgroundImage(self):
        try:
            with open(self.BACKGROUND_IMAGE_DIR + "/metaData.json", "r", encoding="utf-8") as f:
                metaData = json.load(f)

            backgroundImage = random.choice(metaData["imagePath"])

            return backgroundImage

        except FileNotFoundError:
            raise RuntimeError("背景画像が見つかりません。")
        
        except json.JSONDecodeError:
            raise RuntimeError("再度生成してください。")

    def pickLicensePlates(self):
        licensePlatePaths = []
        licensePlateClasses = []
        
        try:
            with open(LICENSE_PLATE.LICENSE_PLATE.LICENSE_PLATE_DIR + "/metaData.json", "r", encoding="utf-8") as f:
                metaData = json.load(f)

            licensePlateNumber = random.randint(1, self.MAX_LICENSE_PLATES_PER_IMAGE)

            while licensePlateNumber > 0:
                typeOfVehicle = random.randint(0, len(LICENSE_PLATE.LICENSE_PLATE.TYPE_OF_VEHICLE_STRING) - 1)
                licensePlatePaths.append(random.choice(metaData["imagePath_" + LICENSE_PLATE.LICENSE_PLATE.TYPE_OF_VEHICLE_STRING[typeOfVehicle]]))
                licensePlateClasses.append(LICENSE_PLATE.LICENSE_PLATE.TYPE_OF_VEHICLE_STRING[typeOfVehicle])
                licensePlateNumber -= 1
            
        except FileNotFoundError:
            raise RuntimeError("ナンバープレートが見つかりません。")
        
        except json.JSONDecodeError:
            raise RuntimeError("再度生成してください。")

        return (licensePlatePaths, licensePlateClasses)
        
    def createDataSet(self, trainingNumber, backgroundImagePath, licensePlatePaths, licensePlateClasses, imageNumber):
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
        labels = []
        
        drawingInfoList = []
        
        if isHorizontal:
            cellWidth = BACKGROUND_WIDTH // self.MAX_CELLS_PER_IMAGE
            cellHeight = BACKGROUND_HEIGHT
        elif isVertical:
            cellWidth = BACKGROUND_WIDTH
            cellHeight = BACKGROUND_HEIGHT // self.MAX_CELLS_PER_IMAGE

        for _ in range(self.MAX_CELLS_PER_IMAGE):
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

            originalCorners = np.float32([
                [0, 0],
                [licensePlate.size[0] - 1, 0],
                [licensePlate.size[0] - 1, licensePlate.size[1] - 1],
                [0, licensePlate.size[1] - 1]
            ])
            transformedCorners = originalCorners.copy()

            licensePlateXMinInRotated = 0.0
            licensePlateYMinInRotated = 0.0
            licensePlateXMaxInRotated = float(licensePlate.size[0])
            licensePlateYMaxInRotated = float(licensePlate.size[1])
            
            if rotateOrNot == 1:
                rotationXAngle = random.randint(-30, 30)
                if rotationXAngle != 0:
                    (licensePlate, licensePlateXMinInRotated, licensePlateYMinInRotated, licensePlateXMaxInRotated, licensePlateYMaxInRotated, transformedCorners) = self.rotateLicensePlate(licensePlate, rotationXAngle, 0, originalCorners)
            elif rotateOrNot == 2:
                rotationYAngle = random.randint(-30, 30)
                if rotationYAngle != 0:
                    (licensePlate, licensePlateXMinInRotated, licensePlateYMinInRotated, licensePlateXMaxInRotated, licensePlateYMaxInRotated, transformedCorners) = self.rotateLicensePlate(licensePlate, 0, rotationYAngle, originalCorners)

            currentLicensePlateWidth = licensePlate.size[0]
            currentLicensePlateHeight = licensePlate.size[1]
            
            maxLicensePlateWidth = max(1, cellWidth - (MARGIN * 2))
            maxLicensePlateHeight = max(1, cellHeight - (MARGIN * 2))

            scale = 1.0
            if currentLicensePlateWidth > maxLicensePlateWidth or currentLicensePlateHeight > maxLicensePlateHeight:
                scale = min(maxLicensePlateWidth / currentLicensePlateWidth, maxLicensePlateHeight / currentLicensePlateHeight)
                newLicensePlateWidth = max(1, int(currentLicensePlateWidth * scale))
                newLicensePlateHeight = max(1, int(currentLicensePlateHeight * scale))

                licensePlateXMinInRotated *= scale
                licensePlateYMinInRotated *= scale
                licensePlateXMaxInRotated *= scale
                licensePlateYMaxInRotated *= scale
                transformedCorners *= scale 

                licensePlate = licensePlate.resize((newLicensePlateWidth, newLicensePlateHeight), Image.Resampling.LANCZOS)

                currentLicensePlateWidth = licensePlate.size[0]
                currentLicensePlateHeight = licensePlate.size[1]

            if i < len(startCoordinateForEachLicensePlate):
                licensePlateX = startCoordinateForEachLicensePlate[i][0]
                licensePlateY = startCoordinateForEachLicensePlate[i][1]
            else:
                licensePlateX = random.randint(MARGIN, max(MARGIN, BACKGROUND_WIDTH - licensePlate.size[0] - MARGIN))
                licensePlateY = random.randint(MARGIN, max(MARGIN, BACKGROUND_HEIGHT - licensePlate.size[1] - MARGIN))

            background.paste(licensePlate, (licensePlateX, licensePlateY), licensePlate)

            boxWidth  = licensePlateXMaxInRotated - licensePlateXMinInRotated
            boxHeight = licensePlateYMaxInRotated - licensePlateYMinInRotated

            absoluteXCenter = float(licensePlateX) + licensePlateXMinInRotated + (boxWidth / 2.0)
            absoluteYCenter = float(licensePlateY) + licensePlateYMinInRotated + (boxHeight / 2.0)
            
            classIdRoman = LICENSE_PLATE.LICENSE_PLATE.TYPE_OF_VEHICLE_ROMAN[licensePlateClasses[i]]

            drawingCorners = []
            for corner in transformedCorners:
                cornerX = int(round(licensePlateX + corner[0]))
                cornerY = int(round(licensePlateY + corner[1]))
                drawingCorners.append((cornerX, cornerY))

            drawingInfo = self.getBoxAndLabelDrawingInfo(
                classId = classIdRoman,
                drawingCorners = drawingCorners,
                classIdRoman = classIdRoman,
                xMinAABB = int(round(licensePlateX + licensePlateXMinInRotated)),
                yMinAABB = int(round(licensePlateY + licensePlateYMinInRotated)),
                yMaxAABB = int(round(licensePlateY + licensePlateYMaxInRotated))
            )
            drawingInfoList.append(drawingInfo)

            xCenter = absoluteXCenter / BACKGROUND_WIDTH
            yCenter = absoluteYCenter / BACKGROUND_HEIGHT
            width = boxWidth / BACKGROUND_WIDTH
            height = boxHeight / BACKGROUND_HEIGHT
            labels.append(f"{classIdRoman} {xCenter:.6f} {yCenter:.6f} {width:.6f} {height:.6f}")
                    
        levelOfNoise = random.randint(0, 5)
        if levelOfNoise > 0:
            background = self.makeNoise(background, levelOfNoise)

        npBackground = np.array(background).copy() 
        for info in drawingInfoList:
            npBackground = self.drawBoundingBoxAndLabel(npBackground, info)
            
        image = Image.fromarray(npBackground)

        return image, labels

    def makeNoise(self, background, levelOfNoise):
        npBackground = np.array(background)
        noise = np.random.randint(-levelOfNoise * 10, levelOfNoise * 10, npBackground.shape, dtype='int16')
        noisyBackground = np.clip(npBackground.astype('int16') + noise, 0, 255).astype('uint8')
        return Image.fromarray(noisyBackground)
    
    def rotateLicensePlate(self, licensePlate, rotationXAngle, rotationYAngle, originalCorners):
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

        for x, y, z in srcPoints3D:
            rotatedPoint = finalRotationMatrix @ np.array([x, y, z])
            ZPrime = rotatedPoint[2] + focalLength 
            if ZPrime == 0: ZPrime = 1e-6 
            
            xProj = (focalLength * rotatedPoint[0] / ZPrime) + centerX
            yProj = (focalLength * rotatedPoint[1] / ZPrime) + centerY
            
            dstPoints.append([xProj, yProj])
            
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
            return (licensePlate, 0.0, 0.0, float(licensePlateWidth), float(licensePlateHeight), originalCorners)

        transformedCorners = cv2.perspectiveTransform(originalCorners.reshape(-1, 1, 2), finalMatrix)[:, 0, :]
        transformedCorners[:, 0] += 0.5 
        transformedCorners[:, 1] += 0.5 
        
        affinedLicensePlate = cv2.warpPerspective(
            npLicensePlate, 
            finalMatrix, 
            (newLicensePlateWidth, newLicensePlateHeight), 
            flags=cv2.INTER_LINEAR, 
            borderMode=cv2.BORDER_CONSTANT, 
            borderValue=(0, 0, 0, 0)
        )

        return (
            Image.fromarray(affinedLicensePlate, 'RGBA'),
            minLicensePlateXCoordinate,
            minLicensePlateYCoordinate,
            maxLicensePlateXCoordinate,
            maxLicensePlateYCoordinate,
            transformedCorners
        )
    
    def getBoxAndLabelDrawingInfo(self, classId, drawingCorners, classIdRoman, xMinAABB, yMinAABB, yMaxAABB):
        romanValue = list(LICENSE_PLATE.LICENSE_PLATE.TYPE_OF_VEHICLE_ROMAN.values())
        classIdInt = romanValue.index(classId)
        className = LICENSE_PLATE.LICENSE_PLATE.TYPE_OF_VEHICLE_STRING[classIdInt]
        
        colorRgb = LICENSE_PLATE.LICENSE_PLATE.TYPE_OF_VEHICLE_COLOR_RGB.get(className)

        return {
            "className": className,
            "classIdRoman": classIdRoman,
            "colorRgb": colorRgb,
            "drawingCorners": np.array(drawingCorners, dtype=np.int32),
            "xMinAABB": xMinAABB, 
            "yMinAABB": yMinAABB, 
            "yMaxAABB": yMaxAABB,
        }
    
    def drawBoundingBoxAndLabel(self, image, boxData):
        className = boxData["className"]
        classIdRoman = boxData["classIdRoman"]
        colorRgb = boxData["colorRgb"]
        drawingCorners = boxData["drawingCorners"]
        yMinAABB = boxData["yMinAABB"]
        
        cv2.polylines(
            img = image,
            pts = [drawingCorners],
            isClosed = True,
            color = colorRgb,
            thickness = 2
        )

        pilImage = Image.fromarray(image)
        draw = ImageDraw.Draw(pilImage)
        IMAGE_WIDTH, IMAGE_HEIGHT = pilImage.size

        font0 = "./fonts/HiraginoMaruGothicProNW4.otf"

        try:
            fontSize = 20
            font = ImageFont.truetype(font0, fontSize)
        except IOError:
            className = classIdRoman
            font = ImageFont.load_default()
            fontSize = 12

        dummyImg = Image.new('RGB', (1, 1))
        dummyDraw = ImageDraw.Draw(dummyImg)
        bbox = dummyDraw.textbbox((0, 0), className, font=font)
        textWidth = bbox[2] - bbox[0]
        textHeight = bbox[3] - bbox[1]
        
        MARGIN = 10
        
        minY_corner = np.min(drawingCorners[:, 1])
        maxY_corner = np.max(drawingCorners[:, 1])
        
        labelXReference = np.min(drawingCorners[:, 0])

        labelYTryAbove = minY_corner - textHeight - MARGIN
        labelYTryBelow = maxY_corner + MARGIN
        
        labelY = -1

        if labelYTryAbove >= 0:
            labelY = labelYTryAbove
        elif labelYTryBelow + textHeight + 5 <= IMAGE_HEIGHT:
            labelY = labelYTryBelow
        else:
            labelY = min(labelYTryBelow, IMAGE_HEIGHT - textHeight - 5)
            if labelY < yMinAABB:
                labelY = yMinAABB + MARGIN
        
        labelX = labelXReference
        
        if labelX + textWidth + 10 > IMAGE_WIDTH:
            labelX = IMAGE_WIDTH - textWidth - 10
        
        if labelX < 0:
            labelX = 0
            
        labelXMax = labelX + textWidth + 10
        labelYMax = labelY + textHeight + 5
        
        draw.rectangle(
            [(labelX, labelY), (labelXMax, labelYMax)],
            fill=colorRgb
        )
        
        draw.text(
            (labelX + 5, labelY + 2),
            className,
            font=font,
            fill=(255, 255, 255)
        )

        return np.array(pilImage)
    
    def saveDataSet(self, image, labels, trainingNumber, imageNumber, isTrain):
        try:
            if isTrain:
                imagePath = f"{self.IMAGES_TRAIN_DIR}/{imageNumber:0{len(str(trainingNumber)) + 1}}.jpg"
                labelPath = f"{self.LABELS_TRAIN_DIR}/{imageNumber:0{len(str(trainingNumber)) + 1}}.txt"
            else:
                imagePath = f"{self.IMAGES_VAL_DIR}/{imageNumber:0{len(str(trainingNumber)) + 1}}.jpg"
                labelPath = f"{self.LABELS_VAL_DIR}/{imageNumber:0{len(str(trainingNumber)) + 1}}.txt"
                
            image.save(imagePath)
        except OSError:
            raise RuntimeError("ERROR: 画像ファイルの保存に失敗しました。")

        for label in labels:
            try:
                with open(labelPath, "a") as f:
                    f.write(label + "\n")
            except FileNotFoundError:
                raise RuntimeError("ERROR: ラベルファイルの作成に失敗しました。")
            
    def createYaml(self):
        classNames = [f"'{name}'" for name in LICENSE_PLATE.LICENSE_PLATE.TYPE_OF_VEHICLE_ROMAN.values()]
        names = ", ".join(classNames)

        data = f"""
# train and val data as 
# 1) directory: path/images/,
# 2) file: path/images.txt, or
# 3) list: [path1/images/, path2/images/]

train: {self.IMAGES_TRAIN_DIR}
val: {self.IMAGES_VAL_DIR}

# number of classes
nc: {LICENSE_PLATE.LICENSE_PLATE.TYPE_OF_VEHICLE_ROMAN.__len__()}

# class names
names: [{names}]

"""

        try:
            with open(self.DATA_SET_DIR + "/data.yaml", "w") as f:
                f.write(data.strip())
        except OSError:
            raise RuntimeError("ERROR: YAMLファイルの保存に失敗しました。")