class Food:
   def __init__(self, variation, cost, calories):
      self.variation = variation
      self.cost = cost
      self.calories = calories
      
   def food_information(self):
      print("Variation: " + self.variation + ", Cost: " + str(self.cost) + ", Calories: " +  str(self.calories))

class Snacks(Food):
   def __init__(self, variation, cost, calories):
      super().__init__(variation, cost, calories)
   
class Pastries(Food):
   def __init__(self, variation, cost, calories):
      super().__init__(variation, cost, calories)
   
   def bake(self):
      print("We just baked the " + self.variation + "!")
   
class Desserts(Food):
   def __init__(self, variation, cost, calories):
      super().__init__(variation, cost, calories)

my_food = Food("ice cream", 2, 150)
my_food.food_information()

my_snack = Snacks("crackers", 3, 100)

my_pastry = Pastries("Apple Fritter", 3, 100)
my_pastry.bake()