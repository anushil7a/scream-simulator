"""Execute actual DodgeVisuals with a deterministic mock tree/Heartbeat. No visual claim."""
from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[1]
source=(root/'src/StarterPlayer/StarterPlayerScripts/DodgeVisuals.luau').read_text()
pre=r'''
local checks=0;local function check(v,m)assert(v,m);checks+=1 end
local allocated=0;local connections=0;local disconnected=0;local listeners={}
local function vec(x,y,z)return {X=x,Y=y,Z=z}end
local Vector3={new=vec};local Color3={fromRGB=vec}
local ColorSequence={new=function(v)return v end};local NumberSequence={new=function(v)return v end}
local Enum={Material={Neon='Neon'}}
local methods={}
local mt={__index=function(t,k)return methods[k] or rawget(t,'props')[k]end,
 __newindex=function(t,k,v)
  local p=rawget(t,'props');if k=='Parent' then
   if p.Parent then local a=p.Parent.children;for i=#a,1,-1 do if a[i]==t then table.remove(a,i)end end end
   p.Parent=v;if v then table.insert(v.children,t)end
  else p[k]=v end
 end}
local function node(class)
 allocated+=1;return setmetatable({props={ClassName=class,Name=class,children={},Size=vec(2,2,1),Transparency=0,CFrame='initial'}},mt)
end
function methods:IsA(class)return self.ClassName==class or class=='BasePart' and (self.ClassName=='Part' or self.ClassName=='MeshPart')end
function methods:GetChildren()return table.clone(self.children)end
function methods:Destroy()if self.destroyed then return end;self:ClearAllChildren();self.Parent=nil;self.destroyed=true end
function methods:ClearAllChildren()for _,c in ipairs(self:GetChildren())do c:Destroy()end end
function methods:Clone()
 local c=node(self.ClassName)
 for k,v in pairs(self.props)do if k~='children' and k~='Parent' then c[k]=v end end
 for _,child in ipairs(self.children)do local clone=child:Clone();clone.Parent=c end
 return c
end
local Instance={new=node};local typeof=function(v)return type(v)=='table' and getmetatable(v)==mt and 'Instance' or type(v)end
local workspace=node('Folder')
local Heartbeat={Connect=function(_,fn)
 connections+=1;local c={active=true,fn=fn};table.insert(listeners,c)
 function c:Disconnect()if self.active then self.active=false;disconnected+=1 end end
 return c
end}
local function tick(dt)for _,c in ipairs(table.clone(listeners))do if c.active then c.fn(dt)end end end
local game={GetService=function(_,name)assert(name=='RunService');return {Heartbeat=Heartbeat}end}
local function character()
 local c=node('Model');c.Name='Character';c.Parent=workspace
 for _,name in ipairs({'Head','UpperTorso','LeftFoot','RightFoot','LeftHand'})do
  local b=node('MeshPart');b.Name=name;b.Parent=c
  local script=node('Script');script.Parent=b
 end
 local extra=node('Part');extra.Name='HumanoidRootPart';extra.Parent=c
 return c
end
local function effectRoots()
 local roots={};for _,c in ipairs(workspace.children)do if c.Name=='LocalDodgeEchoes' then table.insert(roots,c)end end;return roots
end
local function all(root)
 local list={};local function walk(n)for _,c in ipairs(n.children)do table.insert(list,c);walk(c)end end;walk(root);return list
end
local Visuals=(function()
'''
post=r'''
end)()
local c=character();local before=allocated
check(not Visuals.Play(c,true) and allocated==before,'Reduced mode allocated effects')
check(not Visuals.Play(nil,false) and allocated==before,'Invalid character allocated effects')
check(Visuals.Play(c,false),'Valid play rejected')
check(#effectRoots()==1 and connections==1,'Initial root/connection missing')
local root=effectRoots()[1];check(#root.children==1,'First snapshot missing')
local echo=root.children[1];check(#echo.children==5,'Whitelist copied root or omitted body')
for _,part in ipairs(echo.children)do
 check(part.Anchored and not part.CanCollide and not part.CanTouch and not part.CanQuery and part.Massless,'Unsafe echo physics')
 check(part.CFrame=='initial' and part.TextureID=='','Echo pose/texture mismatch')
end
for _,n in ipairs(all(root))do check(n.ClassName~='Script','Cloned script survived')end
for _,b in ipairs(c.children)do if b:IsA('BasePart')then b.CFrame='moved' end end
tick(.16);check(#root.children==2,'Second actual-position sample missing')
for _,part in ipairs(root.children[2].children)do check(part.CFrame=='moved','Second echo used speculative offset or stale pose')end
tick(.20);check(#root.children==1 and root.children[1]~=echo,'Echo lifetime not measured from each sample')
tick(.25);check(#effectRoots()==0 and disconnected==1,'Cast expiry failed teardown')
Visuals.Play(c,false);local latest=effectRoots()[1];c.Parent=nil;tick(.01)
check(latest.destroyed and #effectRoots()==0 and disconnected==2,'Character removal failed cleanup')
c.Parent=workspace
Visuals.Play(c,false);local first=effectRoots()[1]
for _=1,4 do Visuals.Play(c,false)end
check(first.destroyed and #effectRoots()==4,'Concurrency cap failed eviction')
check(connections==3,'Allocated one Heartbeat per cast')
Visuals.Destroy();check(#effectRoots()==0 and disconnected==3,'Destroy failed global cleanup/disconnect')
local allocations=allocated;tick(1);check(allocated==allocations and #effectRoots()==0,'Destroyed callback recreated effects')
Visuals.Destroy();check(disconnected==3,'Destroy disconnected twice')
Visuals.Play(c,false);tick(.30)
check(#effectRoots()[1].children==1,'Stalled callback created a late second sample')
Visuals.Destroy()
-- More than sixteen recognized direct body objects still produce a capped echo.
for i=1,20 do local b=node('Part');b.Name='Head';b.Parent=c end
Visuals.Play(c,false);check(#effectRoots()[1].children[1].children==16,'Body part cap exceeded')
Visuals.Destroy()
print('PASS '..checks..' actual DodgeVisuals lifecycle checks; mocked tree/clock, not native rendering')
'''
with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=root/'tests',delete=False) as f:
 p=Path(f.name);f.write(pre+source+post)
try:subprocess.run(['luau',str(p)],cwd=root,check=True)
finally:p.unlink()
