import LICENSE_PLATE 
import DATA_SET
import TRAIN

def main():
    print("【ANRP_JP】\n")
    
    while True:
        print("""\n作業番号 (
        0: ナンバープレート生成
        1: データセット生成
        2: 学習
        3: 終了
        )\n""")

        try:
            selectedNum = int(input("作業番号?: "))
            
            if selectedNum not in [0, 1, 2, 3]:
                print("0~3の数字を入力してください。\n")
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

            DATA_SET.DATA_SET(trainingNumber)
            print("\n")

        elif selectedNum == 2:
            TRAIN.TRAIN()

        elif selectedNum == 3:
            break
    
        else:
            print("0~3の数字を入力してください。\n")

main()
