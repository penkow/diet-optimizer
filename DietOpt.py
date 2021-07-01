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
        d = {'Food': self.food_list, 'Serving_(g)': self.serving_list,'Price_(EUR)': self.price_list,"Calories": self.calorie_list,"Carbs_(g)": self.carb_list,"Proteins_(g)": self.protein_list,"Fats_(g)": self.fat_list}
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
        if(len(self.df) == 0):
            raise RuntimeError("Foods list is empty")

        if(len(self.A_eq) == 0):
            self.A_eq = None
            self.b_eq = None
            raise RuntimeError("Can't solve problem without equality constraints")

        if(len(self.A_ub) == 0):
            self.A_ub = None
            self.b_ub = None

        c = list(self.df['Price_(EUR)'])

        return linprog(c, A_eq=self.A_eq, b_eq=self.b_eq, A_ub=self.A_ub, b_ub=self.b_ub, bounds=self.bounds, method='simplex')
    
    def parse_result(self, res):
        if(res.success):
            food_ammount = round(res.x * self.df['Serving_(g)'],4)
            res_calories = round(res.x * self.df['Calories'],4)
            res_carbs = round(res.x * self.df['Carbs_(g)'],4)
            res_proteins = round(res.x * self.df['Proteins_(g)'],4)
            res_fats = round(res.x * self.df['Fats_(g)'],4)
            
            #out = {'Food': self.df.Food, "Servings":np.round(res.x,2),'Ammount_(g)':food_ammount,'Carbs':res_carbs,'Protein':res_proteins,'Fat':res_fats,'Calories':res_calories}
            out = {'Food': self.df.Food, 'Ammount (g)':food_ammount,'Carbs':res_carbs,'Protein':res_proteins,'Fat':res_fats,'Calories':res_calories}
            out_df = pd.DataFrame(data=out)

            print(tabulate(out_df, headers='keys', tablefmt='psql'))
            
            print()
            total_price = round(sum(res.x * self.df['Price_(EUR)']),2)
            total_calories = round(sum(res.x * self.df['Calories']),2)
            total_carbs = round(sum(res.x * self.df['Carbs_(g)']),2)
            total_protein = round(sum(res.x * self.df['Proteins_(g)']),2)
            total_fat = round(sum(res.x * self.df['Fats_(g)']),2)
            
            print("Total diet price:",total_price,"Eur")
            print("Total calories:",total_calories,'g of',self.calories, 'g --> Delta is', total_calories - self.calories, 'g')
            print("Total carbs:",total_carbs,'g of',self.carbohydrates, 'g --> Delta is', total_carbs - self.carbohydrates, 'g')
            print("Total protein:",total_protein,'g of',self.proteins, 'g --> Delta is', total_protein - self.proteins, 'g')
            print("Total fat:",total_fat,'g of',self.fats, 'g --> Delta is', total_fat - self.fats, 'g')
        else:
            print(res.message)

    def constrain_calories(self, type = "eq"):
        if(type == "eq"):
            self.add_equality_constrain(params = self.get_food_df().Calories, const = self.calories)
        elif(type =="un"):
            self.add_inequality_constrain(params = self.get_food_df().Calories, const = self.calories)
        else:
            print("Constrain type",type,"is unknown")

    def constrain_protein(self, type = "un"):
        if(type == "eq"):
            self.add_equality_constrain(params = self.get_food_df()['Proteins_(g)'], const = self.proteins)
        elif(type =="un"):
            self.add_inequality_constrain(params = self.get_food_df()['Proteins_(g)'], const = self.proteins)
        else:
            print("Constrain type",type,"is unknown")

    def constrain_carbs(self, type = "un"):
        if(type == "eq"):
            self.add_equality_constrain(params = self.get_food_df()['Carbs_(g)'], const = self.carbohydrates)
        elif(type =="un"):
            self.add_inequality_constrain(params = self.get_food_df()['Carbs_(g)'], const = self.carbohydrates)
        else:
            print("Constrain type",type,"is unknown")

    def constrain_fats(self, type = "un"):
        if(type == "eq"):
            self.add_equality_constrain(params = self.get_food_df()['Fats_(g)'], const = self.fats)
        elif(type =="un"):
            self.add_inequality_constrain(params = self.get_food_df()['Fats_(g)'], const = self.fats)
        else:
            print("Constrain type",type,"is unknown")

    def add_foods_from_xlsx(self, file_path):
        self.df = pd.read_excel(file_path)
        self.df = self.df.where(pd.notnull(self.df), None)

        for index, food in self.df.iterrows():
            bound = (food['Min_Servings'],food['Max_Servings'])
            self.bounds.append(bound)
            