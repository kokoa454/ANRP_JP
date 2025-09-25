class LICENSE_PLATE:
    # 車種 (
    #     0: 普通（自家用）
    #     1: 普通（事業用）
    #     2: 軽（自家用）
    #     3: 軽（事業用）
    # )

    def __init__(trainingNumber, typeOfVehicle):
        trainingNumber = int(trainingNumber)
        typeOfVehicle = int(typeOfVehicle)

        while(trainingNumber > 0):
            plateBackGroundColor = getPlateBackGroundColor(typeOfVehicle)
            plateTextColor = getPlateTextColor(typeOfVehicle)
            officeCode = getOfficeCode()
            classNumber = getClassNumber(typeOfVehicle)
            hiraganaCode = getHiraganaCode(typeOfVehicle)
            registrationNumber = getRegistrationNumber()

            plate = createPlate(plateBackGroundColor, plateTextColor, officeCode, classNumber, hiraganaCode, registrationNumber)

        print("生成完了")

    def getPlateBackGroundColor(typeOfVehicle):

    def getPlateTextColor(typeOfVehicle):
    
    def getOfficeCode():

    def getClassNumber(typeOfVehicle):

    def getHiraganaCode(typeOfVehicle):

    def getRegistrationNumber():

    def createPlate(plateBackGroundColor, plateTextColor, officeCode, classNumber, hiraganaCode, registrationNumber):


def main():
    trainingNumber = input("生成数?: ")

    print("""
        \n車種 (
        0: 普通（自家用）
        1: 普通（事業用）
        2: 軽（自家用）
        3: 軽（事業用）
    )""")
    typeOfVehicle = input("車種?: ")

    LICENSE_PLATE(trainingNumber, typeOfVehicle)
