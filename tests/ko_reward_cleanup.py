"""Bounded server-wide pair history; synthetic clock, no memory benchmark."""
from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[1]
checks="""
local C=require('../src/ReplicatedStorage/Shared/CombatCredit')
local h={pairs={}};local n=0;local function check(v,m)assert(v,m);n+=1 end
for id=1,C.MaxPairs do check(C.RepeatFactor(h,id,99999,0)==1,'Pair unexpectedly rejected') end
check(C.RepeatFactor(h,C.MaxPairs+1,99999,1)==0,'Unbounded history')
check(C.RepeatFactor(h,1,99999,60)==.5,'Full history lost existing eligibility')
check(C.RepeatFactor(h,C.MaxPairs+1,99999,600)==1,'Expired entries did not clear')
local count=0;for _ in pairs(h.pairs)do count+=1 end
check(count==1,'Historical pair entries retained')
print('PASS '..n..' bounded repeat-opponent cleanup checks')
"""
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
 path=Path(f.name);f.write(checks)
try: subprocess.run(['luau',str(path)],cwd=root,check=True)
finally: path.unlink()
