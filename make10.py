
import itertools

# -------------------- 
#　式を作り出す
def Make_formula(strNum):

    lstComp = ['+','-','*','/']
    lstFormula = []

    # 数字の順列を列挙する
    for x in itertools.permutations(strNum):
        # 1桁の場合（あまり意味はない）
        if   len(strNum) == 1:
            lstFormula.append(str(x))
        
        # 2桁の場合（()演算子なし）
        elif len(strNum) == 2:
            for i in lstComp:
                lstFormula.append(x[0] + i + x[1])

        # 3桁の場合
        elif len(strNum) == 3:
            for i in lstComp:
                for j in lstComp:
                    # ()演算子なし
                    lstFormula.append(x[0] + i + x[1] + j + x[2])
                    # 前半に()演算子
                    lstFormula.append('(' + x[0] + i + x[1] + ')' + j + x[2])
                    # 後半に()演算子
                    lstFormula.append(x[0] + i + '(' + x[1] + j + x[2] + ')')

        # 4桁の場合
        elif len(strNum) == 4:
            for i in lstComp:
                for j in lstComp:
                    for k in lstComp:
                        # ()演算子なし
                        lstFormula.append(x[0] + i + x[1] + j + x[2] + k + x[3])
                        # 2値を()演算子 前半 (a + b) + c + d
                        lstFormula.append('(' + x[0] + i + x[1] + ')' + j + x[2] + k + x[3])
                        # 2値を()演算子 中盤 a + (b + c) + d
                        lstFormula.append(x[0] + i + '(' + x[1] + j + x[2] + ')' + k + x[3])
                        # 2値を()演算子 後半 a + b + (c + d)
                        lstFormula.append(x[0] + i + x[1] + j + '(' + x[2] + k + x[3] + ')')
                        # 3値を()演算子 前半 (a + b + c) + d
                        lstFormula.append('(' + x[0] + i + x[1] + j + x[2] + ')' + k + x[3])
                        # 3値を()演算子 後半 a + (b + c + d)
                        lstFormula.append(x[0] + i + '(' + x[1] + j + x[2] + k + x[3] + ')')
                        # ()演算子 2つ      (a + b) + (c + d)
                        lstFormula.append('(' + x[0] + i + x[1] + ')' + j + '(' + x[2] + k + x[3] + ')')

        # その他の場合（あり得ないこととする）
        else:
            lstFormula.append('')
            break

    # 式のリストを返す
    return lstFormula


# -------------------- 
# 式を計算
def Calculate_formula(lstFormula, iTaget):
    
    iCount = 0
    for strFormula in lstFormula:
        try:
            iAns = eval(strFormula)
        except:
            iAns = 0

        if iAns == iTaget:
            print(strFormula, ' = ', str(int(iAns)))
            iCount += 1
    print('[Count: ', str(iCount), ']')


# 4桁以内の数字を入力すると四則演算して10になる式を列挙
strNumber = input('number? = ')
while strNumber != 'end':
    Calculate_formula(Make_formula(strNumber),10)
    print('')
    strNumber = input('number? = ')


