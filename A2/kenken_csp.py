'''
All models need to return a CSP object, and a list of lists of Variable objects 
representing the board. The returned list of lists is used to access the 
solution. 

For example, after these three lines of code

    csp, var_array = kenken_csp_model(board)
    solver = BT(csp)
    solver.bt_search(prop_FC, var_ord)

var_array[0][0].get_assigned_value() should be the correct value in the top left
cell of the KenKen puzzle.

The grid-only models do not need to encode the cage constraints.

1. binary_ne_grid (worth 10/100 marks)
    - A model of a KenKen grid (without cage constraints) built using only 
      binary not-equal constraints for both the row and column constraints.

2. nary_ad_grid (worth 10/100 marks)
    - A model of a KenKen grid (without cage constraints) built using only n-ary 
      all-different constraints for both the row and column constraints. 

3. kenken_csp_model (worth 20/100 marks) 
    - A model built using your choice of (1) binary binary not-equal, or (2) 
      n-ary all-different constraints for the grid.
    - Together with KenKen cage constraints.

'''

import itertools
from cspbase import *

def inequality_constraint(var1, var2):
    con = Constraint(name=var1.name + "_" + var2.name,
                     scope=[var1, var2])
    sat_tuples = []
    for val1, val2 in itertools.product(*[var1.dom, var2.dom]):
        if val1 != val2:
            sat_tuples.append((val1, val2))
    con.add_satisfying_tuples(sat_tuples)
    return con

def permutation_constraint(vars, name):
    con = Constraint(name = name,
                     scope = vars)
    domain = vars[0].dom
    sat_tuples = itertools.permutations(domain)
    con.add_satisfying_tuples(sat_tuples)
    return con

def check(values, target, op):
    res = None
    for val in values:
        if res == None:
            res = val
        else:
            if op == 2 and res % val != 0:
                return False
            if op == 0: res += val
            if op == 1: res -= val
            if op == 3: res *= val
            if op == 2: res //= val

    if res == target:
        return True
    return False

def combination_generator(domain, res, store, prev, max_val, num):
    if num == 0:
        res.append(tuple(store))
        return
    for i in range(prev, max_val):
        store.append(domain[i])
        combination_generator(domain, res, store, i, max_val, num - 1)
        store.pop()

def cage_constraint(vars, name, target, op):
    con = Constraint(name=name,
                     scope=vars)
    domain = vars[0].dom
    sat_tuples = []

    if op == 0 or op == 3:
        tuples = []
        combination_generator(domain, tuples, [], 0, len(domain), len(vars))
    else:
        tuples = itertools.product(domain, repeat = len(vars))

    for values in tuples:
        if check(values, target, op):
            values_col = itertools.permutations(values)
            sat_tuples.extend(values_col)

    con.add_satisfying_tuples(sat_tuples)
    return con

def binary_ne_grid(kenken_grid):
    n = kenken_grid[0][0]
    coords = list(itertools.product(range(n),repeat = 2))
    vars = [Variable(name = str(coord), domain = list(range(1, n + 1))) for coord in coords]
    csp = CSP(name = "binary_ne_grid", vars = vars)
    for index in range(n):
        for sub_index1 in range(n):
            for sub_index2 in range(sub_index1 + 1, n):
                # row
                var1 = vars[index * n + sub_index1]
                var2 = vars[index * n + sub_index2]
                con = inequality_constraint(var1, var2)
                csp.add_constraint(con)

                # column
                var1 = vars[index + sub_index1 * n]
                var2 = vars[index + sub_index2 * n]
                con = inequality_constraint(var1, var2)
                csp.add_constraint(con)
    vars = [[vars[i * n + j] for j in range(n)] for i in range(n)]
    return csp, vars


def nary_ad_grid(kenken_grid):
    n = kenken_grid[0][0]
    coords = list(itertools.product(range(n), repeat=2))
    vars = [Variable(name=str(coord), domain=list(range(1, n + 1))) for coord in coords]
    csp = CSP(name="nary_ad_grid", vars=vars)
    for index in range(n):
        row_vars = [vars[index * n + i] for i in range(n)]
        column_vars = [vars[index + i * n] for i in range(n)]
        row_con = permutation_constraint(row_vars, "row" + str(index))
        column_con = permutation_constraint(column_vars, "column" + str(index))
        csp.add_constraint(row_con)
        csp.add_constraint(column_con)
    vars = [[vars[i * n + j] for j in range(n)] for i in range(n)]
    return csp, vars

def print_con(con):
    print("Constraint {}:".format(con.name))
    print(con.sat_tuples)

def kenken_csp_model(kenken_grid):
    csp, vars = nary_ad_grid(kenken_grid)
    n = kenken_grid[0][0]
    for cage_index in range(1, len(kenken_grid)):
        cage_des = kenken_grid[cage_index]
        num = len(cage_des) - 2
        op = cage_des[-1]
        target = cage_des[-2]
        c_vars = []
        for v in range(num):
            cell_i = (cage_des[v] // 10) - 1
            cell_j = (cage_des[v] % 10) - 1
            c_vars.append(vars[cell_i][cell_j])
        if len(c_vars) != 0:
            con = cage_constraint(c_vars, "cage" + str(cage_index), target, op)
            csp.add_constraint(con)

    return csp, vars