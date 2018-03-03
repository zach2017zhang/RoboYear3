'''
This file will contain different variable ordering heuristics to be used within
bt_search.

1. ord_dh(csp)
    - Takes in a CSP object (csp).
    - Returns the next Variable to be assigned as per the DH heuristic.
2. ord_mrv(csp)
    - Takes in a CSP object (csp).
    - Returns the next Variable to be assigned as per the MRV heuristic.
3. val_lcv(csp, var)
    - Takes in a CSP object (csp), and a Variable object (var)
    - Returns a list of all of var's potential values, ordered from best value 
      choice to worst value choice according to the LCV heuristic.

The heuristics can use the csp argument (CSP object) to get access to the 
variables and constraints of the problem. The assigned variables and values can 
be accessed via methods.
'''

import random
from copy import deepcopy
import numpy as np
import itertools

def ord_dh(csp):
    target, target_var = -1, None
    for var in csp.get_all_unasgn_vars():
        cons = csp.get_cons_with_var(var)
        num = 0
        for con in cons:
            vars_t = con.get_unasgn_vars()
            for var_t in vars_t:
                if var_t != var:
                    num += 1
        if num > target:
            target, target_var = num, var
    return target_var

def ord_mrv(csp):
    size_m, target_var = None, None
    for var in csp.get_all_unasgn_vars():
        if not size_m or var.cur_domain_size() < size_m:
            size_m, target_var = var.cur_domain_size(), var
    return target_var

def check_con(con):
    assert con.get_n_unasgn() == 0, "trying to check a constraint that is not full!"
    vals = []
    vars = con.get_scope()
    for var in vars:
        vals.append(var.get_assigned_value())
    return con.check(vals)

def val_lcv(csp, var):
    lst = []
    for val in var.cur_domain():
        var.assign(val)
        pruns = []
        constraints = csp.get_cons_with_var(var)
        fail = False
        for c in constraints:
            if c.get_n_unasgn() == 0:
                vals_t = []
                vars_t = c.get_scope()
                for var_t in vars_t:
                    vals_t.append(var_t.get_assigned_value())
                if not c.check(vals_t):
                    fail = True
                    break
            if c.get_n_unasgn() == 1:
                vals_t = []
                vars_t = c.get_scope()
                n_vars = len(vars_t)
                for var_t in vars_t:
                    vals_t.append(var_t.get_assigned_value())
                for i in range(n_vars):
                    if vals_t[i] == None:
                        domain, index = vars_t[i].cur_domain(), i
                fail_flag = True
                for attempt_val in domain:
                    vals_t[index] = attempt_val
                    if not c.check(vals_t):
                        vars_t[index].prune_value(attempt_val)
                        pruns.append((vars_t[index], attempt_val))
                    else:
                        fail_flag = False
                if fail_flag:
                    fail = True
                    break

        INF = float("inf") # infinity
        if not fail:
            lst.append((len(pruns), val))
        else:
            lst.append((INF, val))

        # restore everything
        for prun in pruns:
            var_t, attempt_val = prun
            var_t.unprune_value(attempt_val)
        var.unassign()

    lst = sorted(lst, key=lambda x: x[0])
    lst_val = [l[1] for l in lst]
    return np.array(lst_val)