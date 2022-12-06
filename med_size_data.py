import gurobipy as gp
from gurobipy import GRB
from itertools import product
import openpyxl 

''' This code is used to test with small test case
Note: The truck size should be changed to realistic size
'''
class Box:
    def __init__(self, width, length, height, weight, nutrition_value):
        self.width = int(width)
        self.length = int(length)
        self.height = int(height)
        self.weight = int(weight)
        self.value = int(nutrition_value)

# get all combination of indices for avoid tons of for loops
def get_index_comb(*args):
    def get_combination(*args):
        return list(product(*args))
    l = []
    for arg in args:
        l.append([i for i in range(arg)])
    return get_combination(*l)

# ============================== DATA ==============================
truck_width = 5
truck_length = 9
truck_height = 7
truck_weight_cap = 30

# boxes data
boxes = []

data_file = "./project_data.xlsx"
wb = openpyxl.load_workbook(data_file)
boxes_raw_data = list(wb['Medium data'].values)

for i in range(1, len(boxes_raw_data)):
    box_data = boxes_raw_data[i][1:]
    boxes.append(Box(*box_data))

# number of box
num_box = len(boxes)

# binary indicator if box i can put on top/front/right to box j
t = [[False for _ in range(num_box)] for _ in range(num_box)]
f = [[False for _ in range(num_box)] for _ in range(num_box)]
r = [[False for _ in range(num_box)] for _ in range(num_box)]

for i, j in get_index_comb(num_box, num_box):
    if i == j: continue
    # top
    if boxes[i].width <= boxes[j].width and boxes[i].length <= boxes[j].length and boxes[i].weight <= boxes[j].weight:
        t[i][j] = True
    # right
    if boxes[i].width <= boxes[j].width and boxes[i].height <= boxes[j].height:
        r[i][j] = True
    # front
    if boxes[i].length <= boxes[j].length and boxes[i].height <= boxes[j].height:
        f[i][j] = True


# model
model = gp.Model()
w = model.addMVar((truck_width, truck_length, truck_height, num_box), vtype=GRB.INTEGER, lb=0, ub=1, name="w")


# ============================== CONSTRAINTS ==============================
# Constraint 1: All boxes are exclusively included inside the truck
# fit in length (only care height 0) for every row
for x in range(truck_width):
    sum = 0
    for y, i in get_index_comb(truck_length, num_box):
        sum += w[x, y, 0, i] * boxes[i].length
    model.addConstr(sum <= truck_length)

# fit in width (only care the first column, and height 0)
width_sum = 0
for x, i in get_index_comb(truck_width, num_box):
    width_sum += w[x, 0, 0, i] * boxes[i].width
model.addConstr(width_sum <= truck_length)

# fit in height (only care the same width and length)
for x, y in get_index_comb(truck_width, truck_length):
    sum = 0
    for z, i in get_index_comb(truck_height, num_box):
        sum += w[x, y, z, i] * boxes[i].height
    model.addConstr(sum <= truck_height)


# Constraint 2: Each box has at most 1 place to put
for i in range(num_box):
    sum = 0
    for x, y, z in get_index_comb(truck_width, truck_length, truck_height):
        sum += w[x, y, z, i]
    model.addConstr(sum <= 1)

# Constraint 3: Each coordination can only contain 1 box
for x, y, z in get_index_comb(truck_width, truck_length, truck_height):
    sum = 0
    for i in get_index_comb(num_box):
        sum += w[x, y, z, i]
    model.addConstr(sum <= 1)

# Constrant 4: box i can only be put on top of a box j 
# if the width and length and weight of i are respectively less or equal to the width and length and weight of j
for x, y in get_index_comb(truck_width, truck_length):
    for i, j in get_index_comb(num_box, num_box):
        if i == j or t[i][j]: continue
        # box i can not on top box j
        for z1, z2 in get_index_comb(truck_height, truck_height):
            if z1 >= z2: continue
            # z2 > z1
            model.addConstr(w[x, y, z2, i] + w[x, y, z1, j] <= 1)

# Constrant 5: box i can only be put in front of a box j 
# if the height and length of i are respectively less or equal to the height and length of j
# Note: only need to constraint on the first column (z = 0, y = 0)
for i, j in get_index_comb(num_box, num_box):
    if i == j or f[i][j]: continue
    # box i can not in front of box j
    for x1, x2 in get_index_comb(truck_width, truck_width):
        if x1 >= x2: continue
        # x2 > x1
        model.addConstr(w[x2, 0, 0, i] + w[x1, 0, 0, j] <= 1)


