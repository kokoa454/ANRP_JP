import random
from PIL import Image, ImageDraw, ImageFont
import os

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

            self.createPlate(typeOfVehicle, plateBackGroundColor, plateTextColor, officeCode, classNumber, hiraganaCode, registrationNumber)

            trainingNumber -= 1

        print("\n生成完了")

    def getPlateBackGroundColor(self, typeOfVehicle):
        colorList = [
            ("white", (240, 240, 240)),  # 普通（自家用）
            ("green", (0, 60, 0)),      # 普通（事業用）
            ("yellow", (255, 255, 0)),   # 軽（自家用）
            ("black", (0, 0, 0))         # 軽（事業用）
        ]

        return colorList[typeOfVehicle]

    def getPlateTextColor(self, typeOfVehicle):
        colorList = [
            ("green", (0, 60, 0)),      # 普通（自家用）
            ("white", (240, 240, 240)),  # 普通（事業用）
            ("black", (0, 0, 0)),        # 軽（自家用）
            ("yellow", (255, 255, 0))    # 軽（事業用）
        ]

        return colorList[typeOfVehicle]
    
    def getOfficeCode(self):
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

    def getClassNumber(self, typeOfVehicle):
        alphabetList = ["A", "C", "F", "H", "K", "L", "M", "P", "X", "Y"]

        if typeOfVehicle == 0 or typeOfVehicle == 1:  # 普通車
            classNumber = str(random.choice([1, 2, 3, 8, 9, 0]))
            
            randomNum = random.randint(0, 1)

            if randomNum == 0: # 2桁の分類番号
                classNumber += str(random.randint(0, 9))

            else: # 3桁の分類番号
                randomNum = random.randint(0, 2)

                if randomNum == 0: # 数字のみの分類番号
                    classNumber += str(random.randint(0, 9))
                    classNumber += str(random.randint(0, 9))

                elif randomNum == 1: # アルファベット1桁を含んだ分類番号
                    classNumber += str(random.randint(0, 9))
                    classNumber += random.choice(alphabetList)

                else: # アルファベット2桁を含んだ分類番号
                    classNumber += random.choice(alphabetList)
                    classNumber += random.choice(alphabetList)

        else:  # 軽自動車
            classNumber = str(random.choice([4, 5, 6, 7, 8]))

            randomNum = random.randint(0, 1)

            if randomNum == 0: # 2桁の分類番号
                classNumber += str(random.randint(0, 9))

            else: # 3桁の分類番号
                randomNum = random.randint(0, 2)

                if randomNum == 0: # 数字のみの分類番号
                    classNumber += str(random.randint(0, 9))
                    classNumber += str(random.randint(0, 9))

                elif randomNum == 1: # アルファベット1桁を含んだ分類番号
                    classNumber += str(random.randint(0, 9))
                    classNumber += random.choice(alphabetList)

                else: # アルファベット2桁を含んだ分類番号
                    classNumber += random.choice(alphabetList)
                    classNumber += random.choice(alphabetList)

        return classNumber

    def getHiraganaCode(self, typeOfVehicle):
        if typeOfVehicle == 0: # 普通（自家用）
            hiraganaList = ["さ", "す", "せ", "そ", "た", "ち", "つ", "て", "と", "な", "に", "ぬ", "ね", "の", "は", "ひ", "ふ", "ほ", "ま", "み", "む", "め", "も", "や", "ゆ", "ら", "り", "る", "ろ"]
            hiraganaCode = random.choice(hiraganaList)

        elif typeOfVehicle == 1: # 普通（事業用）
            hiraganaList = ["あ", "い", "う", "え", "か", "き", "く", "け", "こ", "を", "れ", "わ"]
            hiraganaCode = random.choice(hiraganaList)

        elif typeOfVehicle == 2: # 軽（自家用）
            hiraganaList = ["あ", "い", "う", "え", "か", "き", "く", "け", "こ", "さ", "す", "せ", "そ", "た", "ち", "つ", "て", "と", "な", "に", "ぬ", "ね", "の", "は", "ひ", "ふ", "ほ", "ま", "み", "む", "め", "も", "や", "ゆ", "よ", "ら", "る", "ろ"]
            hiraganaCode = random.choice(hiraganaList)

        else: # 軽（事業用）
            hiraganaList = ["り", "れ", "わ"]
            hiraganaCode = random.choice(hiraganaList)

        return hiraganaCode

    def getRegistrationNumber(self):
        prefixRegistrationNumber = random.randint(1, 99)

        if prefixRegistrationNumber < 10:
            registrationNumber = "・" + str(prefixRegistrationNumber)
        else:
            registrationNumber = str(prefixRegistrationNumber)

        registrationNumber += "-"
        registrationNumber += f"{random.randint(0, 99):02d}"

        return registrationNumber

    def createPlate(self, typeOfVehicle, plateBackGroundColor, plateTextColor, officeCode, classNumber, hiraganaCode, registrationNumber):
        # print(f"""
        # +-------------------------------------+
        # |     {officeCode}  {classNumber}     |
        # |                                     |
        # |                                     |
        # | {hiraganaCode} {registrationNumber} |
        # +-------------------------------------+
        # 背景色: {plateBackGroundColor[0]} (RGB: {plateBackGroundColor[1]})
        # 文字色: {plateTextColor[0]} (RGB: {plateTextColor[1]})
        # """)

        height = 220
        width = 440
        margin = 4
        radius = 6
        font0 = "./fonts/HiraginoMaruGothicProNW4.otf"
        font1 = "./fonts/TrmFontJB.ttf"
        font2 = "./fonts/FZcarnumberJA-OTF_ver10.otf"
        colorForFrame = (128, 128, 128)

        img = Image.new("RGB", (width, height), plateBackGroundColor[1])
        draw = ImageDraw.Draw(img)

        # フレーム
        draw.rectangle([(0, 0), (width-1, height-1)], outline=colorForFrame, width=margin)

        # 左上のねじ穴
        center_x, center_y = 80, 30
        draw.ellipse(
            [(center_x - radius, center_y - radius), (center_x + radius, center_y + radius)],
            fill=colorForFrame
        )

        # 右上のねじ穴
        center_x, center_y = 360, 30
        draw.ellipse(
            [(center_x - radius, center_y - radius), (center_x + radius, center_y + radius)],
            fill=colorForFrame
        )

        # 地名
        fontOfficeCode = ImageFont.truetype(font0, 50)
        thicknessForOfficeCode = 1.2
        positionForOfficeCode = (100, 10)

        if len(officeCode) >= 3:
            # 文字サイズを取得するために一時描画用画像を作る
            dummy_img = Image.new("RGB", (1,1))
            dummy_draw = ImageDraw.Draw(dummy_img)
            bbox = dummy_draw.textbbox((0,0), officeCode, font=fontOfficeCode, stroke_width=int(thicknessForOfficeCode))
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # 透明画像に文字を描画
            text_img = Image.new("RGBA", (text_width, text_height), (0,0,0,0))
            text_draw = ImageDraw.Draw(text_img)
            text_draw.text((0,0), officeCode, font=fontOfficeCode, stroke_width=int(thicknessForOfficeCode), fill=plateTextColor[1])

            # 横方向だけ縮小
            if len(officeCode) == 3:
                compress_ratio = 0.7

            else: # 4文字以上
                compress_ratio = 0.55

            new_width = int(text_img.width * compress_ratio)
            text_img = text_img.resize((new_width, text_img.height), Image.Resampling.LANCZOS)

            # 元画像に貼り付け
            img.paste(text_img, positionForOfficeCode, text_img)

        else:
            draw.text(positionForOfficeCode, officeCode, font=fontOfficeCode, stroke_width=int(thicknessForOfficeCode), fill=plateTextColor[1])

        # 分類番号
        fontForClassNumber = ImageFont.truetype(font0, 50)
        thicknessForClassNumber = 1.2
        positionForClassNumber = (240, 10) 

        if len(classNumber) == 2:
            # 文字サイズを取得
            dummy_img = Image.new("RGB", (1,1))
            dummy_draw = ImageDraw.Draw(dummy_img)
            bbox = dummy_draw.textbbox((0,0), classNumber, font=fontForClassNumber, stroke_width=int(thicknessForClassNumber))
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # 上下に余白を追加
            padding = 10
            text_img = Image.new("RGBA", (text_width, text_height + padding), (0,0,0,0))
            text_draw = ImageDraw.Draw(text_img)
            text_draw.text((0, 0), classNumber, font=fontForClassNumber, stroke_width=int(thicknessForClassNumber), fill=plateTextColor[1])

            # 横方向だけ拡大
            compress_ratio = 1.2
            new_width = int(text_img.width * compress_ratio)
            text_img = text_img.resize((new_width, text_img.height), Image.Resampling.LANCZOS)

            # 元画像に貼り付け
            positionForClassNumber = (265, 10)
            img.paste(text_img, positionForClassNumber, text_img)

        elif "M" in classNumber or "W" in classNumber:
            # 文字サイズを取得
            dummy_img = Image.new("RGB", (1,1))
            dummy_draw = ImageDraw.Draw(dummy_img)
            bbox = dummy_draw.textbbox((0,0), classNumber, font=fontForClassNumber, stroke_width=int(thicknessForClassNumber))
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # 上下に余白を追加
            padding = 10
            text_img = Image.new("RGBA", (text_width, text_height + padding), (0,0,0,0))
            text_draw = ImageDraw.Draw(text_img)
            text_draw.text((0, 0), classNumber, font=fontForClassNumber, stroke_width=int(thicknessForClassNumber), fill=plateTextColor[1])

            # 横方向だけ拡大
            compress_ratio = 0.9
            new_width = int(text_img.width * compress_ratio)
            text_img = text_img.resize((new_width, text_img.height), Image.Resampling.LANCZOS)

            # 元画像に貼り付け
            img.paste(text_img, positionForClassNumber, text_img)

        else:
            draw.text(positionForClassNumber, classNumber, font=fontForClassNumber, stroke_width=int(thicknessForClassNumber), fill=plateTextColor[1])

        # ひらがな
        fontSizeForHiraganaCode = 55
        positionForHiraganaCode = (20, 110)
        fontHiraganaCode = ImageFont.truetype(font2, fontSizeForHiraganaCode)
        draw.text(positionForHiraganaCode, hiraganaCode, font=fontHiraganaCode, fill=plateTextColor[1])

        # プレート番号
        fontSizeForRegistrationNumber = 130
        positionForRegistrationNumber = (80, 80)
        fontRegistrationNumber = ImageFont.truetype(font1, fontSizeForRegistrationNumber)
        draw.text(positionForRegistrationNumber, registrationNumber, font=fontRegistrationNumber, fill=plateTextColor[1])

        if not os.path.exists("./output"):
            os.makedirs("./output")

        if typeOfVehicle == 0:
            typeOfVehicle = "普通_自家用"
        elif typeOfVehicle == 1:
            typeOfVehicle = "普通_事業用"
        elif typeOfVehicle == 2:
            typeOfVehicle = "軽_自家用"
        else:
            typeOfVehicle = "軽_事業用"

        if not os.path.exists(f"./output/{typeOfVehicle}"):
            os.makedirs(f"./output/{typeOfVehicle}")

        return img.save(f"./output/{typeOfVehicle}/{officeCode}_{classNumber}_{hiraganaCode}_{registrationNumber}.png")



def main():
    trainingNumber = input("生成数?: ")

    print("""
        \n車種 (
        0: 普通（自家用）
        1: 普通（事業用）
        2: 軽（自家用）
        3: 軽（事業用）
    )\n""")
    typeOfVehicle = input("車種?: ")

    LICENSE_PLATE(trainingNumber, typeOfVehicle)


if __name__ == "__main__":
    main()