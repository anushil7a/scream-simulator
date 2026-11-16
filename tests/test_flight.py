"""Actual TestFlight module in mocked server vector/physics environment; no native proof."""
from pathlib import Path
import tempfile,subprocess
r=Path(__file__).resolve().parents[1]
pre=r'''
local n=0;local function check(v,m)assert(v,m);n+=1 end
local V={};local mt={__type='Vector3'}
function V.new(x,y,z)return setmetatable({X=x,Y=y,Z=z},mt)end
mt.__add=function(a,b)return V.new(a.X+b.X,a.Y+b.Y,a.Z+b.Z)end
mt.__sub=function(a,b)return V.new(a.X-b.X,a.Y-b.Y,a.Z-b.Z)end
mt.__mul=function(a,b)return V.new(a.X*b,a.Y*b,a.Z*b)end
mt.__index=function(a,k)if k=='Magnitude'then return math.sqrt(a.X*a.X+a.Y*a.Y+a.Z*a.Z) elseif k=='Unit'then return a*(1/a.Magnitude)end end
V.zero=V.new(0,0,0);local Vector3=V
local typeof=function(v)return type(v)=='table' and getmetatable(v)==mt and 'Vector3' or type(v)end
local function cf(pos)return setmetatable({Position=pos,LookVector=V.new(0,0,-1)},{__add=function(a,d)return cf(a.Position+d)end})end
local studio=true;local game={GameId=0,PlaceId=0,GetService=function()return {IsStudio=function()return studio end}end}
local RaycastParams={new=function()return {}end};local Enum={RaycastFilterType={Exclude='Exclude'}}
local obstruction;local casts=0
local workspace={Blockcast=function(_,frame,size,delta,params)casts+=1;check(params.RespectCanCollide==true,'Collision filtering lost');return obstruction end}
local function fixture(anchored)
 local c={Parent=true};local root={Parent=c,Anchored=anchored==true,CFrame=cf(V.new(0,10,0)),owner='original',auto=false}
 setmetatable(root,{__index=function(t,k)if k=='Position'then return t.CFrame.Position end end})
 function root:IsA(t)return t=='BasePart'end
 function root:GetNetworkOwnershipAuto()return self.auto end
 function root:GetNetworkOwner()return self.owner end
 function root:SetNetworkOwner(v)self.owner=v end
 function root:SetNetworkOwnershipAuto()self.auto=true end
 local h={Parent=c,Health=100,AutoRotate=true}
 function c:FindFirstChild(name)if name=='HumanoidRootPart'then return root end end
 function c:FindFirstChildOfClass(name)if name=='Humanoid'then return h end end
 local p={Character=c,attrs={}};function p:SetAttribute(k,v)self.attrs[k]=v end
 return p,{testBaseline={}},root,h
end
local bounds={min=V.new(-20,-4,-20),max=V.new(20,220,20),localOnly=true}
local Flight=(function()
'''
# Recursive CFrame helper needs explicit local declaration in Luau.
pre=pre.replace('local function cf(pos)','local cf;cf=function(pos)')
post=r'''
end)()
local p,s,root,h=fixture()
check(not Flight.Start(p,s,false,bounds,0),'Unauthorized start')
s.testBaseline=nil;check(not Flight.Start(p,s,true,bounds,0),'Implicit test activation');s.testBaseline={}
for _,mode in ipairs({'studio','game','place','flag'})do
 studio=mode~='studio';game.GameId=mode=='game' and 1 or 0;game.PlaceId=mode=='place' and 1 or 0;bounds.localOnly=mode~='flag'
 check(not Flight.Start(p,s,true,bounds,0),'Shared/cloud flight accepted '..mode)
end
studio=true;game.GameId=0;game.PlaceId=0;bounds.localOnly=true
check(Flight.Start(p,s,true,bounds,0),'Start rejected');check(Flight.Active(s) and root.Anchored and not h.AutoRotate and p.attrs.TestFlight,'Missing flight state')
check(not Flight.Start(p,s,true,bounds,0),'Duplicate start overwrote origin')
for _,arg in ipairs({{x=2,y=0,z=0},{x=0,y=0,z=0,speed=99},{x=0,y=0,z=0,camera=1},{x=0,y=0},{x=0/0,y=0,z=0}})do check(not Flight.Input(p,s,arg,.01),'Invalid input accepted')end
check(Flight.Input(p,s,{x=1,y=1,z=1},.01),'Valid input rejected')
Flight.Step(p,s,true,bounds,.1,1)
check(math.abs((root.Position-V.new(0,10,0)).Magnitude-3.2)<.00001,'Speed/diagonal/dt cap failed')
check(root.Position.Z<0,'Positive z did not move forward')
local pos=root.Position;Flight.Step(p,s,true,bounds,.5,.1);check((root.Position-pos).Magnitude==0,'Stale input kept moving')
check(not Flight.Input(p,s,{x=1,y=0,z=0},.1),'Old timestamp accepted')
Flight.Input(p,s,{x=1,y=0,z=0},.51);obstruction={Distance=.5};pos=root.Position;Flight.Step(p,s,true,bounds,.52,.1)
check(math.abs((root.Position-pos).Magnitude-.4)<.00001,'Blockcast did not stop at obstacle');obstruction=nil
Flight.Stop(p,s);check(not Flight.Active(s) and not root.Anchored and h.AutoRotate and root.owner=='original' and not p.attrs.TestFlight,'Restore failed')
check((root.Position-V.new(0,10,0)).Magnitude==0,'Original position not restored');Flight.Stop(p,s)
for _,mode in ipairs({'auth','baseline','death','respawn','root','studio'})do
 p,s,root,h=fixture();Flight.Start(p,s,true,bounds,1)
 if mode=='baseline'then s.testBaseline=nil elseif mode=='death'then h.Health=0 elseif mode=='respawn'then p.Character={} elseif mode=='root'then root.Parent=nil elseif mode=='studio'then studio=false end
 check(not Flight.Step(p,s,mode~='auth',bounds,1.1,.1) and not Flight.Active(s),'Teardown failed '..mode)
 studio=true
end
p,s,root,h=fixture(true);check(not Flight.Start(p,s,true,bounds,0) and root.Anchored,'Preexisting anchored root accepted')
for _,mode in ipairs({'Sit','SeatPart','PlatformStand','knock','dodge'})do
 p,s,root,h=fixture();if mode=='knock' then s.knockedUntil=2 elseif mode=='dodge' then s.dodgingUntil=2 else h[mode]=true end
 check(not Flight.Start(p,s,true,bounds,0),'Unsafe motion start accepted '..mode)
end
p,s,root,h=fixture();root.CFrame=cf(V.new(0,3,0));check(Flight.Start(p,s,true,bounds,0),'Grounded coastal start rejected');Flight.Stop(p,s)
p,s,root,h=fixture();root.CFrame=cf(V.new(19.9,10,0));Flight.Start(p,s,true,bounds,0);Flight.Input(p,s,{x=1,y=0,z=0},0);Flight.Step(p,s,true,bounds,.1,.1);check(root.Position.X==20,'World bounds exceeded');Flight.Stop(p,s)
print('PASS '..n..' actual TestFlight security/movement/lifecycle checks; mocked server physics')
'''
with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=r/'tests',delete=False)as f:
 p=Path(f.name);f.write(pre+(r/'src/ServerScriptService/TestFlight.luau').read_text()+post)
try:subprocess.run(['luau',str(p)],cwd=r,check=True)
finally:p.unlink()
