
import random
import numpy as np
import pandas as pd

NUM_BOX = 500
SIZES = [2, 4, 6]
NUMS_SIZE = [4, 3, 3]
NUM_BOXES = 5
WEIGHTS = [10, 20, 30]
NUT_SCORE = [25, 50, 75]

def gen_rand_size(i):
    sizes = np.random.normal(SIZES[i], 0.5, 3)
    sizes = list(map(lambda x: round(x, 1), sizes))
    if not all(s >= 1 for s in sizes):
        return gen_rand_size(i)
    return sizes

def gen_weight(i):
    x = round(np.random.normal(WEIGHTS[i], 5), 1)
    if x < 1: return gen_weight(i)
    return x

def gen_nut(i):
    x = round(np.random.normal(NUT_SCORE[i], 10), 1)
    if x < 1: return gen_nut(i)
    return x

boxes = []
print("Box sizes:")
for i in range(len(SIZES)):
    for _ in range(NUMS_SIZE[i]):
        sizes = gen_rand_size(i)
        print(sizes)
        for j in range(NUM_BOXES):
            boxes += [sizes.copy()]
print()
print("There are", len(boxes), "boxes")

for i in range(len(boxes)):
    x = 2
    if i < 40: x = 0
    elif i < 70: x = 1
    w = gen_weight(x)
    s = gen_nut(x)
    boxes[i] += [w, s]


total_weight = 0
total_volume = 0
total_nutrition_score = 0
for box in boxes:
    total_weight += box[3]
    total_nutrition_score += box[4]
    total_volume += box[0] * box[1] * box[2]

print("total weight:", round(total_weight, 1), "lbs")
print("total box volumn:", round(total_volume, 1), "cube feet")
print("total nutrition score:", round(total_nutrition_score, 1))

# Create a Pandas dataframe from the data.
df = pd.DataFrame({
    'width': list(map(lambda x: x[0], boxes)),
    'length': list(map(lambda x: x[1], boxes)),
    'height': list(map(lambda x: x[2], boxes)),
    'weight': list(map(lambda x: x[3], boxes)),
    'nutrition_score': list(map(lambda x: x[4], boxes)),
})

# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter('test.xlsx', engine='xlsxwriter')

# Convert the dataframe to an XlsxWriter Excel object.
df.to_excel(writer, sheet_name='Big Nutrition Data')

# Close the Pandas Excel writer and output the Excel file.
writer.save()

# ========================= OUTPUT =========================
# Box sizes:
# [1.8, 2.7, 1.9]
# [2.2, 1.9, 1.9]
# [2.4, 3.1, 1.7]
# [2.0, 2.0, 2.7]
# [4.0, 4.4, 4.6]
# [3.6, 4.5, 3.8]
# [3.7, 3.5, 3.5]
# [6.2, 6.1, 6.2]
# [6.1, 6.1, 6.5]
# [6.2, 5.9, 6.1]

# There are 50 boxes
# total weight: 595.4 lbs
# total box volumn: 4639.8 cube feet
# total nutrition score: 1420.9