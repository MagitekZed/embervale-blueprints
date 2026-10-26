"""Can you walk to everything? Runs a generator (without saving) and searches outward from its spawn point on foot, as
walk mode would: steps of one block up, any drop down, 2 m of headroom (mage_common.walk_reach). Lists the items and
labelled areas you can't reach, then which of those a 1 m jump gets you to.

Run: python walkcheck.py isle      (the generator's module name, in this folder)
"""
import contextlib
import importlib
import io
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mage_common import walk_columns, walk_reach, walk_problems

name = sys.argv[1] if len(sys.argv) > 1 else 'isle'
t0 = time.time()
with contextlib.redirect_stdout(io.StringIO()):
    mod = importlib.import_module(name)
P = mod.P
cols = walk_columns(P)
walk = walk_reach(P, 0.5, cols=cols)
probs = walk_problems(P, walk)
print(f'{len(walk)} squares reachable on foot; {len(probs)} things out of reach ({time.time() - t0:.0f} s)')
if probs:
    jump = walk_reach(P, 1.0, cols=cols)
    still = set(walk_problems(P, jump))
    for p_ in probs:
        print('  ', p_, '' if p_ in still else '(a jump gets you there)')
