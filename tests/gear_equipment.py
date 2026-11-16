"""Execute actual Equipment with a tiny tree/transform mock, not Roblox physics."""
from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[1]
source=(root/'src/ServerScriptService/Equipment.luau').read_text()
code=r'''
local transform=setmetatable({},{__mul=function()return transform end})
-- Return a self-multiplying token; positional correctness requires native fitting.
local mt={};mt.__mul=function(a)return a end
local function cf()return setmetatable({},mt)end
local CFrame={new=cf,Angles=cf}
local Vector3={new=function(x,y,z)return {X=x,Y=y,Z=z}end}
local Color3={fromRGB=function(...)return {...}end}
local Enum={Material={SmoothPlastic=1,Neon=2},PartType={Ball=1,Cylinder=2}}
local methods={}
local function node(class,name)
 return setmetatable({ClassName=class,Name=name or class,children={},attrs={},Size={Y=1},CFrame=cf()},{__index=function(n,k)if k=='Parent' then return rawget(n,'_parent') end;return methods[k]end,__newindex=function(n,k,v)
  if k=='Parent' then local old=rawget(n,'_parent');if old then for i,x in ipairs(old.children)do if x==n then table.remove(old.children,i);break end end end
   if v then table.insert(v.children,n)end end
  rawset(n,k=='Parent' and '_parent' or k,v)
 end})
end
function methods:IsA(c)return self.ClassName==c or c=='BasePart' and self.ClassName=='MeshPart' or c=='BasePart' and self.ClassName=='Part'end
function methods:FindFirstChild(name)for _,c in ipairs(self.children)do if c.Name==name then return c end end end
function methods:GetDescendants()local all={};for _,c in ipairs(self.children)do table.insert(all,c);for _,d in ipairs(c:GetDescendants())do table.insert(all,d)end end;return all end
function methods:FindFirstChildWhichIsA(c)for _,d in ipairs(self:GetDescendants())do if d:IsA(c)then return d end end end
function methods:SetAttribute(k,v)self.attrs[k]=v end
function methods:GetAttribute(k)return self.attrs[k]end
function methods:PivotTo(v)self.pivot=v end
function methods:Destroy()self.Parent=nil;self.destroyed=true end
function methods:Clone()local n=node(self.ClassName,self.Name);for _,c in ipairs(self.children)do c:Clone().Parent=n end;return n end
local Instance={new=node};local storage=node('ServerStorage');local templates=node('Folder','GearTemplates');templates.Parent=storage
local game={GetService=function(_,name)assert(name=='ServerStorage');return storage end}
local Equipment=(function()
'''+source+r'''
end)()
local G=require('../src/ReplicatedStorage/Shared/GearCatalog')
local character=node('Model');local hand=node('Part','RightHand');hand.Parent=character;local torso=node('Part','UpperTorso');torso.Parent=character
local player={Character=character}
for _,item in ipairs(G.Items)do
 local template=node('Model',item.template);local mesh=node('MeshPart','Authored');mesh.Parent=template;template.Parent=templates
 Equipment.SyncGear(player,item)
 local model=character:FindFirstChild('ProgressionGear');assert(model and model:GetAttribute('GearId')==item.id and not model:GetAttribute('FallbackVisual'))
 assert(model:GetAttribute('MountKind')==(item.mount=='back' and 'back' or 'hand'))
 local part=model:FindFirstChild('Authored');assert(not part.Anchored and not part.CanCollide and not part.CanQuery and not part.CanTouch and part.Massless)
 local weld=part:FindFirstChild('WeldConstraint');assert(weld.Part0==(item.mount=='back' and torso or hand) and weld.Part1==part)
 Equipment.SyncGear(player,item);assert(character:FindFirstChild('ProgressionGear')==model,'Repeated sync duplicated model')
 Equipment.SyncGear(player,nil);assert(not character:FindFirstChild('ProgressionGear'))
 template:Destroy()
end
Equipment.SyncGear(player,G.Get('CelestialOrgan'))
local fallback=character:FindFirstChild('ProgressionGear');assert(fallback:GetAttribute('FallbackVisual') and fallback:GetAttribute('MountKind')=='hand')
Equipment.SyncGear(player,nil);assert(fallback.destroyed)
local respawn=node('Model');local arm=node('Part','Right Arm');arm.Parent=respawn;player.Character=respawn
Equipment.SyncGear(player,G.Get('MosaicMic'));assert(respawn:FindFirstChild('ProgressionGear'))
print('PASS actual equipment template/fallback lifecycle, pose tags, weld target and R6 fallback in mocked tree; not native geometry')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:path=Path(f.name);f.write(code)
try:subprocess.run(['luau',str(path)],cwd=root,check=True)
finally:path.unlink()
