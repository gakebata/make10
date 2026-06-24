
# -------------------- 
#　式を作り出す
import itertools

def Make_formula(strNum):

    lstComp = ['+','-','*','/']
    lstFormula = []

    for x in itertools.permutations(strNum):
        # 1桁の場合
        if   len(strNum) == 1:
            lstFormula.append(str(x))
        
        # 2桁の場合
        elif len(strNum) == 2:
            for i in lstComp:
                lstFormula.append(x[0] + i + x[1])

        # 3桁の場合
        elif len(strNum) == 3:
            for i in lstComp:
                for j in lstComp:
                    lstFormula.append(x[0] + i + x[1] + j + x[2])

        # 4桁の場合
        elif len(strNum) == 4:
            for i in lstComp:
                for j in lstComp:
                    for k in lstComp:
                        lstFormula.append(x[0] + i + x[1] + j + x[2] + k + x[3])

        # その他の場合（あり得ない）
        else:
            lstFormula.append = ''

    # 式のリストを返す
    return lstFormula


# -------------------- 
# 式を計算
def Calculate_formula(lstFormula, strAns):
    
    for strFormula in lstFormula:
        if eval(strFormula) == int(strAns):
            print(strFormula, str(int(eval(strFormula))))
    
#    try:
#        print(eval('(5+7-3+0'))
#    except:
#        print('エラーハンドラ')
#
#    return 


Calculate_formula(Make_formula(input('number =')),input('Answer ='))
