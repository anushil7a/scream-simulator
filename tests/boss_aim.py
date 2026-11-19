"""Actual shared server targeting and boss body samples under vector/cover doubles."""
from pathlib import Path
import subprocess, tempfile
R=Path(__file__).resolve().parents[1]
bootstrap=(R/'src/ServerScriptService/Bootstrap.server.luau').read_text()
a=bootstrap.index('local function bossInBeam(')
b=bootstrap.index('local function canCapture(',a)
rules=(R/'src/ServerScriptService/CombatRules.luau').read_text().split('\n',1)[1]
body='''
local Vector3={};local mt={}
function Vector3.new(x,y,z)return setmetatable({X=x,Y=y,Z=z},mt)end
function mt.__add(a,b)return Vector3.new(a.X+b.X,a.Y+b.Y,a.Z+b.Z)end
function mt.__sub(a,b)return Vector3.new(a.X-b.X,a.Y-b.Y,a.Z-b.Z)end
function mt.__mul(a,k)return Vector3.new(a.X*k,a.Y*k,a.Z*k)end
function mt.__index(a,k)
 if k=='Magnitude'then return math.sqrt(a.X*a.X+a.Y*a.Y+a.Z*a.Z)end
 if k=='Dot'then return function(b,c)return b.X*c.X+b.Y*c.Y+b.Z*c.Z end end
end
local V=Vector3.new
local Rules=(function()
'''+rules+'''
end)()
local model={}
local cover=false
local rays=0
local function audible(_,origin,target,boss)
 assert(boss==model,'Wrong LOS exclusions')
 rays+=1
 return not cover
end
'''+bootstrap[a:b]+'''
local boss={root={Position=V(0,7,12)},model=model,spec={scale=1.4}}
local function aim(y,length,x)return bossInBeam(boss,{},V(x or 0,y,0),V(0,0,1),length,1)end
assert(aim(7,24),'Center hit lost')
assert(aim(11.9,24),'New upper-body surface should register')
assert(aim(2.8,24),'Lower-body surface should register')
assert(not aim(15.5,24) and not aim(7,24,8),'Aim volume is too broad')
assert(not aim(7,11.9),'Raised samples bypass the clipped beam length')
local before=rays
cover=true;assert(not aim(7,24) and rays>before,'Cover should block each candidate ray')
cover=false;boss.spec.scale=nil
assert(aim(7,24) and not aim(12.7,24),'Unscaled fallback should stay smaller')
boss.root.Position=V(0,14,24);boss.spec.scale=2.8
assert(aim(14,32) and aim(23.8,32) and aim(5.6,32),'Double scale lost proportional body hits')
assert(not aim(31,32) and not aim(14,32,16),'Double scale extended off-body')
assert(not aim(14,23.9),'Double scale extended beam length')
cover=true;assert(not aim(14,32),'Double scale bypassed cover')
print('PASS boss body, upper/lower aim, off-body miss, clipped beam and cover')
'''
assert 'bosses:CanHit(boss,ctx.player,now) and bossInBeam(' in bootstrap
assert 'bosses:CanHit(boss,p,now) and bossInBeam(' in bootstrap
with tempfile.NamedTemporaryFile(mode='w',dir=R/'tests',prefix='tmp_boss_aim_',suffix='.luau',delete=False) as f:
 f.write(body);path=Path(f.name)
try:subprocess.run(['luau',str(path)],cwd=R,check=True)
finally:path.unlink()
