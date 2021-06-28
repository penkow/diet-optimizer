from scipy.optimize import linprog
import pandas as pd
import numpy as np
from tabulate import tabulate

class DietOpt:
    food_list = []
    serving_list = []
    price_list = []
    calorie_list = []
    carb_list = []
    protein_list = []
    fat_list = []

    calories = 0
    carbohydrates = 0
    proteins = 0
    fats = 0

    A_ub = []
    b_ub = []

    A_eq = []
    b_eq = []

    bounds = []
    
    df = None

    def __init__(self, calories, carbohydrates, proteins, fats):
        self.calories = calories
        self.carbohydrates = carbohydrates
        self.proteins = proteins
        self.fats = fats

    def __update_df(self):
        d = {'Food': self.food_list, 'Serving': self.serving_list,'Price': self.price_list,"Calories": self.calorie_list,"Carbs": self.carb_list,"Proteins": self.protein_list,"Fats": self.fat_list}
        self.df = pd.DataFrame(data=d)

    def add_food(self, name, serving, price, carbs, protein, fat, min_servings=0, max_servings=None):
        self.food_list.append(name)
        self.serving_list.append(serving)
        self.price_list.append(price)
        self.calorie_list.append(carbs*4 + protein*4 + fat*9)
        self.carb_list.append(carbs)
        self.protein_list.append(protein)
        self.fat_list.append(fat)
        self.bounds.append((min_servings,max_servings))
        self.__update_df()

    def get_food_arrays(self, id):
        return self.food_list[id], self.serving_list[id], self.price_list[id], self.calorie_list[id], self.carb_list[id], self.protein_list[id], self.fat_list[id]

    def get_food_df(self):
        return self.df

    def remove_food(self, id):
        self.food_list.pop(id)
        self.serving_list.pop(id)
        self.price_list.pop(id)
        self.calorie_list.pop(id)
        self.carb_list.pop(id)
        self.protein_list.pop(id)
        self.fat_list.pop(id)
        self.bounds.pop(id)
        self.__update_df()

    def remove_foods(self):
        self.food_list = []
        self.serving_list = []
        self.price_list = []
        self.calorie_list = []
        self.carb_list = []
        self.protein_list = []
        self.fat_list = []
        self.bounds = []
        self.__update_df()  

    def add_equality_constrain(self, params, const):
        self.A_eq.append(params)
        self.b_eq.append(const)
    
    def add_inequality_constrain(self, params, const):
        self.A_ub.append(params)
        self.b_ub.append(const)

    def remove_constrains(self):
        self.A_eq = []
        self.A_ub = []
        self.b_eq = []
        self.b_ub = []
        self.bounds = []

    def solve(self):
        if(len(self.food_list) == 0):
            raise RuntimeError("Foods list is empty")

        if(len(self.A_eq) == 0):
            self.A_eq = None
            self.b_eq = None
            raise RuntimeError("Can't solve problem without equality constraints")

        if(len(self.A_ub) == 0):
            self.A_ub = None
            self.b_ub = None

        c = list(self.df.Price)

        return linprog(c, A_eq=self.A_eq, b_eq=self.b_eq, A_ub=self.A_ub, b_ub=self.b_ub, bounds=self.bounds)
    
    def parse_result(self, res):
        if(res.success):
            food_ammount = round(res.x * self.df.Serving,4)
            res_calories = round(res.x * self.df.Calories,4)
            res_carbs = round(res.x * self.df.Carbs,4)
            res_proteins = round(res.x * self.df.Proteins,4)
            res_fats = round(res.x * self.df.Fats,4)
            
            out = {'Food': self.df.Food, "Servings":np.round(res.x,2),'Ammount g':food_ammount,'Carbs':res_carbs,'Protein':res_proteins,'Fat':res_fats,'Calories':res_calories}
            out_df = pd.DataFrame(data=out)
            print(tabulate(out_df, headers='keys', tablefmt='psql'))
            
            print()
            total_price = round(sum(res.x * self.df.Price),2)
            total_calories = round(sum(res.x * self.df.Calories),2)
            total_carbs = round(sum(res.x * self.df.Carbs),2)
            total_protein = round(sum(res.x * self.df.Proteins),2)
            total_fat = round(sum(res.x * self.df.Fats),2)
            
            print("Total diet price:",total_price,"Eur")
            print("Total calories:",total_calories,'g of',self.calories, 'g --> Delta is', self.calories - total_calories, 'g')
            print("Total carbs:",total_carbs,'g of',self.carbohydrates, 'g --> Delta is', self.carbohydrates - total_carbs, 'g')
            print("Total protein:",total_protein,'g of',self.proteins, 'g --> Delta is', self.proteins - total_protein, 'g')
            print("Total fat:",total_fat,'g of',self.fats, 'g --> Delta is', self.fats - total_fat, 'g')
        else:
            print(res.message)