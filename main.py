import LICENSE_PLATE 
import DATA_SET

def main():
    while True:
        try:
            trainingNumber = int(input("車両数?: "))
            break
        except ValueError:
            print("数字を入力してください。\n")

    print("""
        \n車種 (
        0: 普通（自家用）
        1: 普通（事業用）
        2: 軽（自家用）
        3: 軽（事業用）
    )\n""")
    
    while True:
        try:
            typeOfVehicle = int(input("車種は?: "))
            if typeOfVehicle in [0, 1, 2, 3]:
                break
            else:
                print("0~3の数字を入力してください。\n")
        except ValueError:
            print("数字を入力してください。\n")

    LICENSE_PLATE.LICENSE_PLATE(trainingNumber, typeOfVehicle)

main()