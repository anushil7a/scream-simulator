"""Actual renderer/motion/controller with numeric CFrame and Instance doubles.
No Studio, network timing or mobile GPU claim.
"""
import ast,subprocess,tempfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
tree=ast.parse((R/'tests/boss_visuals.py').read_text())
pre=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='pre' for t in n.targets))
start=pre.index('local CF=');end=pre.index('Color3=',start)
cf=r'''
local CF={};CF.__index=CF
local function frame(p,r,u,b)return setmetatable({Position=p,r=r,u=u,b=b},CF)end
local function v(x,y,z)return Vector3.new(x,y,z)end
function CF:VectorToWorldSpace(x)return self.r*x.X+self.u*x.Y+self.b*x.Z end
CF.__mul=function(a,b)
 return frame(a.Position+a:VectorToWorldSpace(b.Position),a:VectorToWorldSpace(b.r),a:VectorToWorldSpace(b.u),a:VectorToWorldSpace(b.b))
end
function CF:Inverse()
 local r=v(self.r.X,self.u.X,self.b.X);local u=v(self.r.Y,self.u.Y,self.b.Y);local b=v(self.r.Z,self.u.Z,self.b.Z)
 local f=frame(v(0,0,0),r,u,b);f.Position=f:VectorToWorldSpace(-self.Position);return f
end
function CF:ToObjectSpace(other)return self:Inverse()*other end
function CF:Lerp(other,t)return frame(self.Position+(other.Position-self.Position)*t,self.r+(other.r-self.r)*t,self.u+(other.u-self.u)*t,self.b+(other.b-self.b)*t)end
CFrame={new=function(x,y,z,...)
 local p=type(x)=='table' and x or v(x or 0,y or 0,z or 0);local m={...}
 if #m==9 then return frame(p,v(m[1],m[4],m[7]),v(m[2],m[5],m[8]),v(m[3],m[6],m[9]))end
 return frame(p,v(1,0,0),v(0,1,0),v(0,0,1))
end,fromMatrix=frame}
CFrame.Angles=function(x,y,z)
 local sx,cx,sy,cy,sz,cz=math.sin(x),math.cos(x),math.sin(y),math.cos(y),math.sin(z),math.cos(z)
 return frame(v(0,0,0),v(1,0,0),v(0,cx,sx),v(0,-sx,cx))*frame(v(0,0,0),v(cy,0,-sy),v(0,1,0),v(sy,0,cy))*frame(v(0,0,0),v(cz,sz,0),v(-sz,cz,0),v(0,0,1))
end
CFrame.identity=CFrame.new()
'''
pre=pre[:start]+cf+pre[end:]
pre=pre.replace('local o={ClassName=class}','local o={ClassName=class,IsA=function(self,c)return c==self.ClassName or c=="BasePart" end}')
data=(R/'src/ReplicatedStorage/Shared/BossVisualData.luau').read_text()
render=(R/'src/StarterPlayer/StarterPlayerScripts/BossAppearance.luau').read_text().split('local Appearance=',1)[1]
motion=(R/'src/StarterPlayer/StarterPlayerScripts/BossPose.luau').read_text()
controller=(R/'src/StarterPlayer/StarterPlayerScripts/BossVisualController.luau').read_text()
checks=r'''
local function same(a,b)return (a.Position-b.Position).Magnitude<.00001 and (a.r-b.r).Magnitude<.00001 and (a.u-b.u).Magnitude<.00001 end
local function model(center)
 local m={Parent=true,WorldPivot=CFrame.new(center)}
 function m:SetAttribute(k,value)self[k]=value end
 function m:GetDescendants()local out={};for _,p in ipairs(created)do if p.Parent==self then table.insert(out,p)end end;return out end
 function m:PivotTo(target)local delta=target*self.WorldPivot:Inverse();for _,p in ipairs(self:GetDescendants())do p.CFrame=delta*p.CFrame end;self.WorldPivot=target end
 function m:Destroy()for _,p in ipairs(self:GetDescendants())do p.Parent=nil end;self.Parent=nil end
 return m
end
-- The stable level-70 key now contains the Seagull Captain, not the retired coil.
local names={};local nativeBudget=0
for _,e in ipairs(Data.leviathan)do
 names[e.name]=(names[e.name] or 0)+1
 nativeBudget+=e.kind=='Surface' and #e.triangles*2 or 1
end
for _,name in ipairs({'CaptainCoat','GullHead','HookedBeak','TricornFront','SirenHorn','CaptainHook','CaptainPeg','CutlassBlade'})do
 check(names[name]~=nil,'Seagull signature absent '..name)
end
check(names.SirenHorn==2 and names.SirenDriver==2,'paired sirens missing')
check(not names.LowerJaw and not names.DorsalFin,'retired sea creature leaked')
check(nativeBudget<=435,'Seagull exceeded old budget')
check(Motion.Group('leviathan','CutlassBlade',-1)=='armL','cutlass not attached to arm')
check(Motion.Group('leviathan','CaptainHook',2)=='armR','hook not attached to arm')
check(Motion.Group('leviathan','CaptainPeg',1)=='legR','peg gait not grouped')
check(Motion.Group('leviathan','SirenHorn',2)=='sirens','horn windup missing')
check(not same(Motion.Pose('leviathan','sirens',10,'Windup',1,1.4,false),CFrame.identity),'horn windup is static')
check(same(Motion.Pose('leviathan','sirens',10,'Windup',1,1.4,true),CFrame.identity),'reduced effects retained cosmetic pose (horn windup)')
for id in pairs(Data)do
 local center=v(20,64,-30);local m=model(center);created={}
 local ok,count=Appearance.Build(m,id,center,function()return true end,function()end,1.4)
 local animation=Motion.new(m,id,center,1.4);local initialCount=#created
 check(ok and count==initialCount and count<=450,'appearance budget')
 local grouped=0;for _,entries in pairs(animation.groups)do grouped+=#entries end
 check(grouped>0 and grouped<=count,'anatomy grouping empty/unbounded')
 local target=CFrame.new(v(24,64,-30))
 for i=1,100 do
  check(animation:Step(target,'Moving',100+i/30,1/30,false,100),'moving lifecycle')
  check(animation.frame.Position.X>=20 and animation.frame.Position.X<=24 and animation.frame.Position.Y==64,'root extrapolated/hovered')
  check(#created==initialCount,'per-frame instance allocation')
  for key,entries in pairs(animation.groups)do
   if key=='legL' or key=='legR' then for _,entry in ipairs(entries)do
    local localPose=animation.frame:ToObjectSpace(entry.part.CFrame)
    local rise=localPose.Position.Y-entry.base.Position.Y
    check(rise>=-.00001 and rise<=.18201,'walking foot sank or excessive lift')
   end end
  end
 end
 local cast=CFrame.new(v(22,64,-31))*CFrame.Angles(0,.6,0)
 animation:Step(cast,'Windup',104,.033,false,103)
 check(same(animation.frame,cast),'cast failed to snap authoritative root')
 local castFrames={};for i,p in ipairs(created)do castFrames[i]=p.CFrame end
 local posed={};for key,entries in pairs(animation.groups)do for _,entry in ipairs(entries)do posed[entry.part]=entry.part.CFrame end end
 animation:Step(cast,'Windup',104,.033,false,103)
 for p,pose in pairs(posed)do check(same(p.CFrame,pose),'late join/time-repeat pose drift')end
 for _,state in ipairs({'Moving','Windup','Recovery','Idle','Defeated'})do
  animation:Step(cast,state,105,.033,true,104)
  for key,entries in pairs(animation.groups)do for _,entry in ipairs(entries)do
   check(same(entry.part.CFrame,cast*entry.base),'reduced effects retained cosmetic pose')
  end end
 end
 animation:Step(cast,'Defeated',106,.033,false,105)
 for _,entries in pairs(animation.groups)do for _,entry in ipairs(entries)do check(same(entry.part.CFrame,cast*entry.base),'defeated still animated')end end
 animation:Destroy();check(not animation:Step(target,'Moving',107,.033,false),'destroyed motion resurrected')
 check(#created==initialCount,'final count changed');m:Destroy()
 -- Stream back in halfway through the SAME windup: comfort remains quiet,
 -- then restoring full motion joins the shared timestamp, not frame zero.
 created={};local rejoined=model(center)
 Appearance.Build(rejoined,id,center,function()return true end,function()end,1.4)
 local resumed=Motion.new(rejoined,id,center,1.4)
 resumed:Step(cast,'Windup',104,.033,true,103)
 for _,entries in pairs(resumed.groups)do for _,entry in ipairs(entries)do check(same(entry.part.CFrame,cast*entry.base),'stream-in ignored reduced setting')end end
 resumed:Step(cast,'Windup',104,.033,false,103)
 for i,p in ipairs(created)do check(same(p.CFrame,castFrames[i]),'stream-in restarted windup')end
 resumed:Destroy();rejoined:Destroy()
 print(id..': '..initialCount..' parts, '..grouped..' posed parts, root grounded')
end
-- Execute actual controller with in-flight builds while Core position changes.
local builds,prepares,disposals,steps=0,0,0,0
local queue={};local models={}
local ctl=Controller.new({create=function()local m={Parent=true,Destroy=function(self)self.Parent=nil end};table.insert(models,m);return m end,
 spawn=function(fn)table.insert(queue,fn)end,pause=function()end,
 build=function(_,_,_,alive)builds+=1;check(alive(),'build unexpectedly canceled');return true end,
 prepare=function()prepares+=1;return {Destroy=function()disposals+=1 end}end,
 animate=function(current)steps+=1;check(current.candidate.center.X==3,'latest movement lost');return true end})
local source={Parent=true};local home=v(0,0,0)
local function candidate(x)return {id='metronome',source=source,center=v(x,0,0),home=home,scale=1.4}end
ctl:Step(v(0,0,0),{candidate(0)})
for i=1,100 do ctl:Step(v(0,0,0),{candidate(3)})end
check(#models==1 and #queue==1,'movement rebuilt pending appearance')
ctl:Animate(10,.03,false);check(steps==0,'animated unfinished appearance')
queue[1]();check(builds==1 and prepares==1,'model built more than once')
for i=1,100 do ctl:Step(v(0,0,0),{candidate(3)});ctl:Animate(10,.03,false)end
check(#models==1 and steps==100,'moving appearance churn')
-- Home, not roaming Core, owns LOD admission.
ctl:Step(v(179,0,0),{candidate(-4)});check(#models==1 and ctl.current~=nil,'LOD follows moving core instead of home')
source.Parent=nil;ctl:Animate(11,.03,false)
check(ctl.current==nil and not models[1].Parent and disposals==1,'stream-out leaked animation/model')
ctl:Destroy();ctl:Animate(12,.03,false);check(steps==100,'destroyed animator updated')
print('PASS '..checks..' actual motion/controller assertions; numeric CFrame doubles, not native Studio')
'''
client=(R/'src/StarterPlayer/StarterPlayerScripts/BossVisuals.client.luau').read_text()
comfort=client[client.index('local function comfort()'):client.index('controller=Controller.new')]
state_client=(R/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
state_line=next(line for line in state_client.splitlines() if 'p:SetAttribute("BossReducedEffects"' in line)
checks+="""
local saved=nil;local p={SetAttribute=function(_,key,value)check(key=='BossReducedEffects','unexpected setting key');saved=value end}
local Players={LocalPlayer={GetAttribute=function(_,key)check(key=='BossReducedEffects','unexpected read key');return saved end}}
local Gui={ReducedMotionEnabled=false}
"""+comfort+"""
check(comfort(),'unknown initial setting must be quiet')
for _,value in ipairs({false,true})do
 local data={settings={reducedShake=value}}
"""+state_line+"""
 check(comfort()==value,'persisted setting not followed')
end
saved=false;Gui.ReducedMotionEnabled=true;check(comfort(),'OS reduced ignored')
Gui=setmetatable({},{__index=function()error('unavailable')end});check(comfort(),'OS failure not quiet')
print('PASS persisted game/OS comfort handoff')
"""
def run(m=motion,c=controller,expected=None):
 code=pre+'\nlocal Data=(function()\n'+data+'\nend)()\nlocal Appearance=(function()\nlocal Appearance='+render+'\nend)()\nlocal Motion=(function()\n'+m+'\nend)()\nlocal Controller=(function()\n'+c+'\nend)()\n'+checks
 with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=R/'tests',delete=False)as f:f.write(code);p=Path(f.name)
 try:result=subprocess.run(['luau',str(p)],capture_output=True,text=True)
 finally:p.unlink()
 out=result.stdout+result.stderr
 if expected:assert result.returncode and expected in out,out;print('PASS control:',expected)
 else:assert result.returncode==0,out;print(out.strip())
run()
run(c=controller.replace('self.current.id==chosen.id then','self.current.id==chosen.id and self.current.center==chosen.center then'),expected='movement rebuilt pending appearance')
run(m=motion.replace('if reduced or state=="Defeated" then','if state=="Defeated" then'),expected='reduced effects retained cosmetic pose')
run(m=motion.replace('math.max(0,wave*sign)*.13','wave*sign*.13'),expected='walking foot sank')
run(c=controller.replace('(candidate.home or candidate.center)','candidate.center'),expected='LOD follows moving core')
