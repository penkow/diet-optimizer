from DietOpt import DietOpt

calories = 400 
carbohydrates = calories * 30/100 /4
proteins = calories * 60/100 /4

fats =  calories * 10/100 /4

dietOpt = DietOpt(calories , carbohydrates, proteins, fats)

dietOpt.add_foods_from_xlsx("foods.xlsx")

#dietOpt.constrain_calories()
dietOpt.constrain_protein(type="eq")
dietOpt.constrain_fats(type="eq")
dietOpt.constrain_carbs(type="eq")

res = dietOpt.solve()
dietOpt.parse_result(res)