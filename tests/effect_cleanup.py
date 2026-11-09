"""Actual pooled particle cleanup with fake tweens/instances; no rendering evidence."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'src/StarterPlayer/StarterPlayerScripts/ScreamEffects.luau').read_text();s=s.rsplit('return Effects',1)[0]
setup='''
local created={};local queue={};local tweens={}
local Instance={new=function()local p={Destroy=function(self)self.destroyed=true;self.Parent=nil end};table.insert(created,p);return p end}
local Tween={Create=function()local t={Play=function()end,Cancel=function(self)self.canceled=true end};table.insert(tweens,t);return t end}
local game={GetService=function()return Tween end};local workspace={}
local task={delay=function(_,fn)table.insert(queue,fn)end}
local Enum={PartType={Block='block'},Material={Neon='neon'},EasingStyle={Quad='quad'},EasingDirection={Out='out'}}
local TweenInfo={new=function()return {}end}
'''
checks='''
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
particle('core',{}, {}, {},nil,.2);particle('detail',{}, {}, {},nil,.2)
check(Effects.Budget().core==1 and Effects.Budget().detail==1,'Fixture did not allocate particles')
queue[1]();check(Effects.Budget().cachedCore==1 and Effects.Budget().core==0,'Normal expiry did not pool particle')
Effects.Clear()
check(created[1].destroyed and created[2].destroyed and tweens[2].canceled,'Cleanup retained cached/live particles or tween')
local b=Effects.Budget();check(b.core==0 and b.detail==0 and b.cachedCore==0 and b.cachedDetail==0,'Cleanup retained budget/pool')
queue[2]();Effects.Clear()
b=Effects.Budget();check(b.detail==0 and b.cachedDetail==0,'Late expiry revived destroyed pool or underflowed budget')
particle('detail',{}, {}, {},nil,.2)
check(#created==3 and Effects.Budget().detail==1,'Reusable cleanup prevented later rendering')
queue[2]();check(Effects.Budget().detail==1,'Old expiry changed new effect budget')
queue[3]();check(Effects.Budget().detail==0 and Effects.Budget().cachedDetail==1,'New effect failed normal expiry')
Effects.Clear();check(created[3].destroyed,'Second lifecycle retained cached part')
print('PASS '..checks..' actual effect pool cleanup checks with mocked tweens')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
 path=Path(f.name);f.write(setup+s+checks)
try: subprocess.run(['luau',str(path)],cwd=root,check=True)
finally: path.unlink()
