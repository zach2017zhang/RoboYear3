# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 20:02:01 2018

@author: chene
"""

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
from cspbase import Variable, Constraint, CSP
from itertools import permutations, product
from functools import reduce
import operator

def binary_ne_grid(kenken_grid):
    # TODO! IMPLEMENT THIS!
    variable_list = []
    variable_list_2d = []
    constraint_list = []
    n = kenken_grid[0][0]
    for i in range(n):
        variable_list_2d.append([])
        for j in range(n):
            variable = Variable("Var"+str(i+1)+str(j+1), [x for x in range(1,n+1)])
            variable_list.append(variable)
            variable_list_2d[i].append(variable)

    for i in range(n):
        for j in range(n-1):
            for k in range(j+1,n):
                #row
                tuples = []
                constraint = Constraint("ConsRow"+str(i+1)+str(j+1)+str(k+1), [variable_list[i*n+j],variable_list[i*n+k]])
                for t in permutations(list(range(1,n+1)),2):
                    tuples.append(t)
                constraint.add_satisfying_tuples(tuples)
                constraint_list.append(constraint)
                #col
                tuples = []
                constraint = Constraint("ConsColn"+str(i+1)+str(j+1)+str(k+1), [variable_list[j*n+i],variable_list[k*n+i]])
                for t in permutations(list(range(1,n+1)),2):
                    tuples.append(t)
                constraint.add_satisfying_tuples(tuples)
                constraint_list.append(constraint)
    csp = CSP("binary_ne_grid", variable_list)
    for cons in constraint_list:
        csp.add_constraint(cons)
    
    return csp, variable_list_2d
    
    #pass

def nary_ad_grid(kenken_grid):
    # TODO! IMPLEMENT THIS!
    variable_list = []
    variable_list_2d = []
    constraint_list = []
    n = kenken_grid[0][0]
    for i in range(n):
        variable_list_2d.append([])
        for j in range(n):
            variable = Variable("Var"+str(i+1)+str(j+1), [x for x in range(1,n+1)])
            variable_list.append(variable)
            variable_list_2d[i].append(variable)

    for i in range(n):
        #row
        tuples = []
        constraint = Constraint("ConsRow"+str(i+1), variable_list_2d[i])
        for t in permutations(list(range(1,n+1))):
            tuples.append(t)
        constraint.add_satisfying_tuples(tuples)
        constraint_list.append(constraint)
        #col
        tuples = []
        constraint = Constraint("ConsColn"+str(i+1), [variable_list_2d[row_i][i] for row_i in range(n)])
        for t in permutations(list(range(1,n+1))):
            tuples.append(t)
        constraint.add_satisfying_tuples(tuples)
        constraint_list.append(constraint)
    csp = CSP("nary_ad_grid", variable_list)
    for cons in constraint_list:
        csp.add_constraint(cons)
    
    return csp, variable_list_2d
    #pass

def kenken_csp_model(kenken_grid):
    # TODO! IMPLEMENT THIS!
    variable_list = []
    variable_list_2d = []
    constraint_list = []
    n = kenken_grid[0][0]
    for i in range(n):
        variable_list_2d.append([])
        for j in range(n):
            variable = Variable("Var"+str(i+1)+str(j+1), [x for x in range(1,n+1)])
            variable_list.append(variable)
            variable_list_2d[i].append(variable)

    for i in range(n):
        #row
        tuples = []
        constraint = Constraint("ConsRow"+str(i+1), variable_list_2d[i])
        for t in permutations(list(range(1,n+1))):
            tuples.append(t)
        constraint.add_satisfying_tuples(tuples)
        constraint_list.append(constraint)
        #col
        tuples = []
        constraint = Constraint("ConsColn"+str(i+1), [variable_list_2d[row_i][i] for row_i in range(n)])
        for t in permutations(list(range(1,n+1))):
            tuples.append(t)
        constraint.add_satisfying_tuples(tuples)
        constraint_list.append(constraint)
    
    num_cons = 1
    for kenken_cons in kenken_grid[1:]:
        if len(kenken_cons) == 2:
            constraint = Constraint("KenKen"+str(num_cons+1), [variable_list_2d[int(str(kenken_cons[0])[0])-1][int(str(kenken_cons[0])[1])-1]])
            constraint.add_satisfying_tuples([[kenken_cons[1]]])
            constraint_list.append(constraint)
        else:
            constraint = Constraint("KenKen"+str(num_cons+1), [variable_list_2d[int(str(num)[0])-1][int(str(num)[1])-1] for num in kenken_cons[:-2]])
            tuples = []
            if kenken_cons[-1] == 0: #+
                for trial in product(list(range(1,n+1)),repeat = (len(kenken_cons)-2)):
                    if reduce(operator.add,trial) == kenken_cons[-2]:
                        tuples.append(trial)
            elif kenken_cons[-1] == 1: #-
                for trial in product(list(range(1,n+1)),repeat = (len(kenken_cons)-2)):
                    if reduce(operator.sub,trial) == kenken_cons[-2]:
                        for perm_trial in permutations(trial):
                            if not perm_trial in tuples:
                                tuples.append(perm_trial)
            elif kenken_cons[-1] == 2: #/
                for trial in product(list(range(1,n+1)),repeat = (len(kenken_cons)-2)):
                    if reduce(operator.truediv,trial) == kenken_cons[-2]:
                        for perm_trial in permutations(trial):
                            if not perm_trial in tuples:
                                tuples.append(perm_trial)
            else: #*
                for trial in product(list(range(1,n+1)),repeat = (len(kenken_cons)-2)):
                    if reduce(operator.mul,trial) == kenken_cons[-2]:
                        tuples.append(trial)
            constraint.add_satisfying_tuples(tuples)
            constraint_list.append(constraint)
            num_cons += 1
            
    csp = CSP("kenken_csp_model", variable_list)
    for cons in constraint_list:
        csp.add_constraint(cons)
    
    return csp, variable_list_2d
    #pass