from propagators import *
from heuristics import *
from cspbase import *
from kenken_csp import *
from tests import *
import os
import filecmp
import numpy as np


BOARDS = [ [[3],[11,21,3,0],[12,22,2,1],[13,23,33,6,3],[31,32,5,0]],
[[4],[11,21,6,3],[12,13,3,0],[14,24,3,1],[22,23,7,0],[31,32,2,2],[33,43,3,1],[34,44,6,3],[41,42,7,0]],
[[5],[11,21,4,1],[12,13,2,2],[14,24,1,1],[15,25,1,1],[22,23,9,0],[31,32,3,1],[33,34,44,6,3],[35,45,9,0],[41,51,7,0],[42,43,3,1],[52,53,6,3],[54,55,4,1]],
[[6],[11,21,11,0],[12,13,2,2],[14,24,20,3],[15,16,26,36,6,3],[22,23,3,1],[25,35,3,2],[31,32,41,42,240,3],[33,34,6,3],[43,53,6,3],[44,54,55,7,0],[45,46,30,3],[51,52,6,3],[56,66,9,0],[61,62,63,8,0],[64,65,2,2]],
[[5],[11,12,21,22,10,0],[13,14,23,24,34,18,0],[15,25,35,2,1],[31,32,33,1,1],[41,42,43,51,52,53,600,3],[44,54,55,2,2],[45,3]],
[[6],[11,12,13,2,2],[14,15,3,1],[16,26,36,11,0],[21,22,23,2,2],[24,25,34,35,40,3],[31,41,51,61,14,0],[32,33,42,43,52,53,3600,3],[44,54,64,120,3],[45,46,55,56,1,1],[62,63,5,1],[65,66,5,0]]]

def wrapper(fn, fname):
    if fn == None:
        return fn
    def core(*args, **kwargs):
        res = fn(*args, **kwargs)
        if type(res) == np.ndarray:
            res = res.tolist()
        print(res, file = open(fname, "a"))
        return res
    return core

def print_diff_files(dcmp):
    fail = 0
    for name in dcmp.diff_files:
        fail += 1
        print("diff_file %s found in %s and %s" % (name, dcmp.left, dcmp.right))
    for sub_dcmp in dcmp.subdirs.values():
        fail += print_diff_files(sub_dcmp)
    return fail

rep = {val_lcv: "lcv",
       ord_mrv: "mrv",
       ord_dh: "dh",
       prop_BT: "bt",
       prop_FC: "fc",
       prop_GAC: "gac",
       None: "none"}

var_ords = [None, ord_mrv, ord_dh]
val_ords = [None, val_lcv]
props = [prop_FC, prop_GAC]

generate = False

if generate:
    name = "test_output_gt"
else:
    name = "test_output"

if not os.path.exists(name):
    os.mkdir(name)

for var_ord, val_ord, prop in itertools.product(*[var_ords, val_ords, props]):
    prefix = "{}/{}-{}-{}".format(name, rep[var_ord], rep[val_ord], rep[prop])
    for i in range(6):
        if val_ord == val_lcv:
            break
        if prop == prop_FC and i > 1:
            break
        prop_f = "{}_board{}_prop.txt".format(prefix, i)
        var_f = "{}_board{}_var.txt".format(prefix, i)
        val_f = "{}_board{}_val.txt".format(prefix, i)
        for f in [prop_f, var_f, val_f]:
            open(f, "w").close()
        csp, var_array = kenken_csp_model(BOARDS[i])
        solver = BT(csp)
        solver.bt_search(wrapper(prop, prop_f), val_ord = wrapper(val_ord, val_f) , var_ord = wrapper(var_ord, var_f))

    for i in range(1, 10):
        prop_f = "{}_nqueens{}_prop.txt".format(prefix, i)
        var_f = "{}_nqueens{}_var.txt".format(prefix, i)
        val_f = "{}_nqueens{}_val.txt".format(prefix, i)
        for f in [prop_f, var_f, val_f]:
            open(f, "w").close()
        csp = nQueens(i)
        solver = BT(csp)
        solver.bt_search(wrapper(prop, prop_f), val_ord = wrapper(val_ord, val_f), var_ord = wrapper(var_ord, var_f))

# comparison = filecmp.dircmp('./test_output', './test_output_gt')
# res = print_diff_files(comparison)
# print("fail: {} file(s) are different".format(res) if res != 0 else "pass!")
print("Checking using git diff..")
try:
    os.system("git diff --no-index -b test_output_gt/ test_output/")
except:
    print("Failed to check using git diff. Please manually check the output files")
else:
    print("Finished.")