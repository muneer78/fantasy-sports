import random

teams = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th']

randomList = random.shuffle(
  teams, weights=(1, 2, 4, 8, 16, 32, 64, 128, 256, 512), k=10)
  
print(randomList)