"""Execute actual four-way server math with synthetic ray/block hits, not native physics."""
from pathlib import Path
import tempfile,subprocess
r=Path(__file__).resolve().parents[1]
code=r'''
local n=0;local function check(v,m)assert(v,m);n+=1 end
local V={};V.__index=function(t,k)if k=='Magnitude' then return math.sqrt(t.X^2+t.Y^2+t.Z^2) elseif k=='Unit' then local m=math.sqrt(t.X^2+t.Y^2+t.Z^2);return setmetatable({X=t.X/m,Y=t.Y/m,Z=t.Z/m},V) end return V[k] end
local Vector3={new=function(x,y,z)return setmetatable({X=x,Y=y,Z=z},V)end}
V.__add=function(a,b)return Vector3.new(a.X+b.X,a.Y+b.Y,a.Z+b.Z)end
V.__sub=function(a,b)return Vector3.new(a.X-b.X,a.Y-b.Y,a.Z-b.Z)end
V.__mul=function(a,b)return Vector3.new(a.X*b,a.Y*b,a.Z*b)end
function V:Dot(b)return self.X*b.X+self.Y*b.Y+self.Z*b.Z end
local CFrame={new=function(p)return setmetatable({Position=p},{__mul=function(a)return a end})end}
local M=(function()
'''+(r/'src/ServerScriptService/DodgeMotion.luau').read_text()+r'''
end)()
local frame={RightVector=Vector3.new(1,0,0),LookVector=Vector3.new(0,0,-1),Position=Vector3.new(0,3,0),Rotation={}}
for _,case in ipairs({{-1,-1},{1,1},{0,1},{math.huge,1},{'left',1},{0/0,1}})do
 local d,side=M.Direction(frame,Vector3.new(0,0,0),case[1]);check(side==case[2] and d.X==case[2] and d.Y==0 and d.Z==0,'side validation')
end
local d,side=M.Direction(frame,Vector3.new(-1,0,0),nil);check(side==-1 and d.X==-1,'movement fallback left')
for _,case in ipairs({{'Left',-1,0},{'Right',1,0},{'Forward',0,-1},{'Back',0,1}})do
 local d,side,front=M.Direction(frame,Vector3.new(0,0,0),case[1]);check(d.X==case[2] and d.Z==case[3] and d.Magnitude==1,'cardinal authoritative axis')
end
for _,bad in ipairs({{},true,false,'ForwardLeft',math.huge,0/0,Vector3.new(100,0,100)})do
 local d=M.Direction(frame,Vector3.new(0,0,-1),bad);check(d.Z==-1 and d.Magnitude==1,'malformed payload fallback')
end
for _,move in ipairs({Vector3.new(1,0,-1),Vector3.new(-1,0,-1)})do
 local d=M.Direction(frame,move,nil);check(d.Z==-1 and d.X==0,'forward diagonal tie')
end
local rotated={RightVector=Vector3.new(0,0,1)}
local d=M.Direction(rotated,Vector3.new(0,0,0),'Forward');check(d.X==1 and d.Z==0,'server rotated facing')
local h={MaxSlopeAngle=60};local mode='flat';local rays,blocks=0,0
local travel=Vector3.new(1,0,0)
local world={}
function world:Raycast(origin)
 rays+=1
 local along=origin:Dot(travel)
 if mode=='edge' and along>1 then return nil end
 return {Position=Vector3.new(origin.X,mode=='ramp' and along*.2 or mode=='step' and along>0 and 2 or 0,origin.Z),Normal=Vector3.new(0,mode=='steep' and .2 or 1,0)}
end
function world:Blockcast(_,_,delta)blocks+=1;check(delta.Magnitude<.6,'substep bounded');return mode=='wall' and {} or nil end
for _,axis in ipairs({Vector3.new(1,0,0),Vector3.new(-1,0,0),Vector3.new(0,0,-1),Vector3.new(0,0,1)})do
 travel=axis
for _,m in ipairs({'flat','ramp','edge','steep','step','wall'}) do
 mode=m;rays=0;blocks=0
 local result=M.Step(world,frame,axis,3,{},h)
 if m=='flat' then check(result and result:Dot(axis)==3 and result.Y==3,'flat travel')
 elseif m=='ramp' then check(result and math.abs(result.Y-3.6)<.001,'ramp height')
 else check(result==nil,'reject '..m) end
end
end
check(M.Step(world,frame,Vector3.new(1,0,0),0,{},h)==frame.Position,'zero step safe')
print('PASS '..n..' actual dodge math checks with mocked geometry; native physics pending')
'''
client=(r/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
start=client.index('local function dodge()')
fragment=client[start:client.index('local controls=',start)]
code += r'''
local keys={};local blockedNow=false;local calls={};local move=Vector3.new(0,0,0)
local root={CFrame={RightVector=Vector3.new(1,0,0),LookVector=Vector3.new(0,0,-1)}}
local h={MoveDirection=move};local c={FindFirstChild=function()return root end,FindFirstChildOfClass=function()return h end}
local p={Character=c};local UIS={IsKeyDown=function(_,key)return keys[key]end}
local Enum={KeyCode={A='A',D='D',W='W',S='S'}}
local action={FireServer=function(_,verb,side)table.insert(calls,{verb,side})end}
local function cancelCapture()end
local function blocked()return blockedNow end
''' + fragment + r'''
for _,case in ipairs({
 {{},0,0,'Right'},{{A=true},0,0,'Left'},{{D=true},0,0,'Right'},
 {{W=true},0,0,'Forward'},{{S=true},0,0,'Back'},
 {{W=true,A=true},0,0,'Forward'},{{S=true,D=true},0,0,'Back'},
 {{W=true,S=true,A=true},0,0,'Left'},{{A=true,D=true,W=true,S=true},0,0,'Right'},
 {{},-1,0,'Left'},{{},1,0,'Right'},{{},0,-1,'Forward'},{{},0,1,'Back'},
 {{},.5,-.5,'Forward'},{{},-.8,.2,'Left'},{{},.02,.03,'Right'}
})do
 keys=case[1];h.MoveDirection=Vector3.new(case[2],0,case[3]);dodge()
 check(calls[#calls][1]=='Dodge' and calls[#calls][2]==case[4],'desktop/joystick/fallback intent')
end
local count=#calls;blockedNow=true;dodge();check(#calls==count,'blocked input escaped')
print('PASS desktop/joystick/default intent using actual client function')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=r/'tests',delete=False) as f:f.write(code);p=Path(f.name)
try:subprocess.run(['luau',str(p)],check=True,cwd=r)
finally:p.unlink()
s=(r/'src/ServerScriptService/Bootstrap.server.luau').read_text()
assert 'DodgeMotion.Step(workspace' in s and 'CFrame.new(target)*facing' in s
assert 'then dodge(p,arg);return' in s
s=(r/'src/StarterPlayer/StarterPlayerScripts/RunAnimation.client.luau').read_text()
assert '-math.pi*2*t' not in s and 'DodgeSide' in s
print('PASS four-way integration contracts')
