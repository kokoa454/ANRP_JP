import random

class LICENSE_PLATE:
    # 車種 (
    #     0: 普通（自家用）
    #     1: 普通（事業用）
    #     2: 軽（自家用）
    #     3: 軽（事業用）
    # )

    def __init__(self, trainingNumber, typeOfVehicle):
        trainingNumber = int(trainingNumber)
        typeOfVehicle = int(typeOfVehicle)

        while(trainingNumber > 0):
            plateBackGroundColor = self.getPlateBackGroundColor(typeOfVehicle)
            plateTextColor = self.getPlateTextColor(typeOfVehicle)
            officeCode = self.getOfficeCode()
            classNumber = self.getClassNumber(typeOfVehicle)
            hiraganaCode = self.getHiraganaCode(typeOfVehicle)
            registrationNumber = self.getRegistrationNumber()

            self.createPlate(plateBackGroundColor, plateTextColor, officeCode, classNumber, hiraganaCode, registrationNumber)

            trainingNumber -= 1

        print("生成完了")

    def getPlateBackGroundColor(typeOfVehicle):
        colorList = [
            ("white", (255, 255, 255)),  # 普通（自家用）
            ("green", (0, 128, 0)),      # 普通（事業用）
            ("yellow", (255, 255, 0)),   # 軽（自家用）
            ("black", (0, 0, 0))         # 軽（事業用）
        ]

        return colorList[typeOfVehicle[1]]

    def getPlateTextColor(typeOfVehicle):
        colorList = [
            ("green", (0, 128, 0)),      # 普通（自家用）
            ("white", (255, 255, 255)),  # 普通（事業用）
            ("black", (0, 0, 0)),        # 軽（自家用）
            ("yellow", (255, 255, 0))    # 軽（事業用）
        ]

        return colorList[typeOfVehicle[1]]
    
    def getOfficeCode():
        officeCodeList = [
            # 北海道
            "札幌","函館","旭川","室蘭","苫小牧","釧路","知床","帯広","十勝","北見",
            # 東北
            "青森","弘前","八戸",
            "盛岡","平泉",
            "宮城","仙台",
            "秋田",
            "山形","庄内",
            "福島","会津","郡山","白河","いわき",
            # 関東
            "水戸","土浦","つくば",
            "宇都宮","那須","とちぎ",
            "前橋","高崎","群馬",
            "大宮","川口","春日部","熊谷","所沢","越谷","川越",
            "千葉","習志野","成田","柏","袖ヶ浦","野田",
            "板橋","練馬","足立","江東","品川","多摩","八王子",
            "横浜","川崎","相模","湘南","平塚","厚木",
            # 甲信越・北陸
            "山梨","富士山",
            "新潟","長岡","上越","長野","松本","諏訪","諏訪湖","南信州","安曇野",
            "富山","石川","金沢",
            # 東海
            "岐阜","飛騨",
            "静岡","浜松","沼津","伊豆",
            "名古屋","三河","岡崎","豊田","尾張小牧","一宮","知多",
            # 近畿
            "三重","鈴鹿","伊勢志摩",
            "滋賀","彦根",
            "京都","舞鶴",
            "大阪","なにわ","和泉","堺","富田林",
            "奈良",
            "和歌山",
            "神戸","姫路","西宮","伊丹",
            # 中国
            "鳥取","倉吉",
            "島根","出雲",
            "岡山","倉敷","備前",
            "広島","福山","呉","尾道",
            "山口","下関","周南","岩国","宇部",
            # 四国
            "徳島",
            "香川","高松",
            "愛媛","松山","今治","宇和島",
            "高知","土佐",
            # 九州
            "福岡","北九州","久留米","筑豊",
            "佐賀",
            "長崎","佐世保",
            "熊本","阿蘇",
            "大分","別府",
            "宮崎",
            "鹿児島","奄美",
            # 沖縄
            "沖縄"
        ]

        return random.choice(officeCodeList)

    def getClassNumber(typeOfVehicle):
        if typeOfVehicle == 0 or typeOfVehicle == 1:  # 普通車
            classNumber = str(random.randint(1, 2, 3, 8, 9, 0))

            if random.randint(0, 1) == 0: # 数字分類番号
                classNumber += str(random.randint(0, 99))

                if classNumber[-1] == "0":
                    classNumber += "0"

            else: # アルファベット分類番号
                alphabetList = ["A", "C", "F", "H", "K", "L", "M", "P", "X", "Y"]
                classNumber += random.choice(alphabetList)

        else:  # 軽自動車
            classNumber = str(random.randint(4, 5, 6, 7, 8))

            if random.randint(0, 1) == 0: # 数字分類番号
                classNumber += str(random.randint(80, 82))

            else: # アルファベット分類番号
                alphabetList = ["A", "C", "F", "H", "K", "L", "M", "P", "X", "Y"]
                
                classNumber += random.choice(alphabetList)

        return classNumber

    def getHiraganaCode(typeOfVehicle):
        if typeOfVehicle == 0: # 普通（自家用）
            hiraganaList = ["さ", "す", "せ", "そ", "た", "ち", "つ", "て", "と", "な", "に", "ぬ", "ね", "の", "は", "ひ", "ふ", "ほ", "ま", "み", "む", "め", "も", "や", "ゆ", "ら", "り", "る", "ろ"]
            hiraganaCode = random.choice(hiraganaList)

        elif typeOfVehicle == 1: # 普通（事業用）
            hiraganaList = ["あ", "い", "う", "え", "か", "き", "く", "け", "こ", "を", "わ", "れ"]
            hiraganaCode = random.choice(hiraganaList)

        elif typeOfVehicle == 2: # 軽（自家用）
            # TODO: 軽自動車の自家用のひらがなコードを追加

        return hiraganaCode

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