# Constrant 6: box i can only be put on right of a box j 
# if the width and height of i are respectively less or equal to the width and height of j
# Note: only need to constraint on z = 0
for x in get_index_comb(truck_width):
    for i, j in get_index_comb(num_box, num_box):
        if i == j or r[i][j]: continue
        # box i can not on right box j
        for y1, y2 in get_index_comb(truck_length, truck_length):
            if y1 >= y2: continue
            # y2 > y1
            model.addConstr(w[x, y2, 0, i] + w[x, y1, 0, j] <= 1)


# Constraint 7: Total boxes weight should not exceed truck capacity
total_weight = 0
for x, y, z, i in get_index_comb(truck_width, truck_length, truck_length, num_box):
    total_weight += w[x, y, z, i] * boxes[i].weight
model.addConstr(total_weight <= truck_weight_cap)

# Constraint 8: Put all boxes from left to right
for x in get_index_comb(truck_width):
    for y1, y2 in get_index_comb(truck_length, truck_length):
        if y1 >= y2: continue
        sum_1 = 0
        sum_2 = 0
        for i in get_index_comb(num_box):
            sum_1 += w[x, y1, 0, i]
            sum_2 += w[x, y2, 0, i]
        model.addConstr(sum_1 >= sum_2)

# Constraint 9: Put all boxes from back to front
for x1, x2 in get_index_comb(truck_width, truck_width):
    if x1 >= x2: continue
    sum_1 = 0
    sum_2 = 0
    for i in get_index_comb(num_box):
        sum_1 += w[x1, 0, 0, i]
        sum_2 += w[x2, 0, 0, i]
    model.addConstr(sum_1 >= sum_2)

# Constraint 10: Put all boxes from bottom to top
for x, y in get_index_comb(truck_width, truck_length):
    for z1, z2 in get_index_comb(truck_height, truck_height):
        if z1 >= z2: continue
        sum_1 = 0
        sum_2 = 0
        for i in get_index_comb(num_box):
            sum_1 += w[x, y, z1, i]
            sum_2 += w[x, y, z2, i]
        model.addConstr(sum_1 >= sum_2)

# Constraint 11: For each box, total weight of boxes above it do not exceed 2 times of its weight
for x, y in get_index_comb(truck_width, truck_length):
    for z1 in get_index_comb(truck_height):
        w = 0
        for i in get_index_comb(num_box):
            w += w[x, y, z1, i] * boxes[i].weight

        sum = 0
        for z2, j in get_index_comb(truck_height, num_box):
            if z2 <= z1: continue
            sum += w[x, y, z2, j] * boxes[j].weight
        model.addConstr(sum <= 2 * w)



# ============================== OBJECTIVE ==============================
# Maximize the nutrition value delivered
objective = 0
for x, y, z, i in get_index_comb(truck_width, truck_length, truck_height, num_box):
    objective += w[x, y, z, i] * boxes[i].value
model.setObjective(objective, GRB.MAXIMIZE)

model.optimize()

def extract_data(var):
    num = int(var[2:len(var) - 1])
    i = num % num_box
    num //= num_box
    z = num % truck_height
    num //= truck_height
    y = num % truck_length
    num //= truck_length
    x = num
    print(f"box {i} put in coordinate ({x}, {y}, {z})")

print("Organizing boxes:")
for i in range(len(boxes)):
    print(f"box {i} with size ({boxes[i].width}, {boxes[i].length}, {boxes[i].height}) and weight {boxes[i].weight} and nutrition score {boxes[i].value}")

print()
print("RESULT:")
print("Max Nutrition: %g" % model.objVal)
for v in model.getVars():
    if(int(v.x) == 1):
        extract_data(v.varName)

# Organizing boxes:
# box 0 with size (1, 1, 1) and weight 5 and nutrition score 99
# box 1 with size (1, 1, 1) and weight 7 and nutrition score 30
# box 2 with size (2, 2, 1) and weight 12 and nutrition score 3
# box 3 with size (2, 2, 1) and weight 8 and nutrition score 70

# RESULT:
# Max Nutrition: 169
# box 3 put in coordinate (0, 0, 0)
# box 0 put in coordinate (0, 0, 1)