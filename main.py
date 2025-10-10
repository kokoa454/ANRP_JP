import LICENSE_PLATE 
import DATA_SET

def main():
    while True:
        print("ANRP_JP\n")
        print("""\n作業番号 (
        0: ナンバープレート生成
        1: データセット生成
        2: 終了
        )\n""")

        try:
            selectedNum = int(input("作業番号?: "))
            
            if selectedNum not in [0, 1, 2]:
                print("0~2の数字を入力してください。\n")
                continue
        except ValueError:
            print("数字を入力してください。\n")
            continue

        print("\n")

        if selectedNum == 0:
            try:
                trainingNumber = int(input("ナンバープレート数?: "))

                if trainingNumber < 1:
                    print("1以上の数字を入力してください。\n")
                    continue
            except ValueError:
                print("数字を入力してください。\n")
                continue

            LICENSE_PLATE.LICENSE_PLATE(trainingNumber)
            print("\n")

        elif selectedNum == 1:
            try:
                trainingNumber = int(input("データセット数?: "))

                if trainingNumber < 1:
                    print("1以上の数字を入力してください。\n")
                    continue
            except ValueError:
                print("数字を入力してください。\n")
                continue

            print("""
                \n車種 (
                0: 普通（自家用）
                1: 普通（事業用）
                2: 軽（自家用）
                3: 軽（事業用）
            )\n""")
            
            try:
                typeOfVehicle = int(input("車種?: "))

                if typeOfVehicle not in [0, 1, 2, 3]:
                    print("0~3の数字を入力してください。\n")
                    continue
            except ValueError:
                print("正しい数字を入力してください。\n")
                continue

            DATA_SET.DATA_SET(trainingNumber, typeOfVehicle)
            print("\n")

        elif selectedNum == 2:
            break
    
        else:
            print("0~2の数字を入力してください。\n")

main()
