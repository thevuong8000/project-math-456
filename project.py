import gurobipy as gp
from gurobipy import GRB
from itertools import product

class Box:
    def __init__(self, width, length, height, weight, nutrition_value):
        self.width = width
        self.length = length
        self.height = height
        self.weight = weight
        self.value = nutrition_value

# get all combination of indices for avoid tons of for loops
def get_index_comb(*args):
    def get_combination(*args):
        return list(product(*args))
    l = []
    for arg in args:
        l.append([i for i in range(arg)])
    return get_combination(*l)

# ============================== DATA ==============================
# truck size
truck_width = 10
truck_length = 10
truck_height = 10
truck_weight_cap = 12600

# boxes data
boxes = []

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

# Constrant 3: box i can only be put on top of a box j 
# if the width and length and weight of i are respectively less or equal to the width and length and weight of j
for x, y in get_index_comb(truck_width, truck_length):
    for i, j in get_index_comb(num_box, num_box):
        if i == j or t[i][j]: continue
        # box i can not on top box j
        for z1, z2 in get_index_comb(truck_height, truck_height):
            if z1 >= z2: continue
            # z2 > z1
            model.addConstr(w[x, y, z2, i] + w[x, y, z1, j] <= 1)

# Constrant 4: box i can only be put in front of a box j 
# if the height and length of i are respectively less or equal to the height and length of j
# Note: only need to constraint on the first column (z = 0, y = 0)
for i, j in get_index_comb(num_box, num_box):
    if i == j or f[i][j]: continue
    # box i can not in front of box j
    for x1, x2 in get_index_comb(truck_width, truck_width):
        if x1 >= x2: continue
        # x2 > x1
        model.addConstr(w[x2, 0, 0, i] + w[x1, 0, 0, j] <= 1)


# Constrant 5: box i can only be put on right of a box j 
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


# Constraint 6: Total boxes weight should not exceed truck capacity
total_weight = 0
for x, y, z, i in get_index_comb(truck_width, truck_length, truck_length, num_box):
    total_weight += w[x, y, z, i] * boxes[i].weight
model.addConstr(total_weight <= truck_weight_cap)

# ============================== OBJECTIVE ==============================
# Maximize the nutrition value delivered
objective = 0
for x, y, z, i in get_index_comb(truck_width, truck_length, truck_height, num_box):
    objective += w[x, y, z, i] * boxes[i].value
model.setObjective(objective, GRB.MAXIMIZE)

model.optimize()

for v in model.getVars():
	print(v.varName, int(v.x))