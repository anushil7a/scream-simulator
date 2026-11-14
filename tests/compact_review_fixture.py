"""Actual native-fixture cleanup under mocked state; does not execute Roblox."""
from pathlib import Path
import argparse,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--negative-controls',action='store_true');args=p.parse_args()
s=(ROOT/'tests/StudioCompactCity.server.luau').read_text()
a=s.index(' local activePaths=');b=s.index(' local function check(',a);cleanup=s[a:b]
setup=r'''
local checks=0;local function check(ok,msg)assert(ok,msg);checks+=1 end
local player,session,character,root,old
local cancelled,restored=0,0
local World={Bots={{training=true},{training=false}}}
local function cancelSustained()cancelled+=1 end
local function restoreBot()restored+=1 end
'''
tests=r'''
local path={};function path:Destroy()self.destroyed=true end;activePaths[path]=true
local savedData={level=9};local savedBeam={};old={frame='original',anchor=false,session={data=savedData,sustained=savedBeam,micReady=false,protectedUntil=4}}
session={};for _,key in ipairs(sessionFields)do session[key]='changed'end
root={Parent=true,Anchored=true};character={Parent=true};function character:PivotTo(frame)self.frame=frame end
local ok,err=cleanup();check(ok and err=='','Cleanup unexpectedly failed')
check(path.destroyed and next(activePaths)==nil,'Active path not destroyed')
for _,key in ipairs(sessionFields)do check(session[key]==old.session[key],'Session field not restored')end
check(character.frame=='original' and root.Anchored==false,'Character not restored')
check(cancelled==1 and restored==1,'Beam or trainer cleanup missing')
local bad={};function bad:Destroy()error('fixture failure')end;activePaths[bad]=true
root.Anchored=true;session.data={};local ok,err=cleanup()
check(not ok and string.find(err,'Path cleanup',1,true),'Cleanup failure hidden')
check(root.Anchored==false and session.data==savedData,'One cleanup failure skipped remaining restoration')
character.Parent=nil;root.Parent=nil;check(cleanup(),'Removed character cleanup failed')
print('PASS '..checks..' actual fixture cleanup assertions; mocked only')
'''
def run(source,error=None):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=ROOT/'tests',encoding='utf-8',delete=False)as f:f.write(setup+source+tests);path=Path(f.name)
 try:r=subprocess.run(['luau',str(path)],text=True,capture_output=True)
 finally:path.unlink()
 out=r.stdout+r.stderr
 if error:assert r.returncode and error in out,out;print('PASS negative control:',error)
 else:assert r.returncode==0,out;print(out.strip())
run(cleanup)
if args.negative_controls:
 for old,new,error in [('path:Destroy()','local ignored=true;','Active path not destroyed'),('session[key]=old.session[key]','session[key]=session[key]','Session field not restored'),('root.Anchored=old.anchor','root.Anchored=true','Character not restored')]:
  mutated=cleanup.replace(old,new);assert mutated!=cleanup;run(mutated,error)
assert s.index('task.cancel(worker)')<s.index('local clean,detail=cleanup()')<s.index('report(false,"Fixture exceeded')
assert s.count('local clean,detail=cleanup()')==2
assert 'AgentCanJump=not npc' in s and 'AgentCanClimb=false' in s
assert 'math.abs(delta.Y)<=(npc and 1 or 3)' in s and 'Magnitude<=.25' in s
assert 'activePaths[path]=true' in s and 'path:Destroy();activePaths[path]=nil' in s
print('PASS timeout ordering, shared cleanup, NPC policy and bounded exact-goal source contracts')
