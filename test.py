from DietOpt import DietOpt

calories = 1000 
carbohydrates = 40
proteins = 20
fats = 30

dietOpt = DietOpt(calories , carbohydrates, proteins, fats)

dietOpt.add_food(name = "Evkalipt", serving = 1, price = 2, carbs = 1, protein = 20, fat = 30)
dietOpt.add_food(name = "Bahur", serving = 1, price = 4.40, carbs = 22, protein = 20, fat = 30)
df = dietOpt.get_food_df()
dietOpt.add_equality_constrain(params = df.Calories, const = calories)
dietOpt.add_inequality_constrain(params = df.Carbs, const = carbohydrates)
res = dietOpt.solve()
dietOpt.parse_result(res)