__package__ = "DATA_SET"

import LICENSE_PLATE
import os

os.environ["FIFTYONE_DATABASE_DIR"] = "./fiftyone_db"
os.environ["FIFTYONE_DATASET_ZOO_DIR"] = "./fiftyone_cache"
import fiftyone as fo
import fiftyone.zoo as foz
from fiftyone import ViewField as fovf

import random
import json
from PIL import Image, ImageDraw, ImageFont
import shutil
import numpy as np
import cv2

class DATA_SET:
    BACKGROUND_IMAGE_DIR = "./fiftyone_cache/open-images-v7/train/data"
    DATA_SET_DIR = "./data_set"
    
    DATA_SET_IMAGES_SUBDIR = "images"
    DATA_SET_LABELS_SUBDIR = "labels"

    YOLO_IMAGES_TRAIN_DIR = f"{DATA_SET_IMAGES_SUBDIR}/train"
    YOLO_IMAGES_VAL_DIR = f"{DATA_SET_IMAGES_SUBDIR}/val"

    IMAGES_TRAIN_DIR = f"{DATA_SET_DIR}/{YOLO_IMAGES_TRAIN_DIR}"
    IMAGES_VAL_DIR = f"{DATA_SET_DIR}/{YOLO_IMAGES_VAL_DIR}"
    LABELS_TRAIN_DIR = f"{DATA_SET_DIR}/{DATA_SET_LABELS_SUBDIR}/train"
    LABELS_VAL_DIR = f"{DATA_SET_DIR}/{DATA_SET_LABELS_SUBDIR}/val"
    
    DATA_SET_NAME = "data_set"
    MIN_SCALE = 0.1
    MAX_SCALE = 1.0
    MARGIN = 10
    MAX_PLACEMENT_ATTEMPTS = 50
    MAX_LICENSE_PLATES_PER_IMAGE = 5
    MAX_OVERLAP_RATE = 0.0

    TARGET_CLASS = [
        "Skyscraper",
        "Tower",
        "House",
        "Office building",
        "Convenience store",
        "Tree",
        "Car",
        "Truck",
        "Van",
        "Wheel",
        "Tire",
        "Street light",
        "Parking meter",
        "Traffic light"
    ]

    def __init__(self, trainingNumber):
        trainingNumber = int(trainingNumber)

        if fo.dataset_exists(self.DATA_SET_NAME):
            print(f"\n前回のFiftyOneデータベースを削除します。")
            fo.delete_dataset(self.DATA_SET_NAME)
            print("前回のFiftyOneデータセットを削除しました。")
        
        if os.path.exists(self.BACKGROUND_IMAGE_DIR):
            print("\n前回の背景画像を削除します。")
            shutil.rmtree(self.BACKGROUND_IMAGE_DIR)
            print("前回の背景画像を削除しました。")
        os.makedirs(self.BACKGROUND_IMAGE_DIR)

        if os.path.exists(self.DATA_SET_DIR):
            print("\n前回のデータセットを削除します。")
            shutil.rmtree(self.DATA_SET_DIR)
            print("前回のデータセットを削除しました。")
        os.makedirs(self.DATA_SET_DIR)
        
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
            self.dataSetImage, self.dataSetLabel = self.createDataSet(backgroundImagePath, licensePlatePaths, licensePlateClasses, imageNumber)

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

        try:
            backgroundImages = foz.load_zoo_dataset(
                "open-images-v7",
                split="validation",
                label_types=["detections"],
                classes = self.TARGET_CLASS,
                max_samples = trainingNumber,
                only_matching = True,
                shuffle = True
            )
            backgroundImages.name = self.DATA_SET_NAME

        except Exception as e:
            raise RuntimeError("ERROR: FiftyOneデータベースの読み込みに失敗しました。")

        try:
            print(f"ダウンロードした背景画像数: {len(backgroundImages)}")

            for sample in backgroundImages:
                dstPath = sample.filepath
                metaData["imagePath"].append(dstPath.replace("\\", "/"))
        
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
        
    def createDataSet(self, backgroundImagePath, licensePlatePaths, licensePlateClasses, imageNumber):
        background = Image.open(backgroundImagePath).convert("RGB")

        BACKGROUND_WIDTH = background.size[0]
        BACKGROUND_HEIGHT = background.size[1]
        MARGIN = self.MARGIN
        labels = []
        drawingInfoList = []
        placed_boxes = []

        for i, licensePlatePath in enumerate(licensePlatePaths):
            originalLicensePlate = Image.open(licensePlatePath).convert("RGBA")
            
            scale = random.uniform(self.MIN_SCALE, self.MAX_SCALE)
            
            newWidth_base = max(1, int(originalLicensePlate.size[0] * scale))
            newHeight_base = max(1, int(originalLicensePlate.size[1] * scale))
            
            tempLicensePlate = originalLicensePlate.resize((newWidth_base, newHeight_base), Image.Resampling.LANCZOS)
            
            rotationXAngle = 0
            rotationYAngle = 0
            
            if random.random() < 0.5:
                rotationXAngle = random.randint(-30, 30)
            if random.random() < 0.5:
                rotationYAngle = random.randint(-30, 30)

            (
                rotatedLicensePlate, 
                lp_x_min_rot, lp_y_min_rot, 
                lp_x_max_rot, lp_y_max_rot, 
                transformedCorners
            ) = self.rotateLicensePlate(tempLicensePlate, rotationXAngle, rotationYAngle)
            
            boxWidth = lp_x_max_rot - lp_x_min_rot
            boxHeight = lp_y_max_rot - lp_y_min_rot

            placed = False
            for _ in range(self.MAX_PLACEMENT_ATTEMPTS):
                max_x = BACKGROUND_WIDTH - int(boxWidth) - MARGIN
                max_y = BACKGROUND_HEIGHT - int(boxHeight) - MARGIN
                
                if max_x > MARGIN and max_y > MARGIN:
                    licensePlateX = random.randint(MARGIN, max_x)
                    licensePlateY = random.randint(MARGIN, max_y)
                else:
                    break 

                current_box = [
                    licensePlateX, 
                    licensePlateY,
                    licensePlateX + int(boxWidth),
                    licensePlateY + int(boxHeight)
                ]

                overlap = False
                for placed_box in placed_boxes:
                    if self.checkOverlap(current_box, placed_box):
                        overlap = True
                        break
                
                if not overlap:
                    placed_boxes.append(current_box)
                    placed = True
                    break
            
            if not placed:
                continue             

            pasteX = licensePlateX - int(lp_x_min_rot)
            pasteY = licensePlateY - int(lp_y_min_rot)
            
            background.paste(rotatedLicensePlate, (pasteX, pasteY), rotatedLicensePlate)

            absoluteXCenter = float(licensePlateX) + (boxWidth / 2.0)
            absoluteYCenter = float(licensePlateY) + (boxHeight / 2.0)
            
            classIdRoman = LICENSE_PLATE.LICENSE_PLATE.TYPE_OF_VEHICLE_ROMAN[licensePlateClasses[i]]

            drawingCorners_final = []
            for corner in transformedCorners:
                cornerX = int(round(pasteX + corner[0]))
                cornerY = int(round(pasteY + corner[1]))
                drawingCorners_final.append((cornerX, cornerY))

            drawingInfo = self.getBoxAndLabelDrawingInfo(
                classId = classIdRoman,
                drawingCorners = drawingCorners_final,
                classIdRoman = classIdRoman,
                xMinAABB = current_box[0],
                yMinAABB = current_box[1],
                yMaxAABB = current_box[3]
            )
            drawingInfoList.append(drawingInfo)

            className = licensePlateClasses[i]
            classIdInt = LICENSE_PLATE.LICENSE_PLATE.TYPE_OF_VEHICLE_STRING.index(className)
            xCenter = absoluteXCenter / BACKGROUND_WIDTH
            yCenter = absoluteYCenter / BACKGROUND_HEIGHT
            width = boxWidth / BACKGROUND_WIDTH
            height = boxHeight / BACKGROUND_HEIGHT
            labels.append(f"{classIdInt} {xCenter:.6f} {yCenter:.6f} {width:.6f} {height:.6f}")
            
        randomNumber = random.randint(0, 1)
        if randomNumber > 0:
            levelOfNoise = random.randint(1, 5)
            background = self.makeNoise(background, levelOfNoise)

        randomNumber = random.randint(0, 1)
        if randomNumber > 0:
            levelOfBlur = random.randint(1, 5)
            background = self.makeBlur(background, levelOfBlur)

        randomNumber = random.randint(0, 1)
        if randomNumber > 0:
            levelOfJitter = random.randint(1, 5)
            background = self.makeJitter(background, levelOfJitter)

        npBackground = np.array(background).copy() 
        for info in drawingInfoList:
            npBackground = self.drawBoundingBoxAndLabel(npBackground, info)
            
        image = Image.fromarray(npBackground)

        return image, labels
    
    def checkOverlap(self, box1, box2):
        xMin1, yMin1, xMax1, yMax1 = box1
        xMin2, yMin2, xMax2, yMax2 = box2

        noOverlap = (
            xMax1 < xMin2 or 
            xMax2 < xMin1 or 
            yMax1 < yMin2 or 
            yMax2 < yMin1
        )  

        return not noOverlap

    def makeNoise(self, background, levelOfNoise):
        npBackground = np.array(background)
        noise = np.random.randint(-levelOfNoise * 10, levelOfNoise * 10, npBackground.shape, dtype='int16')
        noisyBackground = np.clip(npBackground.astype('int16') + noise, 0, 255).astype('uint8')

        return Image.fromarray(noisyBackground)
    
    def makeBlur(self, background, levelOfBlur):
        npBackground = np.array(background)
        kernelSize = int(levelOfBlur * 2) + 1
        
        return Image.fromarray(cv2.GaussianBlur(npBackground, (kernelSize, kernelSize), 0))
    
    def makeJitter(self, background, levelOfJitter):
        npBackground = np.array(background).astype(np.float32) / 255.0
        hsvBackground = cv2.cvtColor(npBackground, cv2.COLOR_RGB2HSV)

        saturation = 1.0 + random.uniform(-levelOfJitter, levelOfJitter) / 8.0
        brightness = 1.0 + random.uniform(-levelOfJitter, levelOfJitter) / 8.0
        hsvBackground[:, :, 1] = np.clip(hsvBackground[:, :, 1] * saturation, 0.0, 1.0)
        hsvBackground[:, :, 2] = np.clip(hsvBackground[:, :, 2] * brightness, 0.0, 1.0)
        rgbBackground = cv2.cvtColor(hsvBackground, cv2.COLOR_HSV2RGB)
        rgbBackground = (rgbBackground * 255).astype(np.uint8)

        return Image.fromarray(rgbBackground)
    
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

        if rotationXAngle != 0 and rotationYAngle != 0:
            finalRotationMatrix = rotationYMatrix @ rotationXMatrix
        elif rotationXAngle != 0:
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
            return (licensePlate, 0.0, 0.0, float(licensePlateWidth), float(licensePlateHeight), srcPoint)

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
        
        transformedCorners = cv2.perspectiveTransform(srcPoint.reshape(-1, 1, 2), finalMatrix)[:, 0, :]
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

train: {self.YOLO_IMAGES_TRAIN_DIR}
val: {self.YOLO_IMAGES_VAL_DIR}

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