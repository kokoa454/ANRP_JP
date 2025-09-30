__package__ = "DATA_SET"

import LICENSE_PLATE
import fiftyone.zoo as foz
import random
import json

class DATA_SET:
    LICENSE_PLATE_DIR = "./license_plate_images"
    DATA_SET_IMAGES_DIR = "./data_set/images"
    DATA_SET_LABELS_DIR = "./data_set/labels"
    MAX_LICENSE_PLATES_PER_IMAGE = 4

    def __init__(self, trainingNumber, typeOfVehicle):
        trainingNumber = int(trainingNumber)
        typeOfVehicle = int(typeOfVehicle)
        completedNumber = 0

        self.backgroundImage = self.downloadBackgroundImage()
        self.dataSet = self.createDataSet(self.backgroundImage, typeOfVehicle)

    def downloadBackgroundImage(self):
        dataSet = foz.load_zoo_dataset(
            "open-images-v7",
            split="train",
            label_types=[],
            classes=["Road", "Building", "Tree", "Sky", "Pedestrian", "Sidewalk", "Streetlight", "Traffic light", "Traffic sign", "Crosswalk", "Fence", "Wall", "Pole"],
            max_samples=1000,
            shuffle=True
        )

        dataSet.name = "backgroundImages"
        dataSet.export(DATA_SET.DATA_SET_IMAGES_DIR, dataset_type=foz.types.ImageDirectory)

        return dataSet
        
    def createDataSet(self, backgroundImage, typeOfVehicle):
        licensePlatesNumber = random.choices(range(1, self.MAX_LICENSE_PLATES_PER_IMAGE))
        
        with open(LICENSE_PLATE.LICENSE_PLATE_DIR  + f"/{LICENSE_PLATE.LICENSE_PLATE.typeOfVehicleString[typeOfVehicle]}/metaData.json", "r", encoding="utf-8") as f:
            metaData = json.load(f)

        for licensePlateNumber in licensePlatesNumber:
            licensePlate = random.choice(metaData["imagePath"])

        # TODO : ナンバープレートの位置決め、背景画像とナンバープレートを合成する