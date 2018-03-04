#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  3 01:39:28 2018

@author: yuchen
"""

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

def ord_dh(csp):
    # TODO! IMPLEMENT THIS!
    unasgn_vars = csp.get_all_unasgn_vars()
    vars_degree = []
    for var in unasgn_vars:
        var_degree = 0
        for c in csp.get_cons_with_var(var):
            if c.get_n_unasgn()>1:
                var_degree += c.get_n_unasgn()-1
        vars_degree.append(var_degree)
    #print (unasgn_vars[vars_degree.index(max(vars_degree))])
    return unasgn_vars[vars_degree.index(max(vars_degree))]
    #pass

def ord_mrv(csp):
    # TODO! IMPLEMENT THIS!
    unasgn_vars = csp.get_all_unasgn_vars()
    domain_size = [size.cur_domain_size() for size in unasgn_vars]
    #print (unasgn_vars[domain_size.index(min(domain_size))])
    return unasgn_vars[domain_size.index(min(domain_size))]
    #pass

def val_lcv(csp, var):
    # TODO! IMPLEMENT THIS!    
    vals = var.cur_domain().copy()
    flexibility_list = []
    
    for val in vals:
        var.assign(val)
        cons = csp.get_cons_with_var(var)
        prune_list = []
        val_list = []
        for c in cons:
            if c.get_n_unasgn() == 1:
                unasgn_vars = c.get_unasgn_vars()
                if not len(unasgn_vars) == 1:
                    print ("Error, more than one uninstantiated variables!")
                else:
                    unasgn_var = unasgn_vars[0]
                    current_domain = deepcopy(unasgn_var.cur_domain())
                    for d in current_domain:
                        unasgn_var.assign(d)
                        for vart in c.get_scope():
                            val_list.append(vart.get_assigned_value())
                        if not c.check(val_list):
                            unasgn_var.prune_value(d)
                            prune_list.append((unasgn_var,d))
                        unasgn_var.unassign()
                        val_list = []
        flexibility_list.append(len(prune_list))
        for variable, values in prune_list:
            variable.unprune_value(values)
        var.unassign()
    result = []
    while len(flexibility_list) != 0:
        result.append(vals.pop(flexibility_list.index(min(flexibility_list))))
        flexibility_list.remove(min(flexibility_list))
    
    #print (result)
    return result
    #pass