"""Run the finish module with Instance/CFrame doubles, not Studio physics or visual evidence."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
R=Path(__file__).resolve().parents[1]; S=R/'src/ServerScriptService'
doc=json.loads((R/'prototypes/map10/finish_geometry.json').read_text())
assert set(doc['groups'])=={'Stadium','North','East','Coast','Landmark'}
assert all(not o['collidable'] for o in doc['parts'])
import re
roles=set(re.findall(r'\{role="([^"]+)",name=',(S/'CompactCity.luau').read_text()))
workers=(S/'World.luau').read_text().split('local function workerFinish',1)[1].split('local function trainerOutfit',1)[0]
assert len(roles)==7 and all(role+'={{' in workers for role in roles),'Missing Map 10 authored worker role'
assert 'not job.supporting' in (S/'World.luau').read_text()
subprocess.run([sys.executable,str(R/'tools/build_map10_finish.py'),'--check'],check=True)
script='''
local Vector3={new=function(x,y,z)return {X=x,Y=y,Z=z}end}
local Color3={fromRGB=function(r,g,b)return {R=r,G=g,B=b}end}
local Data=(function()
'''+(S/'Map10FinishGeometry.luau').read_text()+'''
end)()
local script={Parent={Map10FinishGeometry='data'}}
local function require(k)assert(k=='data');return Data end
local mt={__mul=function(a)return a end}
local function frame(...)return setmetatable({...},mt)end
local CFrame={new=frame,Angles=frame}
local UDim2={fromScale=function(...)return {...}end}
local enum=setmetatable({},{__index=function(_,key)return key end})
local Enum=setmetatable({},{__index=function()return enum end})
local nodes={}
local Instance={new=function(class)
 local o={ClassName=class}
 function o:IsA(k)return k==self.ClassName or k=='BasePart' and self.ClassName=='Part'end
 table.insert(nodes,o)
 return o
end}
local Finish=(function()
'''+(S/'Map10Finish.luau').read_text()+'''
end)()
local fixed=Instance.new('Part');fixed.Name='IslandCore0';fixed.CanCollide=true
fixed.CanQuery=true;fixed.Material='SmoothPlastic';fixed.Position=Vector3.new(2,4,8)
local old=Instance.new('Part');old.Name='Crystal0';old.CanCollide=false;old.CanQuery=false;old.CanTouch=false
local solidCrystal=Instance.new('Part');solidCrystal.Name='CrystalCollision';solidCrystal.CanCollide=true;solidCrystal.Transparency=0
local unaffected=Instance.new('Part');unaffected.Name='Other'
local world={GetChildren=function()return {fixed,old,solidCrystal,unaffected}end}
local folder=Finish.Build(world)
assert(folder.Parent==world and folder.Name=='Map10Finishing')
assert(fixed.CanCollide and fixed.CanQuery and fixed.Material=='SmoothPlastic' and fixed.Position.Y==4,'Base collision material or position changed')
assert(old.Transparency==1 and old.CastShadow==false and solidCrystal.Transparency==0,'Only old decorative bars may hide')
assert(unaffected.Color==nil and unaffected.Material==nil,'Non-map part changed')
local count,labels=0,0
for _,p in ipairs(nodes)do
 if (p.ClassName=='Part' or p.ClassName=='WedgePart') and p.Parent and p.Parent.Parent==folder then
  assert(not p.CanCollide and not p.CanQuery and not p.CanTouch and p.Anchored,'Decoration can affect gameplay')
  assert(p.Size.X>0 and p.Size.Y>0 and p.Size.Z>0 and p.Material~=nil and (p.ClassName=='WedgePart' or p.Shape~=nil),'Invalid decoration')
  if p.Material=='Neon' then assert(p.CastShadow==false,'Emissive accent casts shadow') end
  count+=1
 elseif p.ClassName=='SurfaceGui' then
  assert(p.AlwaysOnTop==false and p.Parent,'Labels should not reveal through walls')
  labels+=1
 end
end
assert(count==#Data and count>600 and count<=1100,'Total finishing props outside budget')
assert(labels==5,'Expected five world signs')
print('PASS '..count..' actual finishing props, original collision material retained, five occluded world signs')
'''
with tempfile.NamedTemporaryFile('w',suffix='.luau',prefix='tmp_map_finish_',dir=R/'tests',delete=False,encoding='utf-8') as f:
    f.write(script)
    path=Path(f.name)
try: subprocess.run(['luau',str(path)],cwd=R,check=True)
finally: path.unlink()
